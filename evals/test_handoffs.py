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
