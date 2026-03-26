"""Convention evals — deterministic code checks.

Migrated from .agent/evals/conventions/*.eval.md

SCUE-specific tests are marked with @scue_available and will be skipped
when the SCUE project directory is absent (e.g., on a clean pipeline-only checkout).

Pipeline-level tests (no project dependency) are at the top of this file.
"""

import json
import os
import re
import stat
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


# ── pipeline-level: skill frontmatter ────────────────────────────────────
# Rule: Every SKILL.md must have YAML frontmatter with name and description.


@pytest.mark.convention
class TestAllSkillsHaveFrontmatter:
    """Every SKILL.md has YAML frontmatter with name and description."""

    def _find_all_skills(self) -> list[Path]:
        """Find all SKILL.md files across pipeline and project skills."""
        skills = []
        for pattern in ["skills/**/SKILL.md", ".claude/skills/**/SKILL.md"]:
            skills.extend(ROOT.glob(pattern))
        return skills

    def test_all_skills_have_frontmatter(self) -> None:
        """Every SKILL.md starts with --- delimited YAML frontmatter."""
        skills = self._find_all_skills()
        assert skills, "No SKILL.md files found"
        missing = []
        for skill in skills:
            text = skill.read_text()
            if not text.startswith("---"):
                missing.append(str(skill.relative_to(ROOT)))
        assert not missing, (
            f"SKILL.md files missing YAML frontmatter:\n"
            + "\n".join(f"  - {m}" for m in missing)
        )

    def test_frontmatter_has_name_and_description(self) -> None:
        """Frontmatter contains name and description fields."""
        skills = self._find_all_skills()
        violations = []
        for skill in skills:
            text = skill.read_text()
            if not text.startswith("---"):
                continue  # Caught by test above
            # Extract frontmatter between first two ---
            parts = text.split("---", 2)
            if len(parts) < 3:
                violations.append(f"{skill.relative_to(ROOT)}: malformed frontmatter (no closing ---)")
                continue
            fm = parts[1]
            if "name:" not in fm:
                violations.append(f"{skill.relative_to(ROOT)}: missing 'name' field")
            if "description:" not in fm:
                violations.append(f"{skill.relative_to(ROOT)}: missing 'description' field")
        assert not violations, (
            f"SKILL.md frontmatter issues:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )


# ── pipeline-level: native hooks settings valid ─────────────────────────
# Rule: settings.json is valid JSON and all referenced hook scripts exist.


@pytest.mark.convention
class TestNativeHooksSettingsValid:
    """settings.json is well-formed and all hook scripts are present and executable."""

    SETTINGS_PATH = ROOT / ".claude" / "settings.json"

    def test_settings_json_parses(self) -> None:
        """settings.json is valid JSON."""
        assert self.SETTINGS_PATH.exists(), ".claude/settings.json not found"
        text = self.SETTINGS_PATH.read_text()
        try:
            json.loads(text)
        except json.JSONDecodeError as e:
            pytest.fail(f".claude/settings.json is invalid JSON: {e}")

    def test_all_hook_scripts_exist(self) -> None:
        """Every script referenced in hook commands exists on disk."""
        settings = json.loads(self.SETTINGS_PATH.read_text())
        hooks_config = settings.get("hooks", {})
        missing = []
        for event_name, hook_groups in hooks_config.items():
            for group in hook_groups:
                for hook in group.get("hooks", []):
                    cmd = hook.get("command", "")
                    # Extract script paths from the command string
                    # Pattern: "$CLAUDE_PROJECT_DIR"/path/to/script
                    # Replace the env var with the actual root
                    resolved = cmd.replace('"$CLAUDE_PROJECT_DIR"/', str(ROOT) + "/")
                    resolved = resolved.replace("$CLAUDE_PROJECT_DIR/", str(ROOT) + "/")
                    # The command may have multiple parts (e.g., python script.py)
                    # Check each path-like token
                    for token in resolved.split():
                        if token.startswith(str(ROOT)) and not token.startswith(str(ROOT) + "/.venv"):
                            path = Path(token)
                            if not path.exists():
                                missing.append(f"{event_name}: {path.relative_to(ROOT)}")
        assert not missing, (
            f"Hook scripts referenced in settings.json but not found:\n"
            + "\n".join(f"  - {m}" for m in missing)
        )

    def test_hook_scripts_executable(self) -> None:
        """Shell hook scripts (.sh) are executable."""
        settings = json.loads(self.SETTINGS_PATH.read_text())
        hooks_config = settings.get("hooks", {})
        not_executable = []
        for event_name, hook_groups in hooks_config.items():
            for group in hook_groups:
                for hook in group.get("hooks", []):
                    cmd = hook.get("command", "")
                    resolved = cmd.replace('"$CLAUDE_PROJECT_DIR"/', str(ROOT) + "/")
                    resolved = resolved.replace("$CLAUDE_PROJECT_DIR/", str(ROOT) + "/")
                    for token in resolved.split():
                        if token.endswith(".sh") and token.startswith(str(ROOT)):
                            path = Path(token)
                            if path.exists() and not os.access(path, os.X_OK):
                                not_executable.append(f"{event_name}: {path.relative_to(ROOT)}")
        assert not not_executable, (
            f"Hook scripts not executable:\n"
            + "\n".join(f"  - {m}" for m in not_executable)
        )
SCUE_ROOT = ROOT / "projects" / "DjTools" / "scue"

scue_available = pytest.mark.skipif(
    not SCUE_ROOT.exists(),
    reason="SCUE project not available (projects/ may be gitignored or absent)",
)


# ── uses-dataclasses ─────────────────────────────────────────────────────
# Source: .agent/evals/conventions/uses-dataclasses.eval.md
# Rule: Python data containers should use @dataclass, not plain dicts or raw classes.


@pytest.mark.convention
@scue_available
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
@scue_available
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
@scue_available
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
@scue_available
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


# ── section-boundary-enforcement ─────────────────────────────────────────
# Rule: Section contracts are respected — no forbidden cross-section imports.


@pytest.mark.convention
@scue_available
class TestSectionBoundaries:
    """Section boundary contracts are mechanically enforced."""

    def test_bridge_does_not_import_analysis_or_api(self, scue_python_files: list[Path]) -> None:
        """Bridge section must not import from layer1, layer2-4, or api."""
        forbidden = ("scue.layer1", "scue.layer2", "scue.layer3", "scue.layer4", "scue.api")
        violations = []
        for f in scue_python_files:
            rel = str(f)
            if "/bridge/" not in rel and "/network/" not in rel:
                continue
            text = f.read_text()
            for i, line in enumerate(text.splitlines(), 1):
                stripped = line.strip()
                if not stripped.startswith(("import ", "from ")):
                    continue
                for mod in forbidden:
                    if mod in stripped:
                        violations.append(f"{f.name}:{i} — {stripped}")
        assert not violations, (
            f"Bridge section imports from forbidden modules:\n"
            + "\n".join(violations)
        )

    def test_analysis_does_not_import_api_or_upper_layers(self, scue_python_files: list[Path]) -> None:
        """Analysis section must not import from layer2-4 or api."""
        forbidden = ("scue.layer2", "scue.layer3", "scue.layer4", "scue.api")
        violations = []
        for f in scue_python_files:
            rel = str(f)
            if "/layer1/" not in rel:
                continue
            text = f.read_text()
            for i, line in enumerate(text.splitlines(), 1):
                stripped = line.strip()
                if not stripped.startswith(("import ", "from ")):
                    continue
                for mod in forbidden:
                    if mod in stripped:
                        violations.append(f"{f.name}:{i} — {stripped}")
        assert not violations, (
            f"Analysis section imports from forbidden modules:\n"
            + "\n".join(violations)
        )

    def test_pipeline_layers_respect_downward_only(self, scue_python_files: list[Path]) -> None:
        """Pipeline layers (2/3/4) import only from the layer directly below."""
        violations = []
        layer_forbidden = {
            "layer2": ("scue.layer3", "scue.layer4", "scue.api", "scue.bridge"),
            "layer3": ("scue.layer4", "scue.api", "scue.bridge", "scue.layer1"),
            "layer4": ("scue.api", "scue.bridge", "scue.layer1", "scue.layer2"),
        }
        for f in scue_python_files:
            rel = str(f)
            for layer, forbidden in layer_forbidden.items():
                if f"/{layer}/" not in rel:
                    continue
                text = f.read_text()
                for i, line in enumerate(text.splitlines(), 1):
                    stripped = line.strip()
                    if not stripped.startswith(("import ", "from ")):
                        continue
                    for mod in forbidden:
                        if mod in stripped:
                            violations.append(f"{f.name}:{i} ({layer}) — {stripped}")
        assert not violations, (
            f"Pipeline layer imports from forbidden modules:\n"
            + "\n".join(violations)
        )

    def test_strata_does_not_import_forbidden(self, scue_python_files: list[Path]) -> None:
        """Strata section must not import from tracking, enrichment, api, or upper layers."""
        # Strata may import from: layer1.models, layer1.storage, layer1.detectors.events, bridge.adapter
        forbidden = ("scue.api", "scue.layer2", "scue.layer3", "scue.layer4", "scue.config")
        # Also forbidden: other layer1 subsystems (but not models/storage/detectors)
        forbidden_layer1 = ("layer1.tracking", "layer1.analysis", "layer1.enrichment",
                            "layer1.cursor", "layer1.fingerprint", "layer1.reanalysis",
                            "layer1.usb_scanner", "layer1.divergence")
        violations = []
        for f in scue_python_files:
            rel = str(f)
            if "/layer1/strata/" not in rel:
                continue
            text = f.read_text()
            for i, line in enumerate(text.splitlines(), 1):
                stripped = line.strip()
                if not stripped.startswith(("import ", "from ")):
                    continue
                for mod in forbidden:
                    if mod in stripped:
                        violations.append(f"{f.name}:{i} — {stripped}")
                for mod in forbidden_layer1:
                    if mod in stripped:
                        violations.append(f"{f.name}:{i} — {stripped}")
        assert not violations, (
            f"Strata section imports from forbidden modules:\n"
            + "\n".join(violations)
        )

    def test_frontend_no_python_imports(self) -> None:
        """Frontend section has no Python imports (different runtime)."""
        fe_root = SCUE_ROOT / "frontend" / "src"
        if not fe_root.exists():
            pytest.skip("Frontend not present")
        # Check for any .py files in frontend/ (should be zero)
        py_files = list(fe_root.rglob("*.py"))
        assert not py_files, (
            f"Python files found in frontend/src/:\n"
            + "\n".join(str(f) for f in py_files)
        )

    def test_section_contracts_exist(self) -> None:
        """Each defined section has a contract file."""
        sections_dir = SCUE_ROOT / "sections"
        if not sections_dir.exists():
            pytest.skip("No sections directory")
        required = ["bridge.md", "analysis.md", "strata.md", "pipeline.md", "server.md", "frontend.md"]
        missing = [s for s in required if not (sections_dir / s).exists()]
        assert not missing, f"Missing section contracts: {missing}"

    def test_sections_map_exists(self) -> None:
        """SECTIONS.md exists and defines the section map."""
        sections_md = SCUE_ROOT / "sections" / "SECTIONS.md"
        assert sections_md.exists(), "Missing sections/SECTIONS.md"
        text = sections_md.read_text()
        assert "Coupling Map" in text, "SECTIONS.md missing coupling map"
        assert "Parallelization Rules" in text, "SECTIONS.md missing parallelization rules"
        assert "Three-Pass Review" in text, "SECTIONS.md missing review model"


# ── section-file-coverage ────────────────────────────────────────────────
# Rule: Every source file belongs to exactly one section.


@pytest.mark.convention
@scue_available
class TestSectionFileCoverage:
    """Every source file is claimed by exactly one section."""

    # Section ownership: path prefix → section name
    # Order matters: longer prefixes checked first (strata before layer1)
    SECTION_PATHS = [
        ("scue/layer1/strata/", "strata"),
        ("scue/bridge/", "bridge"),
        ("scue/network/", "bridge"),
        ("scue/layer1/", "analysis"),
        ("scue/layer2/", "pipeline"),
        ("scue/layer3/", "pipeline"),
        ("scue/layer4/", "pipeline"),
        ("scue/api/", "server"),
        ("scue/config/", "server"),
        ("scue/main.py", "server"),
        ("scue/project/", "server"),
        ("scue/ui/", "server"),
        ("frontend/", "frontend"),
    ]

    def test_all_python_source_claimed(self, scue_python_files: list[Path]) -> None:
        """Every Python source file in scue/ belongs to a section."""
        unclaimed = []
        for f in scue_python_files:
            rel = str(f.relative_to(SCUE_ROOT))
            # Skip test files, reference/poc, tools, scripts, hooks, top-level __init__
            if rel.startswith("tests/") or "_reference/" in rel or rel.startswith("tools/"):
                continue
            if rel.startswith(".claude/") or rel == "scue/__init__.py":
                continue
            claimed = any(rel.startswith(prefix) for prefix, _ in self.SECTION_PATHS)
            if not claimed:
                unclaimed.append(rel)
        assert not unclaimed, (
            f"Python files not claimed by any section:\n"
            + "\n".join(f"  - {f}" for f in unclaimed)
        )

    def test_all_typescript_source_claimed(self, scue_ts_files: list[Path]) -> None:
        """Every TypeScript source file in frontend/ belongs to the frontend section."""
        unclaimed = []
        for f in scue_ts_files:
            rel = str(f.relative_to(SCUE_ROOT))
            if not rel.startswith("frontend/"):
                unclaimed.append(rel)
        assert not unclaimed, (
            f"TypeScript files outside frontend/ section:\n"
            + "\n".join(f"  - {f}" for f in unclaimed)
        )


# ── venv-python ──────────────────────────────────────────────────────────
# Source: .agent/evals/conventions/venv-python.eval.md


@pytest.mark.convention
@scue_available
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
@scue_available
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
