"""Behavioral evals — check actual agent behavior from session transcripts.

Unlike structural evals (test_flows.py, test_conventions.py), these parse real
conversation transcripts and verify behavioral patterns. They answer: did the
agent actually follow the flows, not just are the flows written correctly?

Transcripts are JSONL files in .agent/conversations/ with this format:
    {"timestamp": ..., "type": "assistant", "tool_calls": [{"tool": "Read", ...}]}
    {"timestamp": ..., "type": "user", "text": "..."}
"""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CONVERSATIONS_DIR = ROOT / ".agent" / "conversations"

# Minimum session size to analyze (skip trivial sessions)
MIN_TOOL_CALLS = 5


def parse_tool_sequence(jsonl_path: Path) -> list[dict]:
    """Extract ordered tool call sequence from a conversation JSONL file.

    Returns list of {"tool": str, "input_summary": str, "timestamp": str}.
    """
    calls = []
    for line in jsonl_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        if entry.get("type") != "assistant":
            continue
        for tc in entry.get("tool_calls", []):
            calls.append({
                "tool": tc.get("tool", ""),
                "input_summary": tc.get("input_summary", ""),
                "timestamp": entry.get("timestamp", ""),
            })
    return calls


@pytest.fixture
def parsed_transcripts() -> list[dict]:
    """Parse all conversation JSONL files into tool-call sequences.

    Returns list of {"id": str, "calls": list[dict]}.
    Only includes sessions with >= MIN_TOOL_CALLS tool calls.
    """
    if not CONVERSATIONS_DIR.exists():
        return []

    transcripts = []
    for jsonl in sorted(CONVERSATIONS_DIR.glob("*.jsonl")):
        if jsonl.name == "index.jsonl":
            continue
        calls = parse_tool_sequence(jsonl)
        if len(calls) >= MIN_TOOL_CALLS:
            transcripts.append({"id": jsonl.stem, "calls": calls})
    return transcripts


# ── Reads before first Edit ──────────────────────────────────────────────
# Mining baseline: 15-30 reads before first edit. Target: <5.


@pytest.mark.behavioral
class TestReadsBeforeFirstEdit:
    """Sessions should not waste excessive reads before starting work."""

    READ_TOOLS = {"Read", "Glob", "Grep"}
    EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}

    def test_median_ramp_up_under_threshold(self, parsed_transcripts: list[dict]) -> None:
        """Median reads-before-first-edit across sessions should be improving.

        Current threshold: <15 (was 15-30 at mining baseline, target <5).
        We use 15 as the "not regressing" bar — tighter thresholds come later.
        """
        if not parsed_transcripts:
            pytest.skip("No transcripts available")

        ramp_ups = []
        for t in parsed_transcripts:
            reads = 0
            for call in t["calls"]:
                if call["tool"] in self.EDIT_TOOLS:
                    break
                if call["tool"] in self.READ_TOOLS:
                    reads += 1
            ramp_ups.append(reads)

        ramp_ups.sort()
        median = ramp_ups[len(ramp_ups) // 2]
        assert median < 15, (
            f"Median reads-before-first-edit is {median} (threshold: <15). "
            f"Distribution: min={ramp_ups[0]}, max={ramp_ups[-1]}, "
            f"count={len(ramp_ups)}"
        )

    def test_no_extreme_ramp_ups(self, parsed_transcripts: list[dict]) -> None:
        """No session should have >50 reads before first edit (extreme waste)."""
        if not parsed_transcripts:
            pytest.skip("No transcripts available")

        extreme = []
        for t in parsed_transcripts:
            reads = 0
            for call in t["calls"]:
                if call["tool"] in self.EDIT_TOOLS:
                    break
                if call["tool"] in self.READ_TOOLS:
                    reads += 1
            if reads > 50:
                extreme.append(f"{t['id'][:8]}: {reads} reads")

        assert not extreme, (
            f"Sessions with extreme ramp-up (>50 reads before edit):\n"
            + "\n".join(extreme)
        )


# ── No excessive retries ────────────────────────────────────────────────
# Flow skill rule: cap fix attempts at 3 before escalating.


@pytest.mark.behavioral
class TestNoExcessiveRetries:
    """Sessions should not show signs of blind retry loops."""

    def test_no_edit_storms(self, parsed_transcripts: list[dict]) -> None:
        """No session should have >5 consecutive Edits to the same file without a test run.

        A "test run" is a Bash call containing pytest/test/npm/cargo keywords.
        This is a lenient threshold — the flow skill says 3, we allow 5 here
        to account for multi-file edits that touch the same file.
        """
        if not parsed_transcripts:
            pytest.skip("No transcripts available")

        TEST_KEYWORDS = ("pytest", "npm test", "cargo test", "go test", "test")
        violations = []

        for t in parsed_transcripts:
            # Track consecutive edits per file
            edit_streak: dict[str, int] = {}
            max_streak = 0
            max_file = ""

            for call in t["calls"]:
                if call["tool"] == "Bash":
                    summary = call.get("input_summary", "").lower()
                    if any(kw in summary for kw in TEST_KEYWORDS):
                        edit_streak.clear()
                elif call["tool"] == "Edit":
                    # Extract file from input_summary (format: "file: /path/to/file")
                    summary = call.get("input_summary", "")
                    file_hint = summary.split("file:")[-1].strip().split()[0] if "file:" in summary else "unknown"
                    edit_streak[file_hint] = edit_streak.get(file_hint, 0) + 1
                    if edit_streak[file_hint] > max_streak:
                        max_streak = edit_streak[file_hint]
                        max_file = file_hint

            if max_streak > 5:
                violations.append(
                    f"{t['id'][:8]}: {max_streak} consecutive edits to {max_file}"
                )

        # Baseline from mining: ~21% of pre-v2 sessions show edit storms.
        # Target: <10% once fix-attempt-tracker hook is active.
        # Current threshold: 25% (not regressing from baseline).
        if parsed_transcripts:
            violation_rate = len(violations) / len(parsed_transcripts)
            assert violation_rate < 0.25, (
                f"{len(violations)}/{len(parsed_transcripts)} sessions ({violation_rate:.0%}) "
                f"show edit storms (>5 consecutive edits without test):\n"
                + "\n".join(violations[:5])
            )


# ── Diagnostic before visual ────────────────────────────────────────────
# Rule: typecheck/console/network before screenshot. Added in v2.1.


@pytest.mark.behavioral
class TestDiagnosticBeforeVisual:
    """Sessions should use diagnostic tools before visual debugging."""

    SCREENSHOT_TOOLS = {"preview_screenshot", "preview_eval"}
    DIAGNOSTIC_TOOLS = {"preview_console_logs", "preview_logs", "preview_network", "preview_inspect", "preview_snapshot"}
    # Bash commands that count as diagnostics
    DIAGNOSTIC_COMMANDS = ("tsc", "typecheck", "npm run typecheck")

    def test_no_screenshot_heavy_sessions_without_diagnostics(self, parsed_transcripts: list[dict]) -> None:
        """Sessions with 3+ screenshots should have used diagnostic tools first.

        A "diagnostic-before-visual violation" is a session that uses 3+ screenshot/eval
        tools without any preceding diagnostic tool call (console, network, typecheck).
        Threshold: <30% of screenshot-heavy sessions should violate.
        """
        if not parsed_transcripts:
            pytest.skip("No transcripts available")

        screenshot_sessions = []
        violations = []

        for t in parsed_transcripts:
            screenshot_count = 0
            has_diagnostic = False

            for call in t["calls"]:
                tool = call["tool"]
                if tool in self.DIAGNOSTIC_TOOLS:
                    has_diagnostic = True
                elif tool == "Bash":
                    summary = call.get("input_summary", "").lower()
                    if any(kw in summary for kw in self.DIAGNOSTIC_COMMANDS):
                        has_diagnostic = True
                elif tool in self.SCREENSHOT_TOOLS:
                    screenshot_count += 1

            if screenshot_count >= 3:
                screenshot_sessions.append(t["id"])
                if not has_diagnostic:
                    violations.append(
                        f"{t['id'][:8]}: {screenshot_count} screenshots, no diagnostics"
                    )

        if not screenshot_sessions:
            pytest.skip("No screenshot-heavy sessions to analyze")

        violation_rate = len(violations) / len(screenshot_sessions)
        assert violation_rate < 0.30, (
            f"{len(violations)}/{len(screenshot_sessions)} screenshot-heavy sessions "
            f"({violation_rate:.0%}) skipped diagnostics:\n"
            + "\n".join(violations[:5])
        )
