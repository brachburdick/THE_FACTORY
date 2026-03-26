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
        """Reset the state file to 0/0/0/ (fix/total/cycles/files)."""
        self.STATE_FILE.write_text("0\n0\n0\n\n")

    def _read_fix_count(self) -> int:
        """Read line 1: mutations since last test."""
        lines = self.STATE_FILE.read_text().strip().split("\n")
        return int(lines[0]) if lines and lines[0] else 0

    def _read_total_count(self) -> int:
        """Read line 2: total mutations this phase (compound budget)."""
        lines = self.STATE_FILE.read_text().strip().split("\n")
        return int(lines[1]) if len(lines) > 1 and lines[1] else 0

    def _read_test_cycles(self) -> int:
        """Read line 3: number of edit-test cycles."""
        lines = self.STATE_FILE.read_text().strip().split("\n")
        return int(lines[2]) if len(lines) > 2 and lines[2] else 0

    def _read_modified_files(self) -> str:
        """Read line 4: comma-separated modified file basenames."""
        lines = self.STATE_FILE.read_text().split("\n")
        return lines[3] if len(lines) > 3 else ""

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
        assert self._read_fix_count() == 0, "Test file edits incremented counter"

    def test_ignores_docs_and_config(self) -> None:
        """Edits to docs, config, and non-source files don't increment."""
        self._run_hook("Edit", file_path="/project/README.md")
        self._run_hook("Edit", file_path="/project/config.json")
        self._run_hook("Write", file_path="/project/pyproject.toml")
        self._run_hook("Edit", file_path="/project/.claude/settings.yaml")
        assert self._read_fix_count() == 0, "Doc/config edits incremented counter"

    def test_counts_source_edits(self) -> None:
        """Edits to source files increment both counters."""
        self._run_hook("Edit", file_path="/project/src/main.py")
        assert self._read_fix_count() == 1
        assert self._read_total_count() == 1

    def test_counts_source_writes(self) -> None:
        """Write tool on source files also increments both counters."""
        self._run_hook("Write", file_path="/project/src/main.py")
        assert self._read_fix_count() == 1
        assert self._read_total_count() == 1

    def test_resets_fix_count_on_pytest(self) -> None:
        """Running pytest resets fix-attempt counter but NOT total budget."""
        self._run_hook("Edit", file_path="/project/src/main.py")
        self._run_hook("Edit", file_path="/project/src/utils.py")
        assert self._read_fix_count() == 2
        assert self._read_total_count() == 2
        self._run_hook("Bash", command=".venv/bin/python -m pytest tests/ -v")
        assert self._read_fix_count() == 0, "Fix count should reset on test run"
        assert self._read_total_count() == 2, "Total budget should NOT reset on test run"

    def test_resets_on_npm_test(self) -> None:
        """Running npm test resets fix-attempt counter."""
        self._run_hook("Edit", file_path="/project/src/app.tsx")
        assert self._read_fix_count() == 1
        self._run_hook("Bash", command="npm test")
        assert self._read_fix_count() == 0

    def test_blocks_after_fix_threshold(self) -> None:
        """Third source mutation without tests is blocked (exit 2)."""
        self._run_hook("Edit", file_path="/project/src/a.py")
        self._run_hook("Edit", file_path="/project/src/b.py")
        result = self._run_hook("Edit", file_path="/project/src/c.py")
        assert result.returncode == 2, f"Expected exit 2 (blocked), got {result.returncode}"
        assert "BLOCKED" in result.stderr

    def test_normal_workflow_not_blocked(self) -> None:
        """Edit-edit-test-edit-edit cycle should never block fix-attempt cap."""
        self._run_hook("Edit", file_path="/project/src/a.py")
        self._run_hook("Edit", file_path="/project/src/b.py")
        self._run_hook("Bash", command="pytest tests/")
        self._run_hook("Edit", file_path="/project/src/c.py")
        result = self._run_hook("Edit", file_path="/project/src/d.py")
        assert result.returncode == 0, f"Normal workflow blocked: {result.stderr}"

    def test_budget_accumulates_across_test_resets(self) -> None:
        """Total budget counter grows even when fix counter resets on tests."""
        # 2 edits, test, 2 edits, test, 2 edits — fix never exceeds 2
        for _ in range(3):
            self._run_hook("Edit", file_path="/project/src/a.py")
            self._run_hook("Edit", file_path="/project/src/b.py")
            self._run_hook("Bash", command="pytest tests/")
        assert self._read_fix_count() == 0, "Fix count should be 0 after test"
        assert self._read_total_count() == 6, "Total should accumulate across resets"

    def test_budget_reset_clears_all_counters(self) -> None:
        """budget-reset Bash command resets all counters and state."""
        self._run_hook("Edit", file_path="/project/src/a.py")
        self._run_hook("Edit", file_path="/project/src/b.py")
        self._run_hook("Bash", command="pytest tests/")  # creates a cycle
        self._run_hook("Edit", file_path="/project/src/c.py")
        assert self._read_total_count() == 3
        assert self._read_test_cycles() == 1
        self._run_hook("Bash", command="echo budget-reset")
        assert self._read_fix_count() == 0, "Fix count should reset"
        assert self._read_total_count() == 0, "Total should reset"
        assert self._read_test_cycles() == 0, "Cycles should reset"
        assert self._read_modified_files() == "", "Modified files should clear"

    def test_budget_block_message(self) -> None:
        """When total mutations exceed default (medium=7) budget, block."""
        self.STATE_FILE.write_text("0\n7\n0\n\n")
        result = self._run_hook("Edit", file_path="/project/src/overflow.py")
        assert result.returncode == 2, f"Expected budget block, got {result.returncode}"
        assert "BUDGET EXHAUSTED" in result.stderr

    def test_circuit_breaker_spiral(self) -> None:
        """Edit-test spiral detection blocks after cycle threshold (medium=3)."""
        # Simulate 3 edit-test cycles
        for _ in range(3):
            self._run_hook("Edit", file_path="/project/src/a.py")
            self._run_hook("Bash", command="pytest tests/")
        assert self._read_test_cycles() == 3
        # Next edit should be blocked by circuit breaker
        result = self._run_hook("Edit", file_path="/project/src/a.py")
        assert result.returncode == 2, f"Expected circuit breaker, got {result.returncode}"
        assert "CIRCUIT BREAKER" in result.stderr
        assert "spiral" in result.stderr.lower()

    def test_test_cycle_only_counts_when_mutations_exist(self) -> None:
        """Test runs without preceding mutations don't increment cycle counter."""
        self._run_hook("Bash", command="pytest tests/")
        self._run_hook("Bash", command="pytest tests/")
        self._run_hook("Bash", command="pytest tests/")
        assert self._read_test_cycles() == 0, "Empty test runs shouldn't count as cycles"

    def test_tracks_modified_files(self) -> None:
        """Modified files are tracked across mutations."""
        self._run_hook("Edit", file_path="/project/src/foo.py")
        self._run_hook("Edit", file_path="/project/src/bar.py")
        self._run_hook("Bash", command="pytest tests/")
        self._run_hook("Edit", file_path="/project/src/foo.py")  # duplicate
        files = self._read_modified_files()
        assert "foo.py" in files
        assert "bar.py" in files

    def test_circuit_breaker_drift(self) -> None:
        """Drift detection blocks when too many unique files modified (medium=8)."""
        # Write state with 8 already-tracked files + 0 fix count
        files = ",".join([f"f{i}.py" for i in range(8)])
        self.STATE_FILE.write_text(f"0\n0\n0\n{files}\n")
        result = self._run_hook("Edit", file_path="/project/src/new_file.py")
        assert result.returncode == 2, f"Expected drift block, got {result.returncode}"
        assert "CIRCUIT BREAKER" in result.stderr
        assert "drift" in result.stderr.lower()


# ── risk-classifier hook tests ────────────────────────────────────────────
# Direct tests of risk-classifier.sh behavior.


@pytest.mark.flow
class TestRiskClassifierHook:
    """risk-classifier.sh reads task risk and enforces high-risk plan requirement."""

    HOOK = ROOT / ".claude" / "hooks" / "risk-classifier.sh"

    def _run_hook(self, tool_name: str, file_path: str = "", tasks_content: str = "") -> subprocess.CompletedProcess[str]:
        """Run the hook with simulated tool input and a temp tasks file."""
        payload = {"tool_name": tool_name, "tool_input": {}}
        if file_path:
            payload["tool_input"]["file_path"] = file_path

        env = dict(__import__("os").environ)
        if tasks_content:
            tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
            tmp.write(tasks_content)
            tmp.close()
            # Override CLAUDE_PROJECT_DIR to use a temp dir with .agent/tasks.jsonl
            tmpdir = tempfile.mkdtemp()
            import os, shutil
            os.makedirs(os.path.join(tmpdir, ".agent"), exist_ok=True)
            os.makedirs(os.path.join(tmpdir, ".claude", "plans"), exist_ok=True)
            shutil.copy(tmp.name, os.path.join(tmpdir, ".agent", "tasks.jsonl"))
            env["CLAUDE_PROJECT_DIR"] = tmpdir

        return subprocess.run(
            ["bash", str(self.HOOK)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=5,
            env=env,
            cwd=env.get("CLAUDE_PROJECT_DIR", str(ROOT)),
        )

    def test_allows_non_source_files(self) -> None:
        """Edits to docs/config are always allowed regardless of risk."""
        result = self._run_hook("Edit", file_path="/project/README.md")
        assert result.returncode == 0

    def test_allows_test_files(self) -> None:
        """Edits to test files are always allowed regardless of risk."""
        result = self._run_hook("Edit", file_path="/project/tests/test_foo.py")
        assert result.returncode == 0

    def test_allows_medium_risk_source_edits(self) -> None:
        """Medium-risk tasks allow source edits (plan-gate handles enforcement)."""
        tasks = '{"id":"test-001","taskType":"feature","status":"in_progress","summary":"Add new widget","risk":"medium"}\n'
        result = self._run_hook("Edit", file_path="/project/src/main.py", tasks_content=tasks)
        assert result.returncode == 0

    def test_allows_low_risk_source_edits(self) -> None:
        """Low-risk tasks always allow source edits."""
        tasks = '{"id":"test-002","taskType":"refactor","status":"in_progress","summary":"Fix lint issues","risk":"low"}\n'
        result = self._run_hook("Edit", file_path="/project/src/main.py", tasks_content=tasks)
        assert result.returncode == 0

    def test_blocks_high_risk_without_plan(self) -> None:
        """High-risk tasks block source edits when no plan exists."""
        tasks = '{"id":"test-003","taskType":"feature","status":"in_progress","summary":"Database migration","risk":"high"}\n'
        result = self._run_hook("Edit", file_path="/project/src/main.py", tasks_content=tasks)
        assert result.returncode == 2, f"Expected block (exit 2), got {result.returncode}"
        assert "BLOCKED" in result.stderr
        assert "High-risk" in result.stderr

    def test_infers_high_risk_from_keywords(self) -> None:
        """Tasks with security/migration keywords are inferred as high-risk."""
        tasks = '{"id":"test-004","taskType":"feature","status":"in_progress","summary":"Implement auth credentials migration"}\n'
        result = self._run_hook("Edit", file_path="/project/src/main.py", tasks_content=tasks)
        assert result.returncode == 2, f"Expected block (exit 2) for inferred high-risk, got {result.returncode}"


# ── blast-radius hook tests ──────────────────────────────────────────────
# Direct tests of blast-radius.sh behavior.


@pytest.mark.flow
class TestBlastRadiusHook:
    """blast-radius.sh enforces section scope on Edit/Write paths (tf-025)."""

    HOOK = ROOT / ".claude" / "hooks" / "blast-radius.sh"

    def _setup_project(self, tmpdir: str, section_name: str, owned_paths: list[str],
                       task_section: str | None = None, task_project: str = "testproj") -> str:
        """Create a temp project with section contract and tasks file."""
        import os
        # Create project structure
        proj_dir = os.path.join(tmpdir, "projects", task_project)
        sections_dir = os.path.join(proj_dir, "sections")
        os.makedirs(sections_dir, exist_ok=True)
        os.makedirs(os.path.join(tmpdir, ".agent"), exist_ok=True)

        # Write section contract
        owned_block = "\n".join(owned_paths)
        contract = f"# Section: {section_name}\n\n## Owned Paths\n```\n{owned_block}\n```\n\n## Invariants\n- none\n"
        with open(os.path.join(sections_dir, f"{section_name}.md"), "w") as f:
            f.write(contract)

        # Write tasks file
        task = {
            "id": "test-blast",
            "taskType": "feature",
            "status": "in_progress",
            "summary": "Test task for blast radius",
        }
        if task_section:
            task["section"] = task_section
            task["project"] = task_project
        with open(os.path.join(tmpdir, ".agent", "tasks.jsonl"), "w") as f:
            f.write(json.dumps(task) + "\n")

        return tmpdir

    def _run_hook(self, tool_name: str, file_path: str, project_dir: str) -> subprocess.CompletedProcess[str]:
        """Run blast-radius hook with given project dir."""
        payload = {"tool_name": tool_name, "tool_input": {"file_path": file_path}}
        env = dict(__import__("os").environ)
        env["CLAUDE_PROJECT_DIR"] = project_dir
        return subprocess.run(
            ["bash", str(self.HOOK)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=5,
            env=env,
            cwd=project_dir,
        )

    def test_allows_when_no_section_assigned(self) -> None:
        """Tasks without a section field are always allowed."""
        tmpdir = tempfile.mkdtemp()
        self._setup_project(tmpdir, "bridge", ["scue/bridge/"], task_section=None)
        result = self._run_hook("Edit", f"{tmpdir}/projects/testproj/scue/api/routes.py", tmpdir)
        assert result.returncode == 0

    def test_allows_file_in_owned_path(self) -> None:
        """File within section's owned paths is allowed."""
        tmpdir = tempfile.mkdtemp()
        self._setup_project(tmpdir, "bridge", ["scue/bridge/", "scue/network/"], task_section="bridge")
        result = self._run_hook("Edit", f"{tmpdir}/projects/testproj/scue/bridge/adapter.py", tmpdir)
        assert result.returncode == 0

    def test_blocks_file_outside_owned_path(self) -> None:
        """File outside section's owned paths is blocked."""
        tmpdir = tempfile.mkdtemp()
        self._setup_project(tmpdir, "bridge", ["scue/bridge/", "scue/network/"], task_section="bridge")
        result = self._run_hook("Edit", f"{tmpdir}/projects/testproj/scue/api/routes.py", tmpdir)
        assert result.returncode == 2, f"Expected block, got {result.returncode}: {result.stderr}"
        assert "BLOCKED" in result.stderr
        assert "outside section scope" in result.stderr

    def test_allows_non_source_files(self) -> None:
        """Non-source files (md, json, etc.) are always allowed."""
        tmpdir = tempfile.mkdtemp()
        self._setup_project(tmpdir, "bridge", ["scue/bridge/"], task_section="bridge")
        result = self._run_hook("Edit", f"{tmpdir}/projects/testproj/README.md", tmpdir)
        assert result.returncode == 0

    def test_allows_test_files(self) -> None:
        """Test files are always allowed regardless of section."""
        tmpdir = tempfile.mkdtemp()
        self._setup_project(tmpdir, "bridge", ["scue/bridge/"], task_section="bridge")
        result = self._run_hook("Edit", f"{tmpdir}/projects/testproj/tests/test_api.py", tmpdir)
        assert result.returncode == 0


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
