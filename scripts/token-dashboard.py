#!/usr/bin/env python3
"""Token consumption & context usage dashboard for Claude Code sessions.

Parses conversation transcripts, extracts real API token usage from assistant
turns, estimates user turn tokens, and generates an interactive HTML dashboard.

Usage:
    python scripts/token-dashboard.py                      # all sessions
    python scripts/token-dashboard.py --project SCUE       # filter by project
    python scripts/token-dashboard.py --last 20            # most recent N
    python scripts/token-dashboard.py --context-size 1000000  # 1M context
    python scripts/token-dashboard.py --output /tmp/d.html # custom output
"""

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / ".agent" / "reports" / "token-dashboard.html"
DEFAULT_CONTEXT_SIZE = 200_000

# Claude Code project slug mapping (same as index-conversations.py)
CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
PROJECT_SLUGS = {
    "-Users-brach-Documents-THE-FACTORY": "THE_FACTORY",
    "-Users-brach-Documents-THE-FACTORY-projects-DjTools-scue": "SCUE",
    "-Users-brach-Documents-THE-FACTORY-projects-CRUCIBLE": "CRUCIBLE",
    "-Users-brach-Documents-THE-FACTORY-projects-tinyshop": "Tinyshop",
    "-Users-brach-Documents-THE-FACTORY-projects-enable": "enable",
}
LOCAL_CONVOS = ROOT / ".agent" / "conversations"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Turn:
    index: int
    timestamp: str
    role: str  # "user" | "assistant"
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    total_context: int = 0  # full context sent to API
    tool_calls: list[str] = field(default_factory=list)
    has_real_usage: bool = False


@dataclass
class SessionMetrics:
    session_id: str
    project: str
    first_timestamp: str = ""
    turns: list[dict] = field(default_factory=list)  # serialized Turn dicts
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cache_read: int = 0
    total_cache_creation: int = 0
    peak_context: int = 0
    peak_context_pct: float = 0.0
    tool_token_map: dict = field(default_factory=dict)  # tool -> estimated tokens
    turn_count: int = 0
    mtime: float = 0.0


# ---------------------------------------------------------------------------
# Transcript discovery (reused from index-conversations.py)
# ---------------------------------------------------------------------------

def find_all_transcripts() -> list[tuple[Path, str]]:
    transcripts: list[tuple[Path, str]] = []
    if CLAUDE_PROJECTS_DIR.exists():
        for slug, project_name in PROJECT_SLUGS.items():
            project_dir = CLAUDE_PROJECTS_DIR / slug
            if project_dir.exists():
                for jsonl in project_dir.glob("*.jsonl"):
                    if jsonl.parent == project_dir:
                        transcripts.append((jsonl, project_name))
    if LOCAL_CONVOS.exists():
        for jsonl in LOCAL_CONVOS.glob("*.jsonl"):
            if jsonl.name == "index.jsonl":
                continue
            transcripts.append((jsonl, "unknown"))
    return transcripts


# ---------------------------------------------------------------------------
# Transcript parsing
# ---------------------------------------------------------------------------

def estimate_content_tokens(content) -> int:
    """Estimate tokens from message content (user turns without usage)."""
    if isinstance(content, str):
        return max(1, len(content) // 4)
    if isinstance(content, list):
        total_chars = 0
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    total_chars += len(block.get("text", ""))
                elif block.get("type") == "tool_result":
                    # tool_result content can be string or list
                    tr_content = block.get("content", "")
                    if isinstance(tr_content, str):
                        total_chars += len(tr_content)
                    elif isinstance(tr_content, list):
                        for sub in tr_content:
                            if isinstance(sub, dict):
                                total_chars += len(sub.get("text", ""))
            elif isinstance(block, str):
                total_chars += len(block)
        return max(1, total_chars // 4)
    return 1


def extract_tool_names(content) -> list[str]:
    """Extract tool names from assistant message content blocks."""
    tools = []
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                tools.append(block.get("name", "unknown"))
    return tools


def parse_transcript(path: Path, context_size: int) -> list[Turn]:
    """Parse a JSONL transcript into deduplicated Turn objects."""
    try:
        text = path.read_text()
    except (PermissionError, OSError):
        return []

    # First pass: collect all entries, group assistant by requestId
    entries = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg_type = entry.get("type", "")
        if msg_type in ("user", "assistant"):
            entries.append(entry)

    # Deduplicate assistant turns: group by requestId, keep last (highest output_tokens)
    assistant_by_request: dict[str, dict] = {}
    user_entries = []
    assistant_no_rid = []

    for entry in entries:
        if entry.get("type") == "user":
            user_entries.append(entry)
        elif entry.get("type") == "assistant":
            rid = entry.get("requestId", "")
            if rid:
                # Keep last entry per requestId (streaming: last has final counts)
                existing = assistant_by_request.get(rid)
                if existing is None:
                    assistant_by_request[rid] = entry
                else:
                    # Merge: keep the one with more content types, always update usage
                    new_usage = entry.get("message", {}).get("usage", {})
                    old_usage = existing.get("message", {}).get("usage", {})
                    new_out = new_usage.get("output_tokens", 0)
                    old_out = old_usage.get("output_tokens", 0)
                    if new_out >= old_out:
                        # Merge tool_calls from both
                        old_tools = existing.get("tool_calls", [])
                        new_tools = entry.get("tool_calls", [])
                        # Merge content blocks (different chunks have different blocks)
                        old_content = existing.get("message", {}).get("content", [])
                        new_content = entry.get("message", {}).get("content", [])
                        merged_content = []
                        seen_ids = set()
                        for c_list in [old_content, new_content]:
                            if isinstance(c_list, list):
                                for block in c_list:
                                    bid = id(block)
                                    if isinstance(block, dict):
                                        bid = block.get("id", id(block))
                                    if bid not in seen_ids:
                                        seen_ids.add(bid)
                                        merged_content.append(block)
                        entry.setdefault("message", {})["content"] = merged_content
                        entry["tool_calls"] = old_tools + new_tools
                        assistant_by_request[rid] = entry
                    else:
                        # Old had higher output — just merge tool_calls into old
                        old_tools = existing.get("tool_calls", [])
                        new_tools = entry.get("tool_calls", [])
                        existing["tool_calls"] = old_tools + new_tools
            else:
                assistant_no_rid.append(entry)

    # Reconstruct timeline: interleave user and deduped assistant by timestamp
    deduped_assistants = list(assistant_by_request.values()) + assistant_no_rid
    all_deduped = user_entries + deduped_assistants
    all_deduped.sort(key=lambda e: e.get("timestamp", ""))

    turns = []
    for i, entry in enumerate(all_deduped):
        msg = entry.get("message", {})
        msg_type = entry.get("type", "")

        if msg_type == "user":
            content = msg.get("content", entry.get("text", ""))
            est_tokens = estimate_content_tokens(content)
            turn = Turn(
                index=i,
                timestamp=entry.get("timestamp", ""),
                role="user",
                input_tokens=est_tokens,
                output_tokens=0,
                has_real_usage=False,
            )
            turns.append(turn)

        elif msg_type == "assistant":
            usage = msg.get("usage", {})
            has_usage = bool(usage and "output_tokens" in usage)

            input_tok = usage.get("input_tokens", 0)
            output_tok = usage.get("output_tokens", 0)
            cache_read = usage.get("cache_read_input_tokens", 0)
            cache_create = usage.get("cache_creation_input_tokens", 0)
            total_ctx = input_tok + cache_read + cache_create

            # Extract tool names from content blocks and tool_calls field
            content = msg.get("content", [])
            tools_from_content = extract_tool_names(content)
            tools_from_field = [
                tc.get("tool", tc.get("name", "unknown"))
                for tc in entry.get("tool_calls", [])
            ]
            # Deduplicate tool names for this turn
            all_tools = list(dict.fromkeys(tools_from_content + tools_from_field))

            turn = Turn(
                index=i,
                timestamp=entry.get("timestamp", ""),
                role="assistant",
                input_tokens=input_tok,
                output_tokens=output_tok,
                cache_read_tokens=cache_read,
                cache_creation_tokens=cache_create,
                total_context=total_ctx,
                tool_calls=all_tools,
                has_real_usage=has_usage,
            )
            turns.append(turn)

    return turns


# ---------------------------------------------------------------------------
# Session metrics
# ---------------------------------------------------------------------------

def compute_session_metrics(
    session_id: str,
    project: str,
    turns: list[Turn],
    context_size: int,
    mtime: float,
) -> SessionMetrics:
    total_in = 0
    total_out = 0
    total_cache_read = 0
    total_cache_create = 0
    peak_ctx = 0
    tool_token_map: dict[str, int] = {}

    turn_dicts = []
    for t in turns:
        total_in += t.input_tokens
        total_out += t.output_tokens
        total_cache_read += t.cache_read_tokens
        total_cache_create += t.cache_creation_tokens
        if t.total_context > peak_ctx:
            peak_ctx = t.total_context

        # Attribute output tokens to tools proportionally
        if t.tool_calls and t.output_tokens > 0:
            per_tool = t.output_tokens // max(len(t.tool_calls), 1)
            for tool_name in t.tool_calls:
                tool_token_map[tool_name] = tool_token_map.get(tool_name, 0) + per_tool

        turn_dicts.append({
            "index": t.index,
            "timestamp": t.timestamp,
            "role": t.role,
            "input_tokens": t.input_tokens,
            "output_tokens": t.output_tokens,
            "cache_read_tokens": t.cache_read_tokens,
            "cache_creation_tokens": t.cache_creation_tokens,
            "total_context": t.total_context,
            "tool_calls": t.tool_calls,
        })

    first_ts = turns[0].timestamp if turns else ""

    return SessionMetrics(
        session_id=session_id,
        project=project,
        first_timestamp=first_ts,
        turns=turn_dicts,
        total_input_tokens=total_in,
        total_output_tokens=total_out,
        total_cache_read=total_cache_read,
        total_cache_creation=total_cache_create,
        peak_context=peak_ctx,
        peak_context_pct=round((peak_ctx / context_size) * 100, 1) if context_size else 0,
        tool_token_map=tool_token_map,
        turn_count=len(turns),
        mtime=mtime,
    )


def aggregate_by_project(sessions: list[SessionMetrics]) -> dict:
    projects: dict[str, dict] = {}
    for s in sessions:
        p = s.project
        if p not in projects:
            projects[p] = {
                "project": p,
                "session_count": 0,
                "total_input": 0,
                "total_output": 0,
                "total_cache_read": 0,
                "total_cache_creation": 0,
                "avg_peak_context_pct": 0.0,
                "peak_pcts": [],
                "avg_turns": 0.0,
                "turn_counts": [],
                "tool_tokens": {},
            }
        proj = projects[p]
        proj["session_count"] += 1
        proj["total_input"] += s.total_input_tokens
        proj["total_output"] += s.total_output_tokens
        proj["total_cache_read"] += s.total_cache_read
        proj["total_cache_creation"] += s.total_cache_creation
        proj["peak_pcts"].append(s.peak_context_pct)
        proj["turn_counts"].append(s.turn_count)
        for tool, tokens in s.tool_token_map.items():
            proj["tool_tokens"][tool] = proj["tool_tokens"].get(tool, 0) + tokens

    # Compute averages
    for proj in projects.values():
        pcts = proj.pop("peak_pcts")
        proj["avg_peak_context_pct"] = round(sum(pcts) / len(pcts), 1) if pcts else 0
        tc = proj.pop("turn_counts")
        proj["avg_turns"] = round(sum(tc) / len(tc), 1) if tc else 0

    return projects


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

def render_html(
    sessions: list[SessionMetrics],
    project_agg: dict,
    context_size: int,
) -> str:
    # Prepare session data for JSON embedding (turns are already dicts)
    sessions_json = []
    for s in sessions:
        sessions_json.append({
            "session_id": s.session_id,
            "project": s.project,
            "first_timestamp": s.first_timestamp,
            "total_input_tokens": s.total_input_tokens,
            "total_output_tokens": s.total_output_tokens,
            "total_cache_read": s.total_cache_read,
            "total_cache_creation": s.total_cache_creation,
            "peak_context": s.peak_context,
            "peak_context_pct": s.peak_context_pct,
            "tool_token_map": s.tool_token_map,
            "turn_count": s.turn_count,
            "mtime": s.mtime,
            "turns": s.turns,
        })

    data_blob = json.dumps({
        "sessions": sessions_json,
        "projects": project_agg,
        "context_size": context_size,
    }, separators=(",", ":"))

    return HTML_TEMPLATE.replace("__DATA_BLOB__", data_blob)


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Token Dashboard — THE_FACTORY</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
:root {
  --bg: #0f0f1a;
  --card: #16213e;
  --card-border: #1a2744;
  --accent: #e94560;
  --accent2: #0f3460;
  --text: #e0e0e0;
  --text-dim: #8892a4;
  --green: #4ade80;
  --orange: #fb923c;
  --chip-bg: #1a2744;
  --chip-active: #e94560;
  --blue: #60a5fa;
  --purple: #a78bfa;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, 'SF Mono', 'Fira Code', monospace;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
}
header {
  padding: 20px 32px 12px;
  border-bottom: 1px solid var(--card-border);
  display: flex;
  align-items: center;
  gap: 16px;
}
header h1 { font-size: 18px; font-weight: 600; }
header .stats {
  font-size: 13px;
  color: var(--text-dim);
  margin-left: auto;
}
nav {
  display: flex;
  gap: 0;
  padding: 0 32px;
  border-bottom: 1px solid var(--card-border);
}
nav button {
  background: none;
  border: none;
  color: var(--text-dim);
  padding: 12px 20px;
  cursor: pointer;
  font-size: 13px;
  font-family: inherit;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}
nav button:hover { color: var(--text); }
nav button.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}
.tab-content { display: none; padding: 24px 32px; }
.tab-content.active { display: block; }
.controls {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
select, input {
  background: var(--card);
  border: 1px solid var(--card-border);
  color: var(--text);
  padding: 8px 12px;
  border-radius: 6px;
  font-family: inherit;
  font-size: 13px;
}
select:focus, input:focus { outline: 1px solid var(--accent); }
.chart-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.chart-card {
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 10px;
  padding: 16px;
  overflow: hidden;
}
.chart-wrap { position: relative; height: 280px; }
.chart-card.full-width { grid-column: 1 / -1; }
.chart-card.full-width .chart-wrap { height: 320px; }
.chart-card h3 {
  font-size: 13px;
  color: var(--text-dim);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}
.summary-card {
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 10px;
  padding: 16px;
}
.summary-card .label {
  font-size: 11px;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.summary-card .value {
  font-size: 24px;
  font-weight: 700;
  margin-top: 4px;
}
.summary-card .value.accent { color: var(--accent); }
.summary-card .value.green { color: var(--green); }
.summary-card .value.blue { color: var(--blue); }
.summary-card .value.orange { color: var(--orange); }
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
th, td {
  text-align: left;
  padding: 10px 12px;
  border-bottom: 1px solid var(--card-border);
}
th { color: var(--text-dim); font-weight: 500; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; }
td { color: var(--text); }
.compare-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}
.compare-chip {
  background: var(--accent2);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 4px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.compare-chip:hover, .compare-chip.selected {
  background: var(--accent);
  color: white;
}
.session-toggles {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}
.session-toggle {
  background: var(--chip-bg);
  border: 1px solid var(--card-border);
  color: var(--text-dim);
  padding: 5px 14px;
  border-radius: 14px;
  font-size: 12px;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}
.session-toggle:hover { color: var(--text); border-color: var(--text-dim); }
.session-toggle.active {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}
.session-panel {
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 10px;
  margin-bottom: 16px;
  padding: 16px;
}
.panel-header {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
.panel-header .sid { font-weight: 600; color: var(--accent); font-size: 14px; }
.panel-header .stat { font-size: 12px; color: var(--text-dim); }
.panel-header .stat b { color: var(--text); font-weight: 600; }
.panel-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.panel-charts .chart-wrap { height: 200px; }
.panel-expand-btn {
  background: none;
  border: 1px solid var(--card-border);
  color: var(--text-dim);
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 11px;
  font-family: inherit;
  cursor: pointer;
  margin-left: auto;
}
.panel-expand-btn:hover { color: var(--text); border-color: var(--text-dim); }
.panel-extra {
  display: none;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 16px;
}
.panel-extra.open { display: grid; }
.panel-extra .chart-wrap { height: 200px; }
.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 32px;
  border-bottom: 1px solid var(--card-border);
  flex-wrap: wrap;
}
.filter-bar label {
  font-size: 11px;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.filter-chips { display: flex; gap: 6px; }
.filter-chips button {
  background: var(--chip-bg);
  border: 1px solid var(--card-border);
  color: var(--text-dim);
  padding: 5px 14px;
  border-radius: 14px;
  font-size: 12px;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}
.filter-chips button:hover { color: var(--text); border-color: var(--text-dim); }
.filter-chips button.active {
  background: var(--chip-active);
  border-color: var(--chip-active);
  color: white;
}
@media (max-width: 900px) {
  .chart-grid { grid-template-columns: 1fr; }
  header { flex-wrap: wrap; }
  .filter-bar { padding: 12px 16px; }
}
</style>
</head>
<body>

<header>
  <h1>Token Dashboard</h1>
  <span class="stats" id="header-stats"></span>
</header>

<nav>
  <button class="active" data-tab="session">Monitor</button>
  <button data-tab="compare">Compare</button>
  <button data-tab="projects">Projects</button>
</nav>

<div class="filter-bar">
  <label>Show:</label>
  <div class="filter-chips" id="recency-chips">
    <button class="active" data-filter="last10">Last 10</button>
    <button data-filter="24h">Last 24h</button>
    <button data-filter="7d">Last 7d</button>
    <button data-filter="30d">Last 30d</button>
    <button data-filter="all">All</button>
  </div>
  <select id="project-filter">
    <option value="">All Projects</option>
  </select>
</div>

<!-- MONITOR TAB -->
<div class="tab-content active" id="tab-session">
  <div class="controls">
    <span style="color:var(--text-dim);font-size:13px">Toggle sessions to monitor:</span>
  </div>
  <div class="session-toggles" id="session-toggles"></div>
  <div id="session-panels"></div>
</div>

<!-- COMPARE TAB -->
<div class="tab-content" id="tab-compare">
  <div class="controls">
    <span style="color:var(--text-dim);font-size:13px">Click sessions to compare (max 5):</span>
  </div>
  <div class="compare-list" id="compare-chips"></div>
  <div class="chart-grid">
    <div class="chart-card full-width">
      <h3>Burn Rate Comparison</h3>
      <div class="chart-wrap"><canvas id="chart-compare-burn"></canvas></div>
    </div>
    <div class="chart-card full-width">
      <h3>Context Fill Comparison</h3>
      <div class="chart-wrap"><canvas id="chart-compare-context"></canvas></div>
    </div>
  </div>
</div>

<!-- PROJECTS TAB -->
<div class="tab-content" id="tab-projects">
  <div class="summary-cards" id="project-summary"></div>
  <div class="chart-grid">
    <div class="chart-card">
      <h3>Total Tokens by Project</h3>
      <div class="chart-wrap"><canvas id="chart-project-tokens"></canvas></div>
    </div>
    <div class="chart-card">
      <h3>Avg Peak Context % by Project</h3>
      <div class="chart-wrap"><canvas id="chart-project-context"></canvas></div>
    </div>
    <div class="chart-card full-width">
      <h3>Session Details</h3>
      <div style="overflow-x:auto">
        <table id="project-table">
          <thead><tr>
            <th>Project</th><th>Sessions</th><th>Avg Turns</th>
            <th>Total Input</th><th>Total Output</th>
            <th>Avg Peak Ctx %</th>
          </tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<script>
const RAW = __DATA_BLOB__;
const DATA = RAW.sessions;
const CTX_SIZE = RAW.context_size;

// ---------- Helpers ----------
function fmt(n) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1) + "K";
  return n.toString();
}
function shortId(sid) { return sid.slice(0, 8); }
function sessionLabel(s) {
  const date = s.first_timestamp ? new Date(s.first_timestamp).toLocaleDateString() : "?";
  return `${shortId(s.session_id)} — ${s.project} — ${date} — ${s.turn_count} turns`;
}

const COLORS = [
  "#e94560", "#60a5fa", "#4ade80", "#fb923c", "#a78bfa",
  "#f472b6", "#34d399", "#fbbf24", "#818cf8", "#fb7185",
];

Chart.defaults.color = "#8892a4";
Chart.defaults.borderColor = "#1a2744";
Chart.defaults.plugins.legend.labels.boxWidth = 12;

// ---------- Tab switching ----------
document.querySelectorAll("nav button").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("nav button").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
  });
});

// ---------- Filter state ----------
let currentRecency = "last10";
let currentProject = "";
let filtered = []; // array of {_idx, ...session}

// Populate project filter dropdown
const projectFilter = document.getElementById("project-filter");
const allProjects = [...new Set(DATA.map(s => s.project))].sort();
allProjects.forEach(p => {
  const opt = document.createElement("option");
  opt.value = p;
  opt.textContent = p;
  projectFilter.appendChild(opt);
});

function getFilteredSessions() {
  const now = Date.now() / 1000;
  let result = DATA.map((s, i) => ({...s, _idx: i}));

  // Project filter
  if (currentProject) result = result.filter(s => s.project === currentProject);

  // Sort by mtime descending (most recent first)
  result.sort((a, b) => (b.mtime || 0) - (a.mtime || 0));

  // Recency filter
  if (currentRecency === "last10") result = result.slice(0, 10);
  else if (currentRecency === "24h") result = result.filter(s => s.mtime && now - s.mtime < 86400);
  else if (currentRecency === "7d") result = result.filter(s => s.mtime && now - s.mtime < 604800);
  else if (currentRecency === "30d") result = result.filter(s => s.mtime && now - s.mtime < 2592000);
  // "all" — no further filtering

  return result;
}

// ---------- Filter UI wiring ----------
document.querySelectorAll("#recency-chips button").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("#recency-chips button").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentRecency = btn.dataset.filter;
    applyFilters();
  });
});

projectFilter.addEventListener("change", () => {
  currentProject = projectFilter.value;
  applyFilters();
});

// ---------- Chart helpers ----------
let compareBurnChart, compareContextChart;
let projectTokenChart, projectContextChart;

function destroyChart(c) { if (c) c.destroy(); return null; }

// ---------- Monitor (multi-session panels) ----------
const activeSessionIds = new Set();
const panelCharts = new Map(); // sessionId -> {burn, context, perTurn, tools}

function rebuildToggles() {
  const container = document.getElementById("session-toggles");
  container.innerHTML = "";
  filtered.forEach(s => {
    const btn = document.createElement("button");
    btn.className = "session-toggle" + (activeSessionIds.has(s.session_id) ? " active" : "");
    const date = s.first_timestamp ? new Date(s.first_timestamp).toLocaleDateString() : "?";
    btn.textContent = `${shortId(s.session_id)} (${s.project}, ${date})`;
    btn.addEventListener("click", () => {
      if (activeSessionIds.has(s.session_id)) activeSessionIds.delete(s.session_id);
      else activeSessionIds.add(s.session_id);
      rebuildToggles();
      renderPanels();
    });
    container.appendChild(btn);
  });
}

function renderPanels() {
  const container = document.getElementById("session-panels");
  // Destroy charts for sessions no longer active
  for (const [sid, charts] of panelCharts) {
    if (!activeSessionIds.has(sid)) {
      if (charts.burn) charts.burn.destroy();
      if (charts.context) charts.context.destroy();
      if (charts.perTurn) charts.perTurn.destroy();
      if (charts.tools) charts.tools.destroy();
      panelCharts.delete(sid);
    }
  }
  container.innerHTML = "";

  const activeSessions = filtered.filter(s => activeSessionIds.has(s.session_id));
  if (!activeSessions.length) {
    container.innerHTML = '<div style="color:var(--text-dim);padding:40px 0;text-align:center">Select sessions above to monitor</div>';
    return;
  }

  activeSessions.forEach(s => {
    const panel = document.createElement("div");
    panel.className = "session-panel";
    const date = s.first_timestamp ? new Date(s.first_timestamp).toLocaleDateString() : "?";
    const sid = s.session_id;
    panel.innerHTML = `
      <div class="panel-header">
        <span class="sid">${shortId(sid)}</span>
        <span class="stat"><b>${s.project}</b></span>
        <span class="stat">${date}</span>
        <span class="stat">In: <b>${fmt(s.total_input_tokens)}</b></span>
        <span class="stat">Out: <b>${fmt(s.total_output_tokens)}</b></span>
        <span class="stat">Cache: <b>${fmt(s.total_cache_read)}</b></span>
        <span class="stat">Peak: <b style="color:var(--accent)">${s.peak_context_pct}%</b></span>
        <span class="stat">Turns: <b>${s.turn_count}</b></span>
        <button class="panel-expand-btn" data-sid="${sid}">+ Details</button>
      </div>
      <div class="panel-charts">
        <div class="chart-wrap"><canvas id="burn-${sid}"></canvas></div>
        <div class="chart-wrap"><canvas id="ctx-${sid}"></canvas></div>
      </div>
      <div class="panel-extra" id="extra-${sid}">
        <div class="chart-wrap"><canvas id="perturn-${sid}"></canvas></div>
        <div class="chart-wrap"><canvas id="tools-${sid}"></canvas></div>
      </div>
    `;
    container.appendChild(panel);

    // Expand/collapse
    panel.querySelector(".panel-expand-btn").addEventListener("click", (e) => {
      const extra = document.getElementById("extra-" + sid);
      const btn = e.currentTarget;
      if (extra.classList.contains("open")) {
        extra.classList.remove("open");
        btn.textContent = "+ Details";
        // Destroy extra charts
        const ch = panelCharts.get(sid);
        if (ch) {
          if (ch.perTurn) { ch.perTurn.destroy(); ch.perTurn = null; }
          if (ch.tools) { ch.tools.destroy(); ch.tools = null; }
        }
      } else {
        extra.classList.add("open");
        btn.textContent = "- Details";
        renderExtraCharts(s);
      }
    });

    // Render main charts
    renderPanelCharts(s);
  });
}

function renderPanelCharts(s) {
  const sid = s.session_id;
  const turns = s.turns;
  const labels = turns.map((_, i) => i);

  let cumInput = 0, cumOutput = 0;
  const cumInputData = [], cumOutputData = [];
  turns.forEach(t => {
    cumInput += t.input_tokens + t.cache_read_tokens + t.cache_creation_tokens;
    cumOutput += t.output_tokens;
    cumInputData.push(cumInput);
    cumOutputData.push(cumOutput);
  });

  const burnEl = document.getElementById("burn-" + sid);
  const ctxEl = document.getElementById("ctx-" + sid);
  if (!burnEl || !ctxEl) return;

  const charts = {
    burn: new Chart(burnEl, {
      type: "line",
      data: {
        labels,
        datasets: [
          { label: "Input", data: cumInputData, borderColor: "#60a5fa", borderWidth: 2, fill: false, pointRadius: 0 },
          { label: "Output", data: cumOutputData, borderColor: "#fb923c", borderWidth: 2, fill: false, pointRadius: 0 },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: {
          x: { title: { display: true, text: "Turn" } },
          y: { ticks: { callback: v => fmt(v) } },
        },
        plugins: {
          legend: { display: true, position: "top" },
          tooltip: { callbacks: { label: ctx => ctx.dataset.label + ": " + fmt(ctx.raw) } },
        },
      },
    }),
    context: new Chart(ctxEl, {
      type: "line",
      data: {
        labels,
        datasets: [{
          label: "Context %", borderColor: "#e94560", backgroundColor: "rgba(233, 69, 96, 0.15)",
          data: turns.map(t => t.role === "assistant" && t.total_context ? (t.total_context / CTX_SIZE * 100) : null),
          borderWidth: 2, fill: true, pointRadius: 0, spanGaps: true,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: {
          x: { title: { display: true, text: "Turn" } },
          y: { min: 0, suggestedMax: 100 },
        },
      },
    }),
    perTurn: null,
    tools: null,
  };
  panelCharts.set(sid, charts);
}

function renderExtraCharts(s) {
  const sid = s.session_id;
  const turns = s.turns;
  const labels = turns.map((_, i) => i);
  const charts = panelCharts.get(sid);
  if (!charts) return;

  const ptEl = document.getElementById("perturn-" + sid);
  const tlEl = document.getElementById("tools-" + sid);
  if (!ptEl || !tlEl) return;

  charts.perTurn = new Chart(ptEl, {
    type: "bar",
    data: {
      labels,
      datasets: [
        { label: "User (est.)", data: turns.map(t => t.role === "user" ? t.input_tokens : 0), backgroundColor: "rgba(96, 165, 250, 0.7)" },
        { label: "Assistant", data: turns.map(t => t.role === "assistant" ? t.output_tokens : 0), backgroundColor: "rgba(251, 146, 60, 0.7)" },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: { x: { stacked: true }, y: { stacked: true, ticks: { callback: v => fmt(v) } } },
    },
  });

  const toolMap = s.tool_token_map;
  const toolNames = Object.keys(toolMap).sort((a, b) => toolMap[b] - toolMap[a]).slice(0, 10);
  const toolValues = toolNames.map(n => toolMap[n]);
  charts.tools = new Chart(tlEl, {
    type: "bar",
    data: {
      labels: toolNames,
      datasets: [{ label: "Tokens", data: toolValues, backgroundColor: toolNames.map((_, i) => COLORS[i % COLORS.length]) }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      indexAxis: "y",
      scales: { x: { ticks: { callback: v => fmt(v) } } },
    },
  });
}

// ---------- Compare tab ----------
const compareState = new Set(); // stores session_id strings for stability across filter changes

function renderCompareChips() {
  const container = document.getElementById("compare-chips");
  container.innerHTML = "";
  filtered.forEach(s => {
    const chip = document.createElement("span");
    chip.className = "compare-chip" + (compareState.has(s.session_id) ? " selected" : "");
    const date = s.first_timestamp ? new Date(s.first_timestamp).toLocaleDateString() : "?";
    chip.textContent = `${shortId(s.session_id)} (${s.project}, ${date})`;
    chip.addEventListener("click", () => {
      if (compareState.has(s.session_id)) {
        compareState.delete(s.session_id);
      } else if (compareState.size < 5) {
        compareState.add(s.session_id);
      }
      renderCompareChips();
      renderCompareCharts();
    });
    container.appendChild(chip);
  });
}

function renderCompareCharts() {
  const selected = filtered.filter(s => compareState.has(s.session_id));
  if (!selected.length) {
    destroyChart(compareBurnChart);
    destroyChart(compareContextChart);
    compareBurnChart = null;
    compareContextChart = null;
    return;
  }

  const burnDatasets = selected.map((s, ci) => {
    let cum = 0;
    const data = s.turns.map(t => {
      cum += t.input_tokens + t.cache_read_tokens + t.cache_creation_tokens + t.output_tokens;
      return cum;
    });
    return {
      label: `${shortId(s.session_id)} (${s.project})`,
      data, borderColor: COLORS[ci % COLORS.length], borderWidth: 2, fill: false, pointRadius: 0,
    };
  });

  const maxLen = Math.max(...selected.map(s => s.turns.length));
  const labels = Array.from({ length: maxLen }, (_, i) => i);

  destroyChart(compareBurnChart);
  compareBurnChart = new Chart(document.getElementById("chart-compare-burn"), {
    type: "line",
    data: { labels, datasets: burnDatasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        x: { title: { display: true, text: "Turn" } },
        y: { title: { display: true, text: "Cumulative Tokens" }, ticks: { callback: v => fmt(v) } },
      },
    },
  });

  const ctxDatasets = selected.map((s, ci) => ({
    label: `${shortId(s.session_id)} (${s.project})`,
    data: s.turns.map(t => t.role === "assistant" && t.total_context ? (t.total_context / CTX_SIZE * 100) : null),
    borderColor: COLORS[ci % COLORS.length], borderWidth: 2, fill: false, pointRadius: 0, spanGaps: true,
  }));

  destroyChart(compareContextChart);
  compareContextChart = new Chart(document.getElementById("chart-compare-context"), {
    type: "line",
    data: { labels, datasets: ctxDatasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        x: { title: { display: true, text: "Turn" } },
        y: { title: { display: true, text: "Context %" }, min: 0, suggestedMax: 100 },
      },
    },
  });
}

// ---------- Projects tab (client-side aggregation) ----------
function renderProjects() {
  // Aggregate from filtered sessions
  const projects = {};
  filtered.forEach(s => {
    const p = s.project;
    if (!projects[p]) projects[p] = { session_count: 0, total_input: 0, total_output: 0, peak_pcts: [], turn_counts: [] };
    projects[p].session_count++;
    projects[p].total_input += s.total_input_tokens;
    projects[p].total_output += s.total_output_tokens;
    projects[p].peak_pcts.push(s.peak_context_pct);
    projects[p].turn_counts.push(s.turn_count);
  });
  // Compute averages
  for (const p of Object.values(projects)) {
    p.avg_peak_context_pct = p.peak_pcts.length ? +(p.peak_pcts.reduce((a,b) => a+b, 0) / p.peak_pcts.length).toFixed(1) : 0;
    p.avg_turns = p.turn_counts.length ? +(p.turn_counts.reduce((a,b) => a+b, 0) / p.turn_counts.length).toFixed(1) : 0;
  }

  const projKeys = Object.keys(projects).sort();

  const sumEl = document.getElementById("project-summary");
  const totalIn = projKeys.reduce((s, k) => s + projects[k].total_input, 0);
  const totalOut = projKeys.reduce((s, k) => s + projects[k].total_output, 0);
  const totalSessions = projKeys.reduce((s, k) => s + projects[k].session_count, 0);
  sumEl.innerHTML = `
    <div class="summary-card"><div class="label">Projects</div><div class="value">${projKeys.length}</div></div>
    <div class="summary-card"><div class="label">Total Sessions</div><div class="value blue">${totalSessions}</div></div>
    <div class="summary-card"><div class="label">Total Input</div><div class="value orange">${fmt(totalIn)}</div></div>
    <div class="summary-card"><div class="label">Total Output</div><div class="value green">${fmt(totalOut)}</div></div>
  `;

  destroyChart(projectTokenChart);
  projectTokenChart = new Chart(document.getElementById("chart-project-tokens"), {
    type: "bar",
    data: {
      labels: projKeys,
      datasets: [{ label: "Total Tokens", data: projKeys.map(k => projects[k].total_input + projects[k].total_output), backgroundColor: projKeys.map((_, i) => COLORS[i % COLORS.length]) }],
    },
    options: { responsive: true, maintainAspectRatio: false, scales: { y: { ticks: { callback: v => fmt(v) } } }, plugins: { legend: { display: false } } },
  });

  destroyChart(projectContextChart);
  projectContextChart = new Chart(document.getElementById("chart-project-context"), {
    type: "bar",
    data: {
      labels: projKeys,
      datasets: [{ label: "Avg Peak Context %", data: projKeys.map(k => projects[k].avg_peak_context_pct), backgroundColor: projKeys.map((_, i) => COLORS[i % COLORS.length] + "99") }],
    },
    options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: 0, suggestedMax: 100 } }, plugins: { legend: { display: false } } },
  });

  const tbody = document.querySelector("#project-table tbody");
  tbody.innerHTML = "";
  projKeys.forEach(k => {
    const p = projects[k];
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${k}</td><td>${p.session_count}</td><td>${p.avg_turns}</td><td>${fmt(p.total_input)}</td><td>${fmt(p.total_output)}</td><td>${p.avg_peak_context_pct}%</td>`;
    tbody.appendChild(tr);
  });
}

// ---------- Master apply ----------
function applyFilters() {
  filtered = getFilteredSessions();

  // Header stats (for filtered set)
  const totalTok = filtered.reduce((s, d) => s + d.total_input_tokens + d.total_output_tokens, 0);
  document.getElementById("header-stats").textContent =
    `${filtered.length} of ${DATA.length} sessions | ${fmt(totalTok)} tokens | Context: ${fmt(CTX_SIZE)}`;

  // Monitor panels
  // Auto-activate first session if nothing is active
  if (activeSessionIds.size === 0 && filtered.length) activeSessionIds.add(filtered[0].session_id);
  // Remove active sessions that are no longer in filtered set
  const filteredIds = new Set(filtered.map(s => s.session_id));
  for (const sid of activeSessionIds) {
    if (!filteredIds.has(sid)) activeSessionIds.delete(sid);
  }
  rebuildToggles();
  renderPanels();

  // Compare
  renderCompareChips();
  renderCompareCharts();

  // Projects
  renderProjects();
}

// ---------- Init ----------
applyFilters();
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# CLI & main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Token consumption & context usage dashboard"
    )
    parser.add_argument("--project", help="Filter to a specific project")
    parser.add_argument("--last", type=int, help="Only process the N most recent sessions")
    parser.add_argument(
        "--context-size",
        type=int,
        default=DEFAULT_CONTEXT_SIZE,
        help=f"Context window size in tokens (default: {DEFAULT_CONTEXT_SIZE})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output HTML path (default: {DEFAULT_OUTPUT.relative_to(ROOT)})",
    )
    args = parser.parse_args()

    # Discover transcripts
    all_transcripts = find_all_transcripts()
    if not all_transcripts:
        print("No conversation transcripts found.", file=sys.stderr)
        sys.exit(1)

    # Deduplicate by session_id (prefer newer mtime)
    best: dict[str, tuple[Path, str]] = {}
    for path, project in all_transcripts:
        sid = path.stem
        if sid not in best or path.stat().st_mtime > best[sid][0].stat().st_mtime:
            best[sid] = (path, project)

    # Filter by project
    if args.project:
        best = {
            sid: (p, proj)
            for sid, (p, proj) in best.items()
            if proj.lower() == args.project.lower()
        }

    # Sort by mtime descending
    sorted_sessions = sorted(
        best.items(), key=lambda x: x[1][0].stat().st_mtime, reverse=True
    )

    # Apply --last
    if args.last:
        sorted_sessions = sorted_sessions[: args.last]

    if not sorted_sessions:
        print("No sessions match filters.", file=sys.stderr)
        sys.exit(1)

    print(f"Processing {len(sorted_sessions)} sessions...")

    # Parse and compute metrics
    session_metrics: list[SessionMetrics] = []
    for sid, (path, project) in sorted_sessions:
        turns = parse_transcript(path, args.context_size)
        if not turns:
            continue
        metrics = compute_session_metrics(
            sid, project, turns, args.context_size, path.stat().st_mtime
        )
        session_metrics.append(metrics)

    if not session_metrics:
        print("No sessions with parseable data.", file=sys.stderr)
        sys.exit(1)

    print(f"Parsed {len(session_metrics)} sessions with token data")

    # Aggregate by project
    project_agg = aggregate_by_project(session_metrics)

    # Render HTML
    html = render_html(session_metrics, project_agg, args.context_size)

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html)
    print(f"Dashboard written to {args.output}")
    print(f"Open in browser: file://{args.output.resolve()}")


if __name__ == "__main__":
    main()
