"""Flow evals — check that flow skills, routing, and gates are properly defined.

Migrated from .agent/evals/flows/*.eval.md

These are structural checks on the flow skill definitions themselves.
LLM-as-judge evaluation of actual session transcripts is deferred to Phase 5
(assess.py), when Langfuse traces are available as inputs.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


# ── debug-flow-routes-correctly ──────────────────────────────────────────
# Source: .agent/evals/flows/debug-flow-routes-correctly.eval.md


@pytest.mark.flow
class TestDebugFlowStructure:
    """debug-flow skill has correct routing signals and phase gates."""

    def test_has_reproduce_phase(self) -> None:
        """debug-flow begins with a Reproduce phase requiring a failing test."""
        text = (ROOT / ".claude" / "skills" / "debug-flow" / "SKILL.md").read_text()
        assert "Phase 1: Reproduce" in text or "Reproduce" in text
        assert "failing test" in text.lower(), "Reproduce phase missing failing test gate"

    def test_has_separate_context_verification(self) -> None:
        """debug-flow requires separate-context verification before closing."""
        text = (ROOT / ".claude" / "skills" / "debug-flow" / "SKILL.md").read_text()
        assert "separate-context" in text.lower() or "Separate-context" in text
        assert "subagent" in text.lower() or "fresh review" in text.lower()

    def test_has_iteration_cap(self) -> None:
        """debug-flow caps fix attempts at 2 before escalating."""
        text = (ROOT / ".claude" / "skills" / "debug-flow" / "SKILL.md").read_text()
        assert "two fix attempts" in text.lower() and "escalat" in text.lower(), (
            "debug-flow missing 2-attempt iteration cap with escalation"
        )

    def test_routing_signals_in_description(self) -> None:
        """debug-flow description includes correct routing signals."""
        text = (ROOT / ".claude" / "skills" / "debug-flow" / "SKILL.md").read_text()
        for signal in ["fix", "bug", "error", "broken", "regression", "failing"]:
            assert signal in text.lower(), f"Missing routing signal: {signal}"

    def test_diagnostic_before_visual_rule(self) -> None:
        """debug-flow has diagnostic-before-visual with correct ordering."""
        text = (ROOT / ".claude" / "skills" / "debug-flow" / "SKILL.md").read_text()
        assert "Diagnostic Before Visual" in text or "diagnostic before visual" in text.lower(), (
            "debug-flow missing Diagnostic Before Visual section"
        )
        # Verify correct ordering: typecheck before console before screenshot
        tsc_pos = text.find("tsc --noEmit")
        console_pos = text.find("console")
        screenshot_pos = text.find("preview_screenshot")
        assert tsc_pos >= 0, "Missing tsc --noEmit step"
        assert console_pos >= 0, "Missing console check step"
        assert screenshot_pos >= 0, "Missing preview_screenshot step"
        assert tsc_pos < console_pos < screenshot_pos, (
            "Diagnostic Before Visual ordering wrong: must be typecheck → console → screenshot"
        )
        # Verify anti-loop guard
        assert "3 cycles" in text or "three cycles" in text.lower(), (
            "Missing anti-loop guard for visual debugging cycles"
        )


# ── feature-flow-requires-spec-gate ──────────────────────────────────────
# Source: .agent/evals/flows/feature-flow-requires-spec-gate.eval.md


@pytest.mark.flow
class TestFeatureFlowStructure:
    """feature-flow skill requires spec gate before implementation."""

    def test_has_intent_check_phase(self) -> None:
        """feature-flow begins with intent check (Phase 0)."""
        text = (ROOT / ".claude" / "skills" / "feature-flow" / "SKILL.md").read_text()
        assert "Phase 0" in text and "Intent" in text

    def test_has_spec_phase_before_implement(self) -> None:
        """feature-flow has Spec phase before Implement phase."""
        text = (ROOT / ".claude" / "skills" / "feature-flow" / "SKILL.md").read_text()
        spec_pos = text.find("Phase 1: Spec")
        impl_pos = text.find("Phase 3: Implement")
        assert spec_pos >= 0, "Missing Spec phase"
        assert impl_pos >= 0, "Missing Implement phase"
        assert spec_pos < impl_pos, "Spec phase must come before Implement"

    def test_spec_requires_human_confirmation(self) -> None:
        """feature-flow spec phase requires human confirmation."""
        text = (ROOT / ".claude" / "skills" / "feature-flow" / "SKILL.md").read_text()
        assert "Human confirmation" in text or "human" in text.lower()

    def test_no_implement_before_spec(self) -> None:
        """Negative constraint: do not start implementing before spec."""
        text = (ROOT / ".claude" / "skills" / "feature-flow" / "SKILL.md").read_text()
        assert "Do NOT start implementing before" in text or "NOT start implementing" in text


# ── refactor-flow-no-behavior-change ─────────────────────────────────────
# Source: .agent/evals/flows/refactor-flow-no-behavior-change.eval.md


@pytest.mark.flow
class TestRefactorFlowStructure:
    """refactor-flow enforces no behavior change."""

    def test_has_snapshot_phase(self) -> None:
        """refactor-flow has a behavioral baseline snapshot phase."""
        text = (ROOT / ".claude" / "skills" / "refactor-flow" / "SKILL.md").read_text()
        assert "Snapshot" in text
        assert "baseline" in text.lower()

    def test_no_behavior_change_rule(self) -> None:
        """refactor-flow explicitly forbids behavior changes."""
        text = (ROOT / ".claude" / "skills" / "refactor-flow" / "SKILL.md").read_text()
        assert "Do NOT change behavior" in text or "NOT change behavior" in text

    def test_no_features_during_refactor(self) -> None:
        """refactor-flow forbids adding features."""
        text = (ROOT / ".claude" / "skills" / "refactor-flow" / "SKILL.md").read_text()
        assert "Do NOT add new features" in text or "NOT add features" in text


# ── flow-escalation-on-repeated-failure ──────────────────────────────────
# Source: .agent/evals/flows/flow-escalation-on-repeated-failure.eval.md


@pytest.mark.flow
class TestFlowEscalation:
    """All flows enforce escalation on repeated failure."""

    FLOW_SKILLS = [
        ROOT / ".claude" / "skills" / "debug-flow" / "SKILL.md",
        ROOT / ".claude" / "skills" / "feature-flow" / "SKILL.md",
        ROOT / ".claude" / "skills" / "refactor-flow" / "SKILL.md",
    ]

    def test_all_flows_have_iteration_cap(self) -> None:
        """Every flow skill mentions escalation after repeated failures."""
        for skill_path in self.FLOW_SKILLS:
            text = skill_path.read_text()
            flow_name = skill_path.parent.name
            assert "2" in text and ("retry" in text.lower() or "attempt" in text.lower()), (
                f"{flow_name} missing iteration cap"
            )
            assert "escalat" in text.lower() or "incident" in text.lower(), (
                f"{flow_name} missing escalation on failure"
            )

    def test_all_flows_require_run_record(self) -> None:
        """Every flow skill requires a run record at close."""
        for skill_path in self.FLOW_SKILLS:
            text = skill_path.read_text()
            flow_name = skill_path.parent.name
            assert "runs.jsonl" in text, (
                f"{flow_name} doesn't require run record in runs.jsonl"
            )

    def test_all_flows_link_task_id(self) -> None:
        """Every flow skill's Phase 5 links the run record task_id to tasks.jsonl."""
        for skill_path in self.FLOW_SKILLS:
            text = skill_path.read_text()
            flow_name = skill_path.parent.name
            assert "tasks.jsonl" in text, (
                f"{flow_name} Phase 5 doesn't reference tasks.jsonl for task ID linkage"
            )
            assert "task_id" in text, (
                f"{flow_name} Phase 5 doesn't mention task_id field"
            )


# ── fix-attempt-tracker hook tests ───────────────────────────────────────
# Direct tests of the hook script behavior.

import json
import subprocess
import tempfile


@pytest.mark.flow
class TestFixAttemptTrackerHook:
    """fix-attempt-tracker.sh correctly tracks, ignores, resets, and blocks."""

    HOOK = ROOT / ".claude" / "hooks" / "fix-attempt-tracker.sh"
    STATE_FILE = ROOT / ".claude" / "hooks" / "fix-attempt-tracker.state"

    def _run_hook(self, tool_name: str, file_path: str = "", command: str = "") -> subprocess.CompletedProcess[str]:
        """Run the hook with simulated tool input, return CompletedProcess."""
        payload = {"tool_name": tool_name, "tool_input": {}}
        if file_path:
            payload["tool_input"]["file_path"] = file_path
        if command:
            payload["tool_input"]["command"] = command
        return subprocess.run(
            ["bash", str(self.HOOK)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=5,
        )

    def _reset_state(self) -> None:
        """Reset the state file to 0."""
        self.STATE_FILE.write_text("0\n")

    def setup_method(self) -> None:
        """Reset state before each test."""
        self._reset_state()

    def teardown_method(self) -> None:
        """Clean up state after each test."""
        self._reset_state()

    def test_ignores_test_files(self) -> None:
        """Edits to test files don't increment the counter."""
        self._run_hook("Edit", file_path="/project/tests/test_foo.py")
        self._run_hook("Edit", file_path="/project/evals/test_bar.py")
        self._run_hook("Write", file_path="/project/src/foo.spec.ts")
        count = int(self.STATE_FILE.read_text().strip())
        assert count == 0, f"Test file edits incremented counter to {count}"

    def test_ignores_docs_and_config(self) -> None:
        """Edits to docs, config, and non-source files don't increment."""
        self._run_hook("Edit", file_path="/project/README.md")
        self._run_hook("Edit", file_path="/project/config.json")
        self._run_hook("Write", file_path="/project/pyproject.toml")
        self._run_hook("Edit", file_path="/project/.claude/settings.yaml")
        count = int(self.STATE_FILE.read_text().strip())
        assert count == 0, f"Doc/config edits incremented counter to {count}"

    def test_counts_source_edits(self) -> None:
        """Edits to source files increment the counter."""
        self._run_hook("Edit", file_path="/project/src/main.py")
        count = int(self.STATE_FILE.read_text().strip())
        assert count == 1

    def test_counts_source_writes(self) -> None:
        """Write tool on source files also increments the counter."""
        self._run_hook("Write", file_path="/project/src/main.py")
        count = int(self.STATE_FILE.read_text().strip())
        assert count == 1

    def test_resets_on_pytest(self) -> None:
        """Running pytest resets the counter to 0."""
        self._run_hook("Edit", file_path="/project/src/main.py")
        self._run_hook("Edit", file_path="/project/src/utils.py")
        assert int(self.STATE_FILE.read_text().strip()) == 2
        self._run_hook("Bash", command=".venv/bin/python -m pytest tests/ -v")
        assert int(self.STATE_FILE.read_text().strip()) == 0

    def test_resets_on_npm_test(self) -> None:
        """Running npm test resets the counter to 0."""
        self._run_hook("Edit", file_path="/project/src/app.tsx")
        assert int(self.STATE_FILE.read_text().strip()) == 1
        self._run_hook("Bash", command="npm test")
        assert int(self.STATE_FILE.read_text().strip()) == 0

    def test_blocks_after_threshold(self) -> None:
        """Third source mutation without tests is blocked (exit 2)."""
        self._run_hook("Edit", file_path="/project/src/a.py")
        self._run_hook("Edit", file_path="/project/src/b.py")
        result = self._run_hook("Edit", file_path="/project/src/c.py")
        assert result.returncode == 2, f"Expected exit 2 (blocked), got {result.returncode}"
        assert "BLOCKED" in result.stderr

    def test_normal_workflow_not_blocked(self) -> None:
        """Edit-edit-test-edit-edit cycle should never block."""
        self._run_hook("Edit", file_path="/project/src/a.py")
        self._run_hook("Edit", file_path="/project/src/b.py")
        self._run_hook("Bash", command="pytest tests/")
        self._run_hook("Edit", file_path="/project/src/c.py")
        result = self._run_hook("Edit", file_path="/project/src/d.py")
        assert result.returncode == 0, f"Normal workflow blocked: {result.stderr}"


# ── skill-triggers-correctly ─────────────────────────────────────────────
# Source: .agent/evals/skills/skill-triggers-correctly.eval.md


@pytest.mark.skill
class TestSkillTriggerTable:
    """Trigger table in CLAUDE.md is complete and valid."""

    def test_trigger_table_exists(self) -> None:
        """CLAUDE.md has a Trigger Table section."""
        text = (ROOT / "CLAUDE.md").read_text()
        assert "## Trigger Table" in text

    def test_trigger_table_has_flow_routing(self) -> None:
        """CLAUDE.md has Task-Type Flow Routing section."""
        text = (ROOT / "CLAUDE.md").read_text()
        assert "Flow Routing" in text
        for flow in ["debug-flow", "feature-flow", "refactor-flow"]:
            assert flow in text, f"Flow routing missing {flow}"

    def test_all_skill_files_exist(self) -> None:
        """Every skill referenced in the root trigger table actually exists.

        Only checks pipeline-level skills in root CLAUDE.md.
        Project-specific triggers are validated by project-level tests.
        """
        text = (ROOT / "CLAUDE.md").read_text()
        import re
        paths = re.findall(r"`([^`]+/skills?/[^`]+\.md)`", text)
        missing = []
        for path in paths:
            # Skip template paths like [project]/skills/...
            if path.startswith("["):
                continue
            if (ROOT / path).exists():
                continue
            missing.append(path)
        assert not missing, f"Skills referenced in trigger table but missing:\n" + "\n".join(missing)
