"""Convention evals — deterministic code checks.

Migrated from .agent/evals/conventions/*.eval.md
These run against the actual codebase, not session transcripts.
"""

import re
from pathlib import Path

import pytest


# ── uses-dataclasses ─────────────────────────────────────────────────────
# Source: .agent/evals/conventions/uses-dataclasses.eval.md
# Rule: Python data containers should use @dataclass, not plain dicts or raw classes.


@pytest.mark.convention
class TestUsesDataclasses:
    """Config objects and data containers use @dataclass."""

    def test_no_raw_dict_config_objects(self, scue_python_files: list[Path]) -> None:
        """No files define config as a plain dict literal assigned to a module-level var."""
        violations = []
        pattern = re.compile(r"^[A-Z_]+\s*[:=]\s*\{", re.MULTILINE)
        for f in scue_python_files:
            text = f.read_text()
            # Skip __init__.py and config files that legitimately use dicts
            if f.name in ("__init__.py", "conftest.py"):
                continue
            # Look for module-level UPPER_CASE dict assignments that look like config
            for match in pattern.finditer(text):
                line = text[: match.start()].count("\n") + 1
                # Allow dict literals in non-config contexts (e.g., mappings, lookups)
                var_name = match.group().split("=")[0].split(":")[0].strip()
                if "CONFIG" in var_name or "SETTINGS" in var_name or "OPTIONS" in var_name:
                    violations.append(f"{f.name}:{line} — {var_name} should be a @dataclass")
        assert not violations, f"Dict-based config objects found:\n" + "\n".join(violations)

    def test_model_files_use_dataclass(self, scue_python_files: list[Path]) -> None:
        """Files named 'models.py' should use @dataclass or Pydantic BaseModel."""
        for f in scue_python_files:
            # Only check files named exactly 'models.py', not 'flow_model.py' (algorithms)
            if f.name != "models.py":
                continue
            # Skip reference/poc directories
            if "_reference" in str(f):
                continue
            text = f.read_text()
            has_dataclass = "@dataclass" in text or "from dataclasses import" in text
            has_pydantic = "BaseModel" in text
            assert has_dataclass or has_pydantic, (
                f"{f} defines models but doesn't use @dataclass or BaseModel"
            )


# ── no-print-statements ──────────────────────────────────────────────────
# Source: .agent/evals/conventions/no-print-statements.eval.md
# Rule: Use logging module, not print().


@pytest.mark.convention
class TestNoPrintStatements:
    """Source code uses logging, not print()."""

    def test_no_print_in_source(self, scue_python_files: list[Path]) -> None:
        """No print() calls in SCUE Python source files."""
        violations = []
        # Match print( at start of line or after whitespace, excluding comments
        pattern = re.compile(r"^\s*print\s*\(", re.MULTILINE)
        for f in scue_python_files:
            if f.name.startswith("test_"):
                continue  # print in tests is fine
            # CLI tools, scripts, and eval harnesses legitimately use print
            rel = str(f)
            if "/tools/" in rel or "/scripts/" in rel or "eval_" in f.name:
                continue
            # Standalone debug/diagnostic scripts
            if f.name in ("prodjlink.py", "fix-python-cmd.py"):
                continue
            text = f.read_text()
            for match in pattern.finditer(text):
                line_num = text[: match.start()].count("\n") + 1
                # Check it's not inside a comment
                line = text.splitlines()[line_num - 1].strip()
                if line.startswith("#"):
                    continue
                violations.append(f"{f.name}:{line_num}")
        assert not violations, (
            f"print() found in source files (use logging module):\n"
            + "\n".join(violations)
        )


# ── type-hints-required ──────────────────────────────────────────────────
# Source: .agent/evals/conventions/type-hints-required.eval.md
# Rule: All function signatures should have type hints.


@pytest.mark.convention
class TestTypeHintsRequired:
    """Function signatures include type hints."""

    def test_no_any_in_typescript(self, scue_ts_files: list[Path]) -> None:
        """No explicit 'any' type annotations in TypeScript files."""
        violations = []
        # Match ': any' or '<any>' but not 'any' in strings or comments
        pattern = re.compile(r":\s*any\b|<any>", re.IGNORECASE)
        for f in scue_ts_files:
            text = f.read_text()
            for i, line in enumerate(text.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("//") or stripped.startswith("*"):
                    continue
                if pattern.search(line):
                    violations.append(f"{f.name}:{i} — {stripped[:80]}")
        assert not violations, (
            f"'any' type found in TypeScript (use specific types):\n"
            + "\n".join(violations[:10])
        )


# ── no-cross-layer-imports ───────────────────────────────────────────────
# Source: .agent/evals/conventions/no-cross-layer-imports.eval.md
# Rule: SCUE layers only import through documented contracts.


@pytest.mark.convention
class TestNoCrossLayerImports:
    """Layer boundaries enforced — no direct cross-layer imports."""

    LAYER_MAP = {
        "layer1": 1,
        "layer2": 2,
        "layer3": 3,
        "layer4": 4,
        "bridge": 0,
    }

    def test_no_upward_imports(self, scue_python_files: list[Path]) -> None:
        """Higher layers should not be imported by lower layers."""
        violations = []
        for f in scue_python_files:
            # Determine which layer this file belongs to
            rel = str(f)
            file_layer = None
            for layer_name, layer_num in self.LAYER_MAP.items():
                if f"/{layer_name}/" in rel or f"\\{layer_name}\\" in rel:
                    file_layer = layer_num
                    break
            if file_layer is None:
                continue  # Not in a layer directory

            text = f.read_text()
            for line in text.splitlines():
                if not line.strip().startswith(("import ", "from ")):
                    continue
                for layer_name, layer_num in self.LAYER_MAP.items():
                    if layer_num > file_layer and f"scue.{layer_name}" in line:
                        violations.append(
                            f"{f.name} (layer {file_layer}) imports {layer_name} (layer {layer_num}): {line.strip()}"
                        )
        assert not violations, (
            f"Cross-layer import violations (lower imports higher):\n"
            + "\n".join(violations)
        )


# ── venv-python ──────────────────────────────────────────────────────────
# Source: .agent/evals/conventions/venv-python.eval.md
# Rule: Use .venv/bin/python, not bare python.
# Note: This is a session-transcript eval — checks agent behavior, not code.
# Converted to check: does SCUE have a .venv directory?


@pytest.mark.convention
class TestVenvPython:
    """SCUE project has a properly configured virtual environment."""

    def test_venv_exists(self, scue_root: Path) -> None:
        """SCUE has a .venv directory with python binary."""
        venv = scue_root / ".venv"
        assert venv.exists(), f"No .venv directory at {scue_root}"
        python = venv / "bin" / "python"
        assert python.exists(), f"No python binary in {venv / 'bin'}"


# ── beat-link-api-style-dispatch ─────────────────────────────────────────
# Source: .agent/evals/conventions/beat-link-api-style-dispatch.eval.md
# Rule: Branch on WaveformDetail.style before calling style-specific methods.


@pytest.mark.convention
class TestBeatLinkApiStyleDispatch:
    """Waveform rendering branches on style before calling style-specific methods."""

    def test_no_unconditional_three_band_calls(self, scue_ts_files: list[Path]) -> None:
        """No direct calls to segmentHeight with ThreeBandLayer without style check."""
        violations = []
        for f in scue_ts_files:
            if "waveform" not in f.name.lower() and "wave" not in f.name.lower():
                continue
            text = f.read_text()
            if "segmentHeight" not in text:
                continue
            # Check that there's a style check near any segmentHeight call
            if "segmentHeight" in text and ".style" not in text:
                violations.append(f"{f.name} — calls segmentHeight without checking .style")
        assert not violations, (
            f"Waveform files call segmentHeight without style dispatch:\n"
            + "\n".join(violations)
        )
