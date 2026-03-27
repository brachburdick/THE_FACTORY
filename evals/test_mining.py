"""Mining-derived evals — regression tests for the top 5 failure patterns.

Created from conversation mining results (support/v2/conversation-mining-results.md).
These check that the fixes from Phase 1 are in place and working.

Tests are split into two categories:
- @pytest.mark.mining — pipeline-level checks (run always)
- @pytest.mark.scue — SCUE-project-specific checks (skip when /projects absent)
"""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCUE_ROOT = ROOT / "projects" / "DjTools" / "scue"

# Skip SCUE-specific tests if projects directory is absent or SCUE doesn't exist
scue_available = pytest.mark.skipif(
    not SCUE_ROOT.exists(),
    reason="SCUE project not available (projects/ may be gitignored or absent)",
)


# ── Mining Finding #1: Session continuity ────────────────────────────────
# Problem: 10% ramp-up tax, 1500 wasted tool calls re-exploring SCUE.
# Fix: State snapshot hook + codebase orientation skill.


@pytest.mark.mining
class TestSessionContinuity:
    """Infrastructure for session-to-session continuity exists."""

    def test_state_snapshot_hook_exists(self) -> None:
        """The state-snapshot Stop hook is configured (Python, no jq)."""
        hook_py = ROOT / ".claude" / "hooks" / "state-snapshot.py"
        assert hook_py.exists(), "Missing state-snapshot.py hook"
        # Verify the old jq-based .sh is gone (removed in #8)
        hook_sh = ROOT / ".claude" / "hooks" / "state-snapshot.sh"
        assert not hook_sh.exists(), "Stale state-snapshot.sh still present — remove it"

    @scue_available
    def test_codebase_orientation_skill_exists(self) -> None:
        """SCUE codebase orientation skill exists and is referenced in trigger table."""
        skill_path = SCUE_ROOT / "skills" / "codebase-orientation.md"
        assert skill_path.exists(), "Missing codebase-orientation.md skill"
        text = skill_path.read_text()
        assert "File-to-Responsibility" in text or "File Map" in text, (
            "Orientation skill missing file-to-responsibility map"
        )
        assert "Data Flow" in text or "Data flow" in text, (
            "Orientation skill missing data flow chains"
        )

    @scue_available
    def test_scue_trigger_table_references_orientation(self) -> None:
        """SCUE CLAUDE.md trigger table includes codebase orientation."""
        claude_md = SCUE_ROOT / "CLAUDE.md"
        assert claude_md.exists(), "SCUE CLAUDE.md not found"
        text = claude_md.read_text()
        assert "codebase-orientation" in text, (
            "SCUE CLAUDE.md trigger table missing codebase-orientation entry"
        )


# ── Mining Finding #2: API misuse from missing reference docs ────────────
# Problem: #1 bug type (7 instances). beat-link API repeatedly researched.
# Fix: API reference sections in beat-link-bridge.md and pioneer-hardware.md.


@pytest.mark.mining
@scue_available
class TestApiReferenceDocs:
    """API reference details are present in domain skills."""

    def test_beat_link_bridge_has_api_reference(self) -> None:
        """beat-link-bridge skill contains API reference for CdjStatus."""
        skill_path = SCUE_ROOT / "skills" / "beat-link-bridge.md"
        assert skill_path.exists()
        text = skill_path.read_text()
        assert "CdjStatus" in text, "Missing CdjStatus API reference"
        assert "getEffectiveTempo" in text, "Missing getEffectiveTempo docs"
        assert "Finder" in text and "order" in text.lower(), (
            "Missing Finder start order documentation"
        )

    def test_pioneer_hardware_has_device_specifics(self) -> None:
        """pioneer-hardware skill contains XDJ-AZ and Opus Quad specifics."""
        skill_path = SCUE_ROOT / "skills" / "pioneer-hardware.md"
        assert skill_path.exists()
        text = skill_path.read_text()
        assert "XDJ-AZ" in text, "Missing XDJ-AZ specifics"
        assert "BLUE" in text, "Missing BLUE waveform style documentation"
        assert "Opus Quad" in text or "DLP" in text, "Missing DLP device documentation"


# ── Mining Finding #3: Normalized test failures ──────────────────────────
# Problem: Broken tests carried across sessions, layer1 tests skipped.
# Fix: Zero known failures gate.


@pytest.mark.mining
@scue_available
class TestZeroKnownFailures:
    """Test suite has zero pre-existing failures."""

    # Known quarantined failures in SCUE — track explicitly so new regressions are caught
    QUARANTINED = {
        "tests/test_layer1/test_strata_standard.py::TestEngineRouting::test_analyze_routes_to_standard",
    }

    def test_scue_tests_no_new_failures(self) -> None:
        """SCUE test suite has no failures beyond quarantined known issues."""
        import subprocess

        result = subprocess.run(
            [str(SCUE_ROOT / ".venv" / "bin" / "python"), "-m", "pytest", "tests/", "-q",
             "--tb=line", "--no-header"],
            cwd=str(SCUE_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            return  # All pass — even better

        # Extract FAILED lines from output
        failed_tests = set()
        for line in result.stdout.splitlines():
            if line.startswith("FAILED "):
                test_path = line.split("FAILED ")[-1].split(" -")[0].strip()
                failed_tests.add(test_path)

        new_failures = failed_tests - self.QUARANTINED
        assert not new_failures, (
            f"SCUE has NEW test failures (not quarantined):\n"
            + "\n".join(f"  - {t}" for t in sorted(new_failures))
            + f"\n\nQuarantined (known): {self.QUARANTINED}"
        )


# ── Mining Finding #4: Redundant subagent exploration ────────────────────
# Problem: Up to 29 subagents reading overlapping files.
# Fix: Subagent dedup guidance in flow skills.


@pytest.mark.mining
class TestSubagentGuidance:
    """Flow skills contain subagent scope deduplication guidance."""

    FLOW_SKILLS = [
        ROOT / ".claude" / "skills" / "debug-flow" / "SKILL.md",
        ROOT / ".claude" / "skills" / "feature-flow" / "SKILL.md",
        ROOT / ".claude" / "skills" / "refactor-flow" / "SKILL.md",
    ]

    def test_all_flows_have_subagent_guidance(self) -> None:
        """Every flow skill has a Subagent Guidance/Policy section."""
        for skill_path in self.FLOW_SKILLS:
            assert skill_path.exists(), f"Missing flow skill: {skill_path}"
            text = skill_path.read_text()
            assert "Subagent Guidance" in text or "Subagent Policy" in text, (
                f"{skill_path.parent.name} flow missing Subagent Guidance/Policy section"
            )
            assert "specific file scope" in text, (
                f"{skill_path.parent.name} flow missing file scope guidance"
            )


# ── Mining Finding #5: Feature completion status tracking ────────────────
# Problem: Agents waste time implementing features that already exist.
# Fix: Pre-implementation checklist in feature-flow.


@pytest.mark.mining
class TestPreFlightReadinessCheck:
    """Flow skills include pre-flight readiness checks (tf-027)."""

    def test_feature_flow_has_preflight(self) -> None:
        """feature-flow SKILL.md includes pre-flight readiness check."""
        skill_path = ROOT / ".claude" / "skills" / "feature-flow" / "SKILL.md"
        text = skill_path.read_text()
        assert "Pre-Flight" in text, (
            "feature-flow missing Pre-Flight Readiness Check"
        )
        # Must check for prior work (original mining finding)
        assert "already" in text.lower() and "exist" in text.lower(), (
            "Pre-flight checklist doesn't check for already-existing work"
        )
        # Must check risk level (tf-027 requirement)
        assert "risk" in text.lower(), (
            "Pre-flight checklist doesn't verify risk level is set"
        )

    def test_refactor_flow_has_preflight(self) -> None:
        """refactor-flow SKILL.md includes pre-flight readiness check."""
        skill_path = ROOT / ".claude" / "skills" / "refactor-flow" / "SKILL.md"
        text = skill_path.read_text()
        assert "Pre-Flight" in text, (
            "refactor-flow missing Pre-Flight Readiness Check"
        )
        assert "risk" in text.lower(), (
            "Pre-flight checklist doesn't verify risk level is set"
        )


# ── Hooks infrastructure ─────────────────────────────────────────────────


@pytest.mark.mining
class TestHooksInfrastructure:
    """Claude Code hooks are configured and executable."""

    def test_settings_json_has_hooks(self) -> None:
        """settings.json has hook configuration."""
        settings_path = ROOT / ".claude" / "settings.json"
        assert settings_path.exists(), "Missing .claude/settings.json"
        settings = json.loads(settings_path.read_text())
        assert "hooks" in settings, "settings.json missing hooks configuration"
        assert "Stop" in settings["hooks"], "No Stop hooks configured"
        assert "PreToolUse" in settings["hooks"], "No PreToolUse hooks configured"

    def test_git_guard_hook_exists(self) -> None:
        """git-guard hook exists and is executable."""
        hook = ROOT / ".claude" / "hooks" / "git-guard.sh"
        assert hook.exists(), "Missing git-guard.sh"
        assert hook.stat().st_mode & 0o111, "git-guard.sh not executable"

    def test_langfuse_hook_exists(self) -> None:
        """langfuse-trace hook exists."""
        hook = ROOT / ".claude" / "hooks" / "langfuse-trace.py"
        assert hook.exists(), "Missing langfuse-trace.py"
