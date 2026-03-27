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


def compute_slos(count: int = 20) -> dict[str, Any]:
    """Compute pipeline SLO metrics from runs.jsonl.

    Returns dict with metric name → {value, target, status} for each SLO.
    """
    runs_file = AGENT_DIR / "runs.jsonl"
    if not runs_file.exists():
        return {}

    runs_raw = []
    for line in runs_file.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                runs_raw.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # Deduplicate by run_id (last entry wins, same as JSONL append semantics)
    seen_ids: dict[str, dict] = {}
    for r in runs_raw:
        rid = r.get("run_id", "")
        if rid:
            seen_ids[rid] = r
        else:
            seen_ids[f"_anon_{len(seen_ids)}"] = r
    runs = list(seen_ids.values())[-count:]
    if not runs:
        return {}

    total = len(runs)
    slos: dict[str, Any] = {}

    # 1. Completion Rate: % success
    success_count = sum(1 for r in runs if r.get("result") == "success")
    completion_rate = round(success_count / total * 100, 1)
    slos["completion_rate"] = {
        "value": completion_rate,
        "target": 80.0,
        "unit": "%",
        "status": "met" if completion_rate >= 80.0 else "missed",
    }

    # 2. Rework Rate: % of task_ids appearing in 2+ runs
    task_counts: dict[str, int] = {}
    for r in runs:
        tid = r.get("task_id", "")
        if tid:
            task_counts[tid] = task_counts.get(tid, 0) + 1
    reworked = sum(1 for c in task_counts.values() if c >= 2)
    unique_tasks = len(task_counts)
    rework_rate = round(reworked / unique_tasks * 100, 1) if unique_tasks else 0.0
    slos["rework_rate"] = {
        "value": rework_rate,
        "target": 15.0,
        "unit": "%",
        "status": "met" if rework_rate <= 15.0 else "missed",
    }

    # 3. Escalation Rate: % blocked
    blocked_count = sum(1 for r in runs if r.get("result") == "blocked")
    escalation_rate = round(blocked_count / total * 100, 1)
    slos["escalation_rate"] = {
        "value": escalation_rate,
        "target": 20.0,
        "unit": "%",
        "status": "met" if escalation_rate <= 20.0 else "missed",
    }

    # 4. Test-Gate Failure Rate: % with evals_failed > 0
    # Only count runs that actually report eval data (missing ≠ 0)
    runs_with_eval_data = [r for r in runs if "evals_failed" in r and not r.get("backfilled")]
    runs_missing_eval_data = total - len(runs_with_eval_data)
    test_fail_count = sum(1 for r in runs_with_eval_data if (r.get("evals_failed") or 0) > 0)
    test_fail_rate = round(test_fail_count / len(runs_with_eval_data) * 100, 1) if runs_with_eval_data else 0.0
    test_gate_status = "met" if test_fail_rate <= 5.0 else "missed"
    if runs_missing_eval_data > len(runs_with_eval_data):
        test_gate_status = "insufficient_data"
    slos["test_gate_failure_rate"] = {
        "value": test_fail_rate,
        "target": 5.0,
        "unit": "%",
        "status": test_gate_status,
        "sample_size": len(runs_with_eval_data),
        "missing_data": runs_missing_eval_data,
    }

    # 5. Operator Review Latency (if data exists, tf-053)
    latencies = [
        r["time_to_operator_response"]
        for r in runs
        if "time_to_operator_response" in r and r["time_to_operator_response"] is not None
    ]
    if latencies:
        latencies.sort()
        median_latency = latencies[len(latencies) // 2]
        slos["operator_review_latency"] = {
            "value": median_latency,
            "target": None,  # No target yet — measuring first
            "unit": "minutes",
            "status": "measuring",
            "sample_size": len(latencies),
        }

    return slos


def analyze_flakiness(count: int = 20) -> dict[str, Any]:
    """Analyze eval flakiness across recent runs.

    A test is considered flaky if it fails in >10% of runs where it was
    reported, without corresponding code changes to its tested area.

    Returns dict with test_name → {fail_count, total_runs, fail_rate, flaky}.
    """
    runs_file = AGENT_DIR / "runs.jsonl"
    if not runs_file.exists():
        return {}

    runs = []
    for line in runs_file.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                runs.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    runs = runs[-count:]

    # Count failures per test name across runs
    test_failures: dict[str, int] = {}
    runs_with_eval_data = 0
    for r in runs:
        failures = r.get("eval_failures", [])
        if failures is not None:
            runs_with_eval_data += 1
            for test_name in failures:
                test_failures[test_name] = test_failures.get(test_name, 0) + 1

    if not runs_with_eval_data:
        return {}

    results = {}
    for test_name, fail_count in test_failures.items():
        fail_rate = round(fail_count / runs_with_eval_data * 100, 1)
        results[test_name] = {
            "fail_count": fail_count,
            "total_runs": runs_with_eval_data,
            "fail_rate": fail_rate,
            "flaky": fail_rate > 10.0 and fail_rate < 90.0,  # >90% is genuinely broken, not flaky
        }

    return results


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


def assess(count: int, out_path: str | None = None) -> None:
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

    # Pipeline SLOs from runs.jsonl
    slos = compute_slos(count)
    if slos:
        report["slos"] = slos
        print(f"\n--- Pipeline SLOs (last {count} runs) ---")
        for name, slo in slos.items():
            target_str = f"target: {'≤' if name in ('rework_rate', 'escalation_rate', 'test_gate_failure_rate') else '≥'}{slo['target']}{slo['unit']}" if slo.get('target') is not None else "measuring"
            status = "✓" if slo["status"] == "met" else ("📊" if slo["status"] == "measuring" else "✗")
            print(f"  {status} {name}: {slo['value']}{slo['unit']} ({target_str})")

    # Eval flakiness analysis
    flaky_tests = analyze_flakiness(count)
    if flaky_tests:
        report["flakiness"] = flaky_tests
        flaky_names = [name for name, info in flaky_tests.items() if info["flaky"]]
        if flaky_names:
            print(f"\n--- Flaky Tests (>10% fail rate) ---")
            for name in flaky_names:
                info = flaky_tests[name]
                print(f"  ⚠ {name}: {info['fail_rate']}% ({info['fail_count']}/{info['total_runs']} runs)")

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

    # Structured output
    if out_path:
        report["candidates"] = candidates
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n")
        print(f"\n  Report written to {out_path}")

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
    parser.add_argument("--out", type=str, help="Write JSON report to this path (for CI artifacts)")

    args = parser.parse_args()

    if args.baseline:
        show_baselines()
    elif args.improvements:
        show_improvements()
    elif args.last:
        assess(args.last, out_path=args.out)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
