#!/usr/bin/env python3
"""
Extract and assemble Claude Code conversation data into analyzable format.

Reads raw JSONL transcripts from ~/.claude/projects/ and produces:
1. A session index with metadata (conversations-index.jsonl)
2. Per-session narrative exports with timestamps, thinking, tool calls (conversations/)
3. A merged timeline across overlapping sessions (timeline.jsonl)

Usage:
    python3 scripts/extract-conversations.py [--project PROJECT_HASH] [--since YYYY-MM-DD] [--output-dir DIR]

Default output: .agent/conversations/
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

CLAUDE_DIR = Path.home() / ".claude"
PROJECTS_DIR = CLAUDE_DIR / "projects"
HISTORY_FILE = CLAUDE_DIR / "history.jsonl"


def parse_args():
    parser = argparse.ArgumentParser(description="Extract Claude Code conversation data")
    parser.add_argument("--project", help="Project hash filter (e.g., -Users-brach-Documents-THE-FACTORY)")
    parser.add_argument("--since", help="Only sessions after this date (YYYY-MM-DD)")
    parser.add_argument("--output-dir", default=".agent/conversations", help="Output directory")
    parser.add_argument("--include-thinking", action="store_true", default=True,
                        help="Include thinking/reasoning blocks (default: true)")
    parser.add_argument("--include-tool-output", action="store_true", default=False,
                        help="Include full tool output (can be very large)")
    parser.add_argument("--include-subagents", action="store_true", default=True,
                        help="Inline subagent conversations (default: true)")
    parser.add_argument("--format", choices=["jsonl", "markdown", "both"], default="both",
                        help="Output format (default: both)")
    return parser.parse_args()


def read_jsonl(path):
    """Read a JSONL file, yielding parsed objects."""
    if not path.exists():
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def load_history_index():
    """Load history.jsonl as a session metadata index."""
    sessions = defaultdict(list)
    for entry in read_jsonl(HISTORY_FILE):
        sid = entry.get("sessionId")
        if sid:
            sessions[sid].append({
                "display": entry.get("display", ""),
                "timestamp": entry.get("timestamp"),
                "project": entry.get("project", ""),
            })
    return sessions


def find_session_files(project_filter=None):
    """Find all session JSONL files, optionally filtered by project."""
    sessions = []
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        if project_filter and project_filter not in project_dir.name:
            continue
        for f in project_dir.iterdir():
            if f.suffix == ".jsonl" and f.stem != "index":
                subagent_dir = project_dir / f.stem / "subagents"
                subagent_files = []
                if subagent_dir.exists():
                    subagent_files = list(subagent_dir.glob("*.jsonl"))
                sessions.append({
                    "project": project_dir.name,
                    "session_id": f.stem,
                    "transcript_path": f,
                    "subagent_dir": subagent_dir if subagent_dir.exists() else None,
                    "subagent_files": subagent_files,
                })
    return sessions


def extract_session(session_info, include_thinking=True, include_tool_output=False,
                    include_subagents=True):
    """Extract structured data from a session transcript."""
    transcript_path = session_info["transcript_path"]
    messages = list(read_jsonl(transcript_path))

    if not messages:
        return None

    # Extract metadata from first message
    first_msg = messages[0]
    timestamps = [m.get("timestamp") for m in messages if m.get("timestamp")]

    # Collect subagent data
    subagents = {}
    if include_subagents and session_info["subagent_files"]:
        for sa_file in session_info["subagent_files"]:
            agent_id = sa_file.stem.replace("agent-", "")
            meta_file = sa_file.with_suffix(".meta.json")
            meta = {}
            if meta_file.exists():
                with open(meta_file) as f:
                    meta = json.load(f)

            sa_messages = list(read_jsonl(sa_file))
            sa_timestamps = [m.get("timestamp") for m in sa_messages if m.get("timestamp")]

            subagents[agent_id] = {
                "agent_type": meta.get("agentType", "unknown"),
                "description": meta.get("description", ""),
                "message_count": len(sa_messages),
                "start": min(sa_timestamps) if sa_timestamps else None,
                "end": max(sa_timestamps) if sa_timestamps else None,
                "messages": sa_messages,
            }

    # Build structured timeline
    timeline = []
    for msg in messages:
        msg_type = msg.get("type")
        timestamp = msg.get("timestamp")

        if msg_type == "user":
            # User messages store text in msg["message"]["content"].
            # content may be a plain string or a list of content blocks.
            # When it's a string, iterating yields individual characters — don't do that.
            message_obj = msg.get("message", {})
            content = message_obj.get("content", "") if isinstance(message_obj, dict) else ""

            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif isinstance(block, dict) and block.get("type") == "tool_result":
                        # Tool results appear as user messages — summarize
                        text_parts.append(f"[tool_result: {block.get('tool_use_id', '')[:20]}]")
                    elif isinstance(block, str):
                        text_parts.append(block)
                text = "\n".join(text_parts) if text_parts else ""
            else:
                text = str(content)

            timeline.append({
                "timestamp": timestamp,
                "type": "user",
                "text": text[:5000],  # Truncate very long pastes
                "uuid": msg.get("uuid"),
            })

        elif msg_type == "assistant":
            content = msg.get("message", {})
            blocks = content.get("content", []) if isinstance(content, dict) else []

            entry = {
                "timestamp": timestamp,
                "type": "assistant",
                "uuid": msg.get("uuid"),
                "text_parts": [],
                "thinking": [],
                "tool_calls": [],
            }

            for block in blocks:
                if not isinstance(block, dict):
                    continue
                btype = block.get("type")
                if btype == "text":
                    entry["text_parts"].append(block.get("text", ""))
                elif btype == "thinking" and include_thinking:
                    entry["thinking"].append(block.get("thinking", ""))
                elif btype == "tool_use":
                    tool_entry = {
                        "tool": block.get("name", ""),
                        "id": block.get("id", ""),
                        "input_summary": summarize_tool_input(block.get("input", {})),
                    }
                    if include_tool_output:
                        tool_entry["input"] = block.get("input", {})
                    entry["tool_calls"].append(tool_entry)
                elif btype == "tool_result":
                    # Link result back to tool call
                    tool_use_id = block.get("tool_use_id", "")
                    result_content = block.get("content", "")
                    if isinstance(result_content, list):
                        result_text = " ".join(
                            b.get("text", "") for b in result_content
                            if isinstance(b, dict) and b.get("type") == "text"
                        )
                    else:
                        result_text = str(result_content)

                    for tc in entry["tool_calls"]:
                        if tc["id"] == tool_use_id:
                            tc["result_summary"] = result_text[:500] if not include_tool_output else result_text
                            break

            timeline.append(entry)

        elif msg_type == "queue-operation":
            timeline.append({
                "timestamp": timestamp,
                "type": "queue",
                "operation": msg.get("operation"),
            })

    # Session summary
    user_count = sum(1 for m in timeline if m.get("type") == "user")
    assistant_count = sum(1 for m in timeline if m.get("type") == "assistant")
    tool_calls = []
    thinking_count = 0
    for m in timeline:
        if m.get("type") == "assistant":
            tool_calls.extend(m.get("tool_calls", []))
            thinking_count += len(m.get("thinking", []))

    tool_freq = defaultdict(int)
    for tc in tool_calls:
        tool_freq[tc["tool"]] += 1

    return {
        "session_id": session_info["session_id"],
        "project": session_info["project"],
        "start": min(timestamps) if timestamps else None,
        "end": max(timestamps) if timestamps else None,
        "git_branch": first_msg.get("gitBranch"),
        "cwd": first_msg.get("cwd"),
        "entrypoint": first_msg.get("entrypoint"),
        "version": first_msg.get("version"),
        "permission_mode": first_msg.get("permissionMode"),
        "user_messages": user_count,
        "assistant_messages": assistant_count,
        "total_tool_calls": len(tool_calls),
        "tool_frequency": dict(tool_freq),
        "thinking_blocks": thinking_count,
        "subagent_count": len(subagents),
        "subagents": {
            aid: {k: v for k, v in sa.items() if k != "messages"}
            for aid, sa in subagents.items()
        },
        "timeline": timeline,
        "subagent_timelines": {
            aid: extract_subagent_timeline(sa, include_thinking, include_tool_output)
            for aid, sa in subagents.items()
        } if include_subagents else {},
    }


def extract_subagent_timeline(subagent_data, include_thinking, include_tool_output):
    """Extract timeline from subagent messages."""
    timeline = []
    for msg in subagent_data.get("messages", []):
        msg_type = msg.get("type")
        timestamp = msg.get("timestamp")
        content = msg.get("message", {})
        blocks = content.get("content", []) if isinstance(content, dict) else []

        entry = {
            "timestamp": timestamp,
            "type": msg_type,
        }

        if msg_type == "assistant":
            for block in blocks:
                if not isinstance(block, dict):
                    continue
                btype = block.get("type")
                if btype == "text":
                    entry.setdefault("text_parts", []).append(block.get("text", ""))
                elif btype == "thinking" and include_thinking:
                    entry.setdefault("thinking", []).append(block.get("thinking", ""))
                elif btype == "tool_use":
                    entry.setdefault("tool_calls", []).append({
                        "tool": block.get("name", ""),
                        "input_summary": summarize_tool_input(block.get("input", {})),
                    })
        elif msg_type == "user":
            if isinstance(content, dict):
                text_parts = []
                for block in blocks:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                entry["text"] = "\n".join(text_parts)[:2000]
            else:
                entry["text"] = str(content)[:2000]

        timeline.append(entry)
    return timeline


def summarize_tool_input(input_data):
    """Create a brief summary of tool input."""
    if not isinstance(input_data, dict):
        return str(input_data)[:200]

    # Common tool input patterns
    if "command" in input_data:
        return f"$ {input_data['command'][:200]}"
    if "file_path" in input_data:
        return f"file: {input_data['file_path']}"
    if "pattern" in input_data:
        return f"pattern: {input_data['pattern']}"
    if "query" in input_data:
        return f"query: {input_data['query'][:200]}"
    if "prompt" in input_data:
        return f"prompt: {input_data['prompt'][:200]}"
    if "url" in input_data:
        return f"url: {input_data['url']}"
    if "old_string" in input_data:
        return f"edit: {input_data.get('file_path', '?')}"
    if "content" in input_data:
        return f"write: {input_data.get('file_path', '?')}"
    if "skill" in input_data:
        return f"skill: {input_data['skill']}"

    # Fallback
    keys = list(input_data.keys())[:5]
    return f"keys: {keys}"


def to_markdown(session_data):
    """Convert extracted session to readable markdown."""
    lines = []
    sd = session_data
    lines.append(f"# Session: {sd['session_id'][:8]}...")
    lines.append(f"")
    lines.append(f"- **Project:** `{sd['project']}`")
    lines.append(f"- **Branch:** `{sd.get('git_branch', 'unknown')}`")
    lines.append(f"- **Start:** {sd['start']}")
    lines.append(f"- **End:** {sd['end']}")
    lines.append(f"- **Messages:** {sd['user_messages']} user / {sd['assistant_messages']} assistant")
    lines.append(f"- **Tool calls:** {sd['total_tool_calls']}")
    lines.append(f"- **Thinking blocks:** {sd['thinking_blocks']}")
    lines.append(f"- **Subagents:** {sd['subagent_count']}")
    if sd.get("tool_frequency"):
        lines.append(f"- **Tool frequency:** {json.dumps(sd['tool_frequency'])}")
    lines.append("")

    if sd.get("subagents"):
        lines.append("## Subagents")
        for aid, sa in sd["subagents"].items():
            lines.append(f"- `{aid[:12]}` — {sa['agent_type']}: {sa['description']} "
                         f"({sa['message_count']} msgs, {sa['start']} → {sa['end']})")
        lines.append("")

    lines.append("## Timeline")
    lines.append("")

    for entry in sd["timeline"]:
        ts = entry.get("timestamp", "")
        ts_short = ts[11:19] if ts and len(ts) > 19 else ts  # HH:MM:SS

        if entry["type"] == "user":
            text = entry.get("text", "")
            # Truncate for readability
            if len(text) > 500:
                text = text[:500] + "..."
            lines.append(f"### [{ts_short}] USER")
            lines.append(f"")
            lines.append(text)
            lines.append("")

        elif entry["type"] == "assistant":
            lines.append(f"### [{ts_short}] ASSISTANT")
            lines.append("")

            # Thinking
            for t in entry.get("thinking", []):
                lines.append(f"> **Thinking:** {t[:500]}{'...' if len(t) > 500 else ''}")
                lines.append("")

            # Text
            for t in entry.get("text_parts", []):
                if t.strip():
                    lines.append(t[:1000])
                    lines.append("")

            # Tool calls
            for tc in entry.get("tool_calls", []):
                result = tc.get("result_summary", "")
                if len(result) > 200:
                    result = result[:200] + "..."
                lines.append(f"- **{tc['tool']}**: {tc['input_summary']}")
                if result:
                    lines.append(f"  - Result: {result}")
            lines.append("")

        elif entry["type"] == "queue":
            if entry.get("operation") == "enqueue":
                lines.append(f"---")
                lines.append(f"*[{ts_short}] New turn queued*")
                lines.append("")

    # Subagent timelines
    for aid, sa_timeline in sd.get("subagent_timelines", {}).items():
        sa_meta = sd["subagents"].get(aid, {})
        lines.append(f"## Subagent: {sa_meta.get('agent_type', 'unknown')} — {sa_meta.get('description', '')}")
        lines.append(f"*Agent ID: {aid[:12]}*")
        lines.append("")

        for entry in sa_timeline:
            ts = entry.get("timestamp", "")
            ts_short = ts[11:19] if ts and len(ts) > 19 else ts

            if entry["type"] == "assistant":
                for t in entry.get("thinking", []):
                    lines.append(f"> **Thinking:** {t[:300]}{'...' if len(t) > 300 else ''}")
                for t in entry.get("text_parts", []):
                    if t.strip():
                        lines.append(f"[{ts_short}] {t[:500]}")
                for tc in entry.get("tool_calls", []):
                    lines.append(f"- **{tc['tool']}**: {tc['input_summary']}")
                lines.append("")

    return "\n".join(lines)


def build_merged_timeline(all_sessions):
    """Merge multiple session timelines into a single chronological timeline."""
    merged = []
    for sd in all_sessions:
        sid = sd["session_id"][:8]
        project = sd["project"].split("-")[-1] if sd["project"] else "unknown"
        branch = sd.get("git_branch", "")

        for entry in sd["timeline"]:
            ts = entry.get("timestamp")
            if not ts:
                continue
            merged.append({
                "timestamp": ts,
                "session": sid,
                "project": project,
                "branch": branch,
                **{k: v for k, v in entry.items() if k != "timestamp"},
            })

        # Include subagent events in the merged timeline
        for aid, sa_timeline in sd.get("subagent_timelines", {}).items():
            sa_meta = sd["subagents"].get(aid, {})
            for entry in sa_timeline:
                ts = entry.get("timestamp")
                if not ts:
                    continue
                merged.append({
                    "timestamp": ts,
                    "session": sid,
                    "project": project,
                    "branch": branch,
                    "subagent": aid[:12],
                    "subagent_type": sa_meta.get("agent_type", ""),
                    **{k: v for k, v in entry.items() if k != "timestamp"},
                })

    merged.sort(key=lambda x: x["timestamp"])
    return merged


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    since = None
    if args.since:
        since = datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    # Find sessions
    sessions = find_session_files(args.project)
    print(f"Found {len(sessions)} session transcripts")

    # Extract each session
    all_extracted = []
    index_entries = []

    for i, session_info in enumerate(sessions):
        print(f"  [{i+1}/{len(sessions)}] Extracting {session_info['session_id'][:8]}...", end="")

        extracted = extract_session(
            session_info,
            include_thinking=args.include_thinking,
            include_tool_output=args.include_tool_output,
            include_subagents=args.include_subagents,
        )

        if not extracted or not extracted.get("start"):
            print(" (empty, skipped)")
            continue

        # Filter by date
        if since:
            session_start = datetime.fromisoformat(extracted["start"].replace("Z", "+00:00"))
            if session_start < since:
                print(" (before --since, skipped)")
                continue

        print(f" {extracted['user_messages']}u/{extracted['assistant_messages']}a "
              f"{extracted['total_tool_calls']}tools {extracted['subagent_count']}sa")

        # Index entry (without timeline — just metadata)
        index_entry = {k: v for k, v in extracted.items()
                       if k not in ("timeline", "subagent_timelines")}
        index_entries.append(index_entry)

        # Write per-session files
        if args.format in ("jsonl", "both"):
            jsonl_path = output_dir / f"{extracted['session_id']}.jsonl"
            with open(jsonl_path, "w") as f:
                for entry in extracted["timeline"]:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        if args.format in ("markdown", "both"):
            md_path = output_dir / f"{extracted['session_id']}.md"
            with open(md_path, "w") as f:
                f.write(to_markdown(extracted))

        all_extracted.append(extracted)

    # Write index
    index_path = output_dir / "index.jsonl"
    with open(index_path, "w") as f:
        for entry in sorted(index_entries, key=lambda x: x.get("start", "")):
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"\nWrote index: {index_path} ({len(index_entries)} sessions)")

    # Build merged timeline
    if len(all_extracted) > 1:
        merged = build_merged_timeline(all_extracted)
        timeline_path = output_dir / "timeline.jsonl"
        with open(timeline_path, "w") as f:
            for entry in merged:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"Wrote merged timeline: {timeline_path} ({len(merged)} events)")

    print(f"\nDone. Output in {output_dir}/")


if __name__ == "__main__":
    main()
