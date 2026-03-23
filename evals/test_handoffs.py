"""Handoff and schema evals — deterministic validation.

Migrated from .agent/evals/handoffs/handoff-schema-valid.eval.md
"""

import json
from pathlib import Path
from typing import Any

import pytest


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
