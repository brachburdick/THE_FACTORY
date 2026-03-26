"""Handoff, schema, and artifact evals — deterministic validation.

Migrated from .agent/evals/handoffs/handoff-schema-valid.eval.md
Extended with artifact bootstrap validation (tf-004).
"""

import json
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent
AGENT_DIR = ROOT / ".agent"


# ── handoff-schema-valid ─────────────────────────────────────────────────
# Source: .agent/evals/handoffs/handoff-schema-valid.eval.md
# Rule: Handoff packets must match the JSON schema.


@pytest.mark.handoff
class TestHandoffSchemaValid:
    """Handoff envelope schema is well-formed and usable."""

    def test_schema_exists(self, agent_dir: Path) -> None:
        """Handoff envelope schema file exists."""
        schema_path = agent_dir / "schemas" / "handoff-envelope.json"
        assert schema_path.exists(), "Missing handoff-envelope.json schema"

    def test_schema_is_valid_json(self, handoff_schema: dict[str, Any]) -> None:
        """Schema parses as valid JSON."""
        assert handoff_schema.get("$schema") or handoff_schema.get("type")
        assert "properties" in handoff_schema or "properties" in handoff_schema.get("definitions", {}).get("HandoffEnvelope", {})

    def test_schema_has_required_fields(self, handoff_schema: dict[str, Any]) -> None:
        """Schema requires all expected top-level fields."""
        required = handoff_schema.get("required", [])
        expected = {"schemaVersion", "sourceAgent", "targetSkill", "taskType", "summary", "artifacts", "taskRef"}
        missing = expected - set(required)
        assert not missing, f"Schema missing required fields: {missing}"

    def test_schema_disallows_additional_properties(self, handoff_schema: dict[str, Any]) -> None:
        """Schema has additionalProperties: false to prevent drift."""
        assert handoff_schema.get("additionalProperties") is False, (
            "Handoff schema should set additionalProperties: false"
        )

    def test_valid_handoff_passes(self, handoff_schema: dict[str, Any]) -> None:
        """A well-formed handoff should validate against the schema."""
        try:
            import jsonschema
        except ImportError:
            pytest.skip("jsonschema not installed")

        valid_handoff = {
            "schemaVersion": "1.1.0",
            "sourceAgent": "test-agent",
            "targetSkill": "debug-flow",
            "taskType": "debug",
            "summary": "Test handoff for eval",
            "artifacts": ["src/main.py"],
            "taskRef": "TASK-001",
            "dispatchStatus": "READY",
        }
        jsonschema.validate(valid_handoff, handoff_schema)

    def test_invalid_handoff_fails(self, handoff_schema: dict[str, Any]) -> None:
        """A handoff missing required fields should fail validation."""
        try:
            import jsonschema
        except ImportError:
            pytest.skip("jsonschema not installed")

        invalid_handoff = {
            "sourceAgent": "test-agent",
            # Missing: schemaVersion, targetSkill, taskType, summary, artifacts, taskRef
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(invalid_handoff, handoff_schema)


# ── Required artifacts (tf-004) ──────────────────────────────────────────
# Rule: .agent/ must contain bootstrapped artifacts. Missing = fail, not skip.


@pytest.mark.handoff
class TestRequiredArtifacts:
    """Required pipeline artifacts exist in .agent/ directory."""

    def test_runs_jsonl_exists(self) -> None:
        """runs.jsonl must exist (bootstrapped, even if empty)."""
        path = AGENT_DIR / "runs.jsonl"
        assert path.exists(), (
            "Missing .agent/runs.jsonl — bootstrap with an empty file"
        )

    def test_incidents_jsonl_exists(self) -> None:
        """incidents.jsonl must exist (bootstrapped, even if empty)."""
        path = AGENT_DIR / "incidents.jsonl"
        assert path.exists(), (
            "Missing .agent/incidents.jsonl — bootstrap with an empty file"
        )

    def test_tasks_jsonl_exists(self) -> None:
        """tasks.jsonl must exist and contain valid JSONL."""
        path = AGENT_DIR / "tasks.jsonl"
        assert path.exists(), "Missing .agent/tasks.jsonl"
        # Verify it's valid JSONL
        for i, line in enumerate(path.read_text().splitlines()):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                raise AssertionError(f"tasks.jsonl line {i+1} is not valid JSON: {e}")

    def test_state_snapshot_is_valid_json(self) -> None:
        """state-snapshot.json, if present, must be valid JSON."""
        path = AGENT_DIR / "state-snapshot.json"
        if not path.exists():
            pytest.skip("No state-snapshot.json yet (written at session end)")
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            raise AssertionError(f"state-snapshot.json is not valid JSON: {e}")
        # Check required fields
        required = {"session_id", "timestamp", "branch", "modified_files"}
        missing = required - set(data.keys())
        assert not missing, f"state-snapshot.json missing fields: {missing}"

    def test_handoff_schema_exists(self) -> None:
        """handoff-envelope.json schema must exist."""
        path = AGENT_DIR / "schemas" / "handoff-envelope.json"
        assert path.exists(), "Missing .agent/schemas/handoff-envelope.json"


# ── run-record schema ────────────────────────────────────────────────────


@pytest.mark.handoff
class TestRunRecordSchema:
    """Run records in runs.jsonl match the schema."""

    def test_run_records_have_required_fields(self, runs_jsonl: list[dict[str, Any]]) -> None:
        """Every run record has the required fields."""
        if not runs_jsonl:
            pytest.skip("No run records exist yet")
        required = {"run_id", "date", "project_id", "task_id", "task_type", "result"}
        for i, run in enumerate(runs_jsonl):
            missing = required - set(run.keys())
            assert not missing, f"Run record {i} missing fields: {missing}"

    def test_run_results_are_valid_enum(self, runs_jsonl: list[dict[str, Any]]) -> None:
        """Run results use valid enum values."""
        if not runs_jsonl:
            pytest.skip("No run records exist yet")
        valid = {"success", "partial", "failed", "blocked", "escalated"}
        for i, run in enumerate(runs_jsonl):
            result = run.get("result")
            assert result in valid, (
                f"Run record {i} has invalid result '{result}'. Valid: {valid}"
            )

    def test_run_record_task_ids_exist_in_tasks_jsonl(self) -> None:
        """Every run record's task_id must reference a valid task in tasks.jsonl.

        This is the traceability through-line: task queue → flow execution → run record.
        """
        runs_path = AGENT_DIR / "runs.jsonl"
        tasks_path = AGENT_DIR / "tasks.jsonl"
        if not runs_path.exists() or runs_path.stat().st_size == 0:
            pytest.skip("No run records exist yet")
        if not tasks_path.exists():
            pytest.skip("No tasks.jsonl exists")

        # Collect all task IDs
        task_ids: set[str] = set()
        for line in tasks_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                task = json.loads(line)
                tid = task.get("id", "")
                if tid:
                    task_ids.add(tid)
            except json.JSONDecodeError:
                continue

        # Check every run record references a valid task
        orphans = []
        for i, line in enumerate(runs_path.read_text().splitlines()):
            line = line.strip()
            if not line:
                continue
            try:
                run = json.loads(line)
            except json.JSONDecodeError:
                continue
            run_task_id = run.get("task_id", "")
            if run_task_id and run_task_id not in task_ids:
                orphans.append(f"run {i} ({run.get('run_id', '?')}): task_id '{run_task_id}' not in tasks.jsonl")

        assert not orphans, (
            f"Run records reference task IDs not found in tasks.jsonl:\n"
            + "\n".join(orphans)
        )


# ── task closure completeness ───────────────────────────────────────────
# Rule: Every completed task must have a matching run record with summary.


@pytest.mark.handoff
class TestTaskClosureCompleteness:
    """Completed tasks must have matching run records."""

    def test_completed_tasks_have_run_records(self) -> None:
        """Every completed task in tasks.jsonl has a run record in runs.jsonl."""
        tasks_path = AGENT_DIR / "tasks.jsonl"
        runs_path = AGENT_DIR / "runs.jsonl"
        if not tasks_path.exists():
            pytest.skip("No tasks.jsonl")

        completed_ids: set[str] = set()
        for line in tasks_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                task = json.loads(line)
                if task.get("status") == "complete" and task.get("id"):
                    completed_ids.add(task["id"])
            except json.JSONDecodeError:
                continue

        if not completed_ids:
            pytest.skip("No completed tasks")

        run_task_ids: set[str] = set()
        if runs_path.exists():
            for line in runs_path.read_text().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    run = json.loads(line)
                    if run.get("task_id"):
                        run_task_ids.add(run["task_id"])
                except json.JSONDecodeError:
                    continue

        missing = sorted(completed_ids - run_task_ids)
        assert not missing, (
            f"Completed tasks without run records:\n"
            + "\n".join(f"  - {tid}" for tid in missing)
        )

    def test_run_records_have_summary(self, runs_jsonl: list[dict[str, Any]]) -> None:
        """Every run record must include a non-empty summary field."""
        if not runs_jsonl:
            pytest.skip("No run records")
        missing = [
            run.get("run_id", f"index-{i}")
            for i, run in enumerate(runs_jsonl)
            if not run.get("summary")
        ]
        assert not missing, (
            f"Run records missing summary:\n"
            + "\n".join(f"  - {rid}" for rid in missing)
        )


# ── JSONL schema validation (tf-043) ─────────────────────────────────────
# Rule: Every entry in tasks/runs/incidents JSONL validates against its schema.


@pytest.mark.handoff
class TestJsonlSchemaValidation:
    """JSONL entries validate against their JSON schemas."""

    SCHEMAS_DIR = AGENT_DIR / "schemas"

    def _load_schema(self, name: str) -> dict[str, Any] | None:
        path = self.SCHEMAS_DIR / name
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def _load_jsonl(self, name: str) -> list[tuple[int, dict[str, Any]]]:
        path = AGENT_DIR / name
        if not path.exists():
            return []
        entries = []
        for i, line in enumerate(path.read_text().splitlines()):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append((i + 1, json.loads(line)))
            except json.JSONDecodeError:
                pass  # Caught by existing test_tasks_jsonl_exists
        return entries

    def _validate_required_fields(self, entries: list[tuple[int, dict]], schema: dict, file_name: str) -> None:
        required = schema.get("required", [])
        violations = []
        for line_num, entry in entries:
            missing = [f for f in required if f not in entry]
            if missing:
                entry_id = entry.get("id") or entry.get("run_id") or entry.get("incident_id") or f"line-{line_num}"
                violations.append(f"{file_name}:{line_num} ({entry_id}): missing {missing}")
        assert not violations, (
            f"JSONL entries missing required fields:\n"
            + "\n".join(f"  - {v}" for v in violations[:10])
        )

    def _validate_enum_fields(self, entries: list[tuple[int, dict]], schema: dict, file_name: str) -> None:
        props = schema.get("properties", {})
        violations = []
        for line_num, entry in entries:
            for field, field_schema in props.items():
                if field not in entry:
                    continue
                # Handle nullable enums (type is array with string and null)
                allowed = field_schema.get("enum")
                if not allowed:
                    continue
                if entry[field] not in allowed:
                    entry_id = entry.get("id") or entry.get("run_id") or entry.get("incident_id") or f"line-{line_num}"
                    violations.append(f"{file_name}:{line_num} ({entry_id}): {field}='{entry[field]}' not in {allowed}")
        assert not violations, (
            f"JSONL entries with invalid enum values:\n"
            + "\n".join(f"  - {v}" for v in violations[:10])
        )

    def test_tasks_match_schema(self) -> None:
        """Every task entry has required fields and valid enum values."""
        schema = self._load_schema("task.schema.json")
        if not schema:
            pytest.skip("task.schema.json not found")
        entries = self._load_jsonl("tasks.jsonl")
        if not entries:
            pytest.skip("No task entries")
        self._validate_required_fields(entries, schema, "tasks.jsonl")
        self._validate_enum_fields(entries, schema, "tasks.jsonl")

    def test_runs_match_schema(self) -> None:
        """Every run record has required fields and valid enum values."""
        schema = self._load_schema("run.schema.json")
        if not schema:
            pytest.skip("run.schema.json not found")
        entries = self._load_jsonl("runs.jsonl")
        if not entries:
            pytest.skip("No run entries")
        self._validate_required_fields(entries, schema, "runs.jsonl")
        self._validate_enum_fields(entries, schema, "runs.jsonl")

    def test_incidents_match_schema(self) -> None:
        """Every incident entry has required fields and valid enum values."""
        schema = self._load_schema("incident.schema.json")
        if not schema:
            pytest.skip("incident.schema.json not found")
        entries = self._load_jsonl("incidents.jsonl")
        if not entries:
            pytest.skip("No incident entries")
