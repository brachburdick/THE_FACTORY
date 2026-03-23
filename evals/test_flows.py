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
        """debug-flow caps fix attempts at 3 before escalating."""
        text = (ROOT / ".claude" / "skills" / "debug-flow" / "SKILL.md").read_text()
        assert "3" in text and "escalat" in text.lower(), (
            "debug-flow missing 3-attempt iteration cap with escalation"
        )

    def test_routing_signals_in_description(self) -> None:
        """debug-flow description includes correct routing signals."""
        text = (ROOT / ".claude" / "skills" / "debug-flow" / "SKILL.md").read_text()
        for signal in ["fix", "bug", "error", "broken", "regression", "failing"]:
            assert signal in text.lower(), f"Missing routing signal: {signal}"


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
            assert "3" in text and ("retry" in text.lower() or "attempt" in text.lower()), (
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
        """Every skill referenced in the trigger table actually exists."""
        text = (ROOT / "CLAUDE.md").read_text()
        import re
        paths = re.findall(r"`([^`]+/skills?/[^`]+\.md)`", text)
        # Trigger table uses shorthand paths. Resolve against known project locations.
        SEARCH_ROOTS = [
            ROOT,
            ROOT / "projects" / "DjTools",  # scue lives here
            ROOT / "projects",               # CRUCIBLE, Tinyshop
        ]
        missing = []
        for path in paths:
            # Skip template paths like [project]/skills/...
            if path.startswith("["):
                continue
            found = False
            for search_root in SEARCH_ROOTS:
                if (search_root / path).exists():
                    found = True
                    break
            if not found:
                missing.append(path)
        assert not missing, f"Skills referenced in trigger table but missing:\n" + "\n".join(missing)
