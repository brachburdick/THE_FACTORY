#!/usr/bin/env python3
"""
Pipeline assessment tool for THE_FACTORY v2.

Pulls session data, scores it against baselines, identifies low performers,
and generates improvement candidates.

Usage:
    python scripts/assess.py --last 20          # Assess last 20 sessions
    python scripts/assess.py --baseline         # Show current baselines
    python scripts/assess.py --improvements     # Show pending improvement candidates

Sources (in priority order):
    1. Langfuse traces (if configured)
    2. Local state snapshots (.agent/state-snapshot.json)
    3. Local conversation transcripts (.agent/conversations/)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
AGENT_DIR = ROOT / ".agent"
CONVERSATIONS_DIR = AGENT_DIR / "conversations"
IMPROVEMENTS_FILE = ROOT / "support" / "v2" / "improvement-candidates.jsonl"

# Phase 0 mining baselines (from conversation-mining-results.md)
BASELINES = {
    "waste_pct": 25.0,
    "bug_catch_rate": 0.75,
    "reads_before_first_edit": {"low": 15, "high": 30},
    "api_misuse_bugs_per_20": 7,
    "pre_existing_test_failures": 2,
}


def show_baselines() -> None:
    """Display the Phase 0 mining baselines."""
    print("\n=== Phase 0 Baselines (from conversation mining) ===\n")
    print(f"  Overall waste:              ~{BASELINES['waste_pct']}%")
    print(f"  Bug catch rate:             {BASELINES['bug_catch_rate']*100:.0f}%")
    print(f"  Reads before first Edit:    {BASELINES['reads_before_first_edit']['low']}-{BASELINES['reads_before_first_edit']['high']}")
    print(f"  API misuse bugs / 20 sess:  {BASELINES['api_misuse_bugs_per_20']}")
    print(f"  Pre-existing test failures: {BASELINES['pre_existing_test_failures']}")
    print()
    print("  Target after v2 migration:")
    print(f"    Waste:                    <10%")
    print(f"    Bug catch rate:           >90%")
    print(f"    Reads before first Edit:  <5")
    print(f"    API misuse bugs / 20:     <2")
    print(f"    Pre-existing failures:    0")
    print()


def get_langfuse_sessions(count: int) -> list[dict[str, Any]] | None:
    """Pull recent sessions from Langfuse if configured."""
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
    host = os.environ.get("LANGFUSE_BASE_URL") or os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if not public_key or not secret_key:
        return None

    try:
        from langfuse import Langfuse
        langfuse = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
        )
        # Fetch recent traces
        traces = langfuse.fetch_traces(limit=count)
        sessions = []
        for trace in traces.data:
            session = {
                "source": "langfuse",
                "session_id": trace.id,
                "name": trace.name,
                "timestamp": str(trace.timestamp) if trace.timestamp else None,
                "metadata": trace.metadata or {},
                "tags": trace.tags or [],
                "scores": {},
            }
            # Fetch scores for this trace
            if hasattr(trace, 'scores') and trace.scores:
                for score in trace.scores:
                    session["scores"][score.name] = score.value
            sessions.append(session)
        return sessions
    except Exception as e:
        print(f"  Warning: Langfuse fetch failed: {e}", file=sys.stderr)
        return None


def get_local_sessions(count: int) -> list[dict[str, Any]]:
    """Pull session data from local conversation index.

    If index.jsonl is missing or stale, auto-rebuilds it via index-conversations.py.
    Sorts by recency (mtime descending), not message count.
    """
    index_path = CONVERSATIONS_DIR / "index.jsonl"

    # Auto-rebuild index if missing or stale
    if not index_path.exists() or _index_is_stale(index_path):
        _rebuild_index()

    if not index_path.exists():
        return []

    entries = []
    for line in index_path.read_text().splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))

    # Sort by recency (mtime descending, then session end time)
    entries.sort(
        key=lambda e: e.get("mtime", 0),
        reverse=True,
    )

    sessions = []
    for entry in entries[:count]:
        session: dict[str, Any] = {
            "source": "local",
            "session_id": entry.get("session_id", "unknown"),
            "project": entry.get("project", "unknown"),
            "user_messages": entry.get("user_messages", 0),
            "assistant_messages": entry.get("assistant_messages", 0),
            "tool_calls": entry.get("tool_calls", 0) or entry.get("total_tool_calls", 0),
            "subagent_count": entry.get("subagent_count", 0),
        }
        # Include reads_before_edit if available from index
        if "reads_before_edit" in entry:
            session["scores"] = {"ramp-up-reads": entry["reads_before_edit"]}
        sessions.append(session)

    return sessions


def _index_is_stale(index_path: Path) -> bool:
    """Check if any .jsonl transcript is newer than the index."""
    if not index_path.exists():
        return True
    index_mtime = index_path.stat().st_mtime
    for jsonl in CONVERSATIONS_DIR.glob("*.jsonl"):
        if jsonl.name == "index.jsonl":
            continue
        if jsonl.stat().st_mtime > index_mtime:
            return True
    return False


def _rebuild_index() -> None:
    """Rebuild the conversation index by running index-conversations.py."""
    import subprocess
    indexer = ROOT / "scripts" / "index-conversations.py"
    if indexer.exists():
        subprocess.run(
            [sys.executable, str(indexer)],
            capture_output=True,
            timeout=60,
        )


def score_sessions(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    """Score a batch of sessions against baselines."""
    if not sessions:
        return {"error": "No sessions to score"}

    total_sessions = len(sessions)
    source = sessions[0].get("source", "unknown")

    # Aggregate metrics
    total_tool_calls = sum(s.get("tool_calls", 0) for s in sessions)
    total_subagents = sum(s.get("subagent_count", 0) for s in sessions)
    avg_messages = sum(
        s.get("user_messages", 0) + s.get("assistant_messages", 0) for s in sessions
    ) / total_sessions if total_sessions > 0 else 0

    # Langfuse-sourced scores
    ramp_up_scores = []
    for s in sessions:
        if "ramp-up-reads" in s.get("scores", {}):
            ramp_up_scores.append(s["scores"]["ramp-up-reads"])

    report = {
        "timestamp": datetime.now(tz=__import__('datetime').timezone.utc).isoformat(),
        "source": source,
        "sessions_analyzed": total_sessions,
        "metrics": {
            "total_tool_calls": total_tool_calls,
            "total_subagents": total_subagents,
            "avg_messages_per_session": round(avg_messages, 1),
            "subagent_ratio": round(total_subagents / total_sessions, 1) if total_sessions else 0,
        },
        "vs_baseline": {},
    }

    # Compare against baselines
    if ramp_up_scores:
        avg_ramp = sum(ramp_up_scores) / len(ramp_up_scores)
        report["metrics"]["avg_reads_before_edit"] = round(avg_ramp, 1)
        baseline_low = BASELINES["reads_before_first_edit"]["low"]
        if avg_ramp < 5:
            report["vs_baseline"]["ramp_up"] = f"IMPROVED: {avg_ramp:.1f} reads (was {baseline_low}-30)"
        elif avg_ramp < baseline_low:
            report["vs_baseline"]["ramp_up"] = f"Better: {avg_ramp:.1f} reads (was {baseline_low}-30)"
        else:
            report["vs_baseline"]["ramp_up"] = f"No change: {avg_ramp:.1f} reads (baseline {baseline_low}-30)"

    return report


def generate_improvements(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate improvement candidates from assessment report."""
    candidates = []

    metrics = report.get("metrics", {})

    # High subagent ratio suggests redundant exploration
    if metrics.get("subagent_ratio", 0) > 5:
        candidates.append({
            "rank": len(candidates) + 1,
            "category": "pipeline",
            "title": "Reduce subagent count per session",
            "description": f"Average {metrics['subagent_ratio']} subagents/session. Mining baseline was ~5. Consider tightening subagent scope guidance.",
            "suggested_type": "skill",
            "status": "pending",
        })

    # High avg reads before edit
    avg_ramp = metrics.get("avg_reads_before_edit")
    if avg_ramp and avg_ramp > 10:
        candidates.append({
            "rank": len(candidates) + 1,
            "category": "pipeline",
            "title": "Further reduce session ramp-up",
            "description": f"Average {avg_ramp} reads before first edit. Target is <5. Check if state snapshot and codebase orientation are being loaded.",
            "suggested_type": "hook",
            "status": "pending",
        })

    return candidates


def assess(count: int) -> None:
    """Main assessment flow."""
    print(f"\n=== Assessing Last {count} Sessions ===\n")

    # Try Langfuse first, fall back to local
    sessions = get_langfuse_sessions(count)
    if sessions:
        print(f"  Source: Langfuse ({len(sessions)} traces)")
    else:
        sessions = get_local_sessions(count)
        if sessions:
            print(f"  Source: Local conversations ({len(sessions)} sessions)")
            print(f"  Sampled: {', '.join(s['session_id'][:8] for s in sessions[:5])}" +
                  (f"... +{len(sessions)-5} more" if len(sessions) > 5 else ""))
        else:
            print("  No session data found. Run `python scripts/index-conversations.py` first,")
            print("  or configure Langfuse env vars.")
            return

    # Score
    report = score_sessions(sessions)
    print(f"\n--- Metrics ---")
    for key, val in report.get("metrics", {}).items():
        print(f"  {key}: {val}")

    if report.get("vs_baseline"):
        print(f"\n--- vs. Phase 0 Baselines ---")
        for key, val in report["vs_baseline"].items():
            print(f"  {key}: {val}")

    # Generate improvements
    candidates = generate_improvements(report)
    if candidates:
        print(f"\n--- Improvement Candidates ---")
        for c in candidates:
            print(f"  [{c['status'].upper()}] {c['title']}")
            print(f"    {c['description']}")
            print()

        # Save candidates
        IMPROVEMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(IMPROVEMENTS_FILE, "a") as f:
            for c in candidates:
                c["timestamp"] = report["timestamp"]
                f.write(json.dumps(c) + "\n")
        print(f"  Candidates saved to {IMPROVEMENTS_FILE.relative_to(ROOT)}")
    else:
        print(f"\n  No improvement candidates generated. Metrics look good.")

    print()


def show_improvements() -> None:
    """Show pending improvement candidates."""
    if not IMPROVEMENTS_FILE.exists():
        print("\nNo improvement candidates yet. Run `assess --last 20` first.\n")
        return

    print("\n=== Pending Improvement Candidates ===\n")
    for line in IMPROVEMENTS_FILE.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        c = json.loads(line)
        status = c.get("status", "pending").upper()
        print(f"  [{status}] {c.get('title', 'untitled')}")
        print(f"    {c.get('description', '')}")
        print(f"    Type: {c.get('suggested_type', '?')} | From: {c.get('timestamp', '?')}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="THE_FACTORY pipeline assessment")
    parser.add_argument("--last", type=int, help="Assess last N sessions")
    parser.add_argument("--baseline", action="store_true", help="Show Phase 0 baselines")
    parser.add_argument("--improvements", action="store_true", help="Show pending improvements")

    args = parser.parse_args()

    if args.baseline:
        show_baselines()
    elif args.improvements:
        show_improvements()
    elif args.last:
        assess(args.last)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
