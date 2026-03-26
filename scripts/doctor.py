#!/usr/bin/env python3
"""doctor.py — THE_FACTORY environment health checker.

Validates that the workspace is correctly set up for both standalone
(pipeline-only) and portfolio (with project repos) modes.

Usage:
    python scripts/doctor.py          # run all checks
    python scripts/doctor.py --fix    # attempt auto-fixes where possible

Exit codes:
    0 — all checks pass
    1 — one or more checks failed
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── Check definitions ────────────────────────────────────────────────────

REQUIRED_PYTHON = (3, 11)

REQUIRED_DIRS = [
    ".agent",
    ".claude/hooks",
    ".claude/skills",
    "evals",
    "scripts",
    "skills",
    "templates",
]

REQUIRED_FILES = [
    "CLAUDE.md",
    "pyproject.toml",
    ".claude/settings.json",
    ".agent/tasks.jsonl",
    ".agent/runs.jsonl",
]

OPTIONAL_ENV_VARS = [
    ("LANGFUSE_PUBLIC_KEY", "Langfuse observability"),
    ("LANGFUSE_SECRET_KEY", "Langfuse observability"),
    ("LANGFUSE_BASE_URL", "Langfuse observability"),
]

PORTFOLIO_PROJECTS = [
    "projects/DjTools/scue",
    "projects/CRUCIBLE",
]


class Check:
    """A single health check result."""

    def __init__(self, name: str, passed: bool, message: str, fixable: bool = False):
        self.name = name
        self.passed = passed
        self.message = message
        self.fixable = fixable


def check_python_version() -> Check:
    """Verify Python version meets minimum."""
    v = sys.version_info
    ok = (v.major, v.minor) >= REQUIRED_PYTHON
    return Check(
        "Python version",
        ok,
        f"Python {v.major}.{v.minor}.{v.micro} ({'ok' if ok else f'need >={REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}'})",
    )


def check_venv_exists() -> Check:
    """Verify .venv exists and has a Python binary."""
    venv_python = ROOT / ".venv" / "bin" / "python"
    ok = venv_python.exists()
    return Check(
        "Virtual environment",
        ok,
        ".venv/bin/python exists" if ok else ".venv not found — run: python -m venv .venv && .venv/bin/pip install -e '.[all]'",
        fixable=True,
    )


def check_venv_has_pytest() -> Check:
    """Verify pytest is installed in the venv."""
    venv_python = ROOT / ".venv" / "bin" / "python"
    if not venv_python.exists():
        return Check("pytest installed", False, "skipped — no .venv")
    try:
        result = subprocess.run(
            [str(venv_python), "-c", "import pytest"],
            capture_output=True,
            timeout=10,
        )
        ok = result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        ok = False
    return Check(
        "pytest installed",
        ok,
        "pytest available in .venv" if ok else "pytest not installed — run: .venv/bin/pip install -e '.[evals]'",
        fixable=True,
    )


def check_required_dirs() -> list[Check]:
    """Verify required directories exist."""
    checks = []
    for d in REQUIRED_DIRS:
        path = ROOT / d
        ok = path.is_dir()
        checks.append(Check(
            f"Directory: {d}",
            ok,
            "exists" if ok else f"missing — create with: mkdir -p {d}",
            fixable=True,
        ))
    return checks


def check_required_files() -> list[Check]:
    """Verify required files exist."""
    checks = []
    for f in REQUIRED_FILES:
        path = ROOT / f
        ok = path.is_file()
        checks.append(Check(
            f"File: {f}",
            ok,
            "exists" if ok else "missing",
        ))
    return checks


def check_settings_json_valid() -> Check:
    """Verify .claude/settings.json is valid JSON."""
    path = ROOT / ".claude" / "settings.json"
    if not path.exists():
        return Check("settings.json valid", False, "file not found")
    try:
        json.loads(path.read_text())
        return Check("settings.json valid", True, "parses as valid JSON")
    except json.JSONDecodeError as e:
        return Check("settings.json valid", False, f"invalid JSON: {e}")


def check_hook_scripts_exist() -> list[Check]:
    """Verify all hook scripts referenced in settings.json exist."""
    path = ROOT / ".claude" / "settings.json"
    if not path.exists():
        return [Check("Hook scripts", False, "settings.json not found")]
    try:
        settings = json.loads(path.read_text())
    except json.JSONDecodeError:
        return [Check("Hook scripts", False, "settings.json is invalid JSON")]

    hooks_config = settings.get("hooks", {})
    seen_scripts: set[str] = set()
    checks = []

    for event_name, hook_groups in hooks_config.items():
        for group in hook_groups:
            # Hooks can be nested: group has "hooks" list or direct "command"
            hook_entries = group.get("hooks", [])
            if not hook_entries and "command" in group:
                hook_entries = [group]
            for entry in hook_entries:
                cmd = entry.get("command", "")
                # Extract script paths, resolving $CLAUDE_PROJECT_DIR to ROOT
                resolved = cmd.replace('"$CLAUDE_PROJECT_DIR"', str(ROOT))
                resolved = resolved.replace("$CLAUDE_PROJECT_DIR", str(ROOT))
                for token in resolved.split():
                    token = token.strip('"')
                    if token.endswith((".sh", ".py")) and os.path.sep in token:
                        # Deduplicate — same script may be referenced multiple times
                        rel = os.path.relpath(token, ROOT) if os.path.isabs(token) else token
                        if rel in seen_scripts:
                            continue
                        seen_scripts.add(rel)
                        script_path = Path(token) if os.path.isabs(token) else ROOT / token
                        ok = script_path.exists()
                        checks.append(Check(
                            f"Hook script: {rel}",
                            ok,
                            "exists" if ok else f"referenced in {event_name} but not found",
                        ))

    if not checks:
        checks.append(Check("Hook scripts", True, "no hook scripts referenced"))
    return checks


def check_env_vars() -> list[Check]:
    """Check optional environment variables."""
    checks = []
    for var, purpose in OPTIONAL_ENV_VARS:
        ok = var in os.environ
        checks.append(Check(
            f"Env: {var}",
            ok,
            f"set ({purpose})" if ok else f"not set — needed for {purpose} (optional)",
        ))
    return checks


def check_jsonl_files_valid() -> list[Check]:
    """Verify JSONL files have valid JSON on each line."""
    checks = []
    for name in ["tasks.jsonl", "runs.jsonl"]:
        path = ROOT / ".agent" / name
        if not path.exists():
            checks.append(Check(f"JSONL: {name}", False, "file not found"))
            continue
        lines = path.read_text().strip().split("\n")
        bad_lines = []
        for i, line in enumerate(lines, 1):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError:
                bad_lines.append(i)
        ok = len(bad_lines) == 0
        checks.append(Check(
            f"JSONL: {name}",
            ok,
            f"{len(lines)} valid entries" if ok else f"invalid JSON on lines: {bad_lines[:5]}",
        ))
    return checks


def check_portfolio_repos() -> list[Check]:
    """Check for portfolio project repos (optional)."""
    checks = []
    any_present = False
    for proj in PORTFOLIO_PROJECTS:
        path = ROOT / proj
        ok = path.is_dir()
        if ok:
            any_present = True
        checks.append(Check(
            f"Project: {proj}",
            ok,
            "present" if ok else "not found (portfolio mode only)",
        ))
    if not any_present:
        checks.append(Check(
            "Portfolio mode",
            True,
            "no project repos found — running in standalone mode (this is fine)",
        ))
    return checks


def check_git_repo() -> Check:
    """Verify we're in a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            timeout=5,
        )
        ok = result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        ok = False
    return Check("Git repository", ok, "inside git repo" if ok else "not a git repository")


# ── Runner ───────────────────────────────────────────────────────────────


def run_all_checks() -> list[Check]:
    """Run all health checks and return results."""
    checks: list[Check] = []
    checks.append(check_python_version())
    checks.append(check_git_repo())
    checks.append(check_venv_exists())
    checks.append(check_venv_has_pytest())
    checks.extend(check_required_dirs())
    checks.extend(check_required_files())
    checks.append(check_settings_json_valid())
    checks.extend(check_hook_scripts_exist())
    checks.extend(check_jsonl_files_valid())
    checks.extend(check_env_vars())
    checks.extend(check_portfolio_repos())
    return checks


def print_results(checks: list[Check]) -> int:
    """Print check results and return exit code."""
    passed = sum(1 for c in checks if c.passed)
    failed = [c for c in checks if not c.passed]

    # Separate required failures from optional (env vars, portfolio)
    required_failures = [c for c in failed if not c.name.startswith(("Env:", "Project:", "Portfolio"))]
    optional_warnings = [c for c in failed if c.name.startswith(("Env:", "Project:", "Portfolio"))]

    print(f"\n{'='*60}")
    print(f"  THE_FACTORY Doctor — Environment Health Check")
    print(f"{'='*60}\n")

    for check in checks:
        icon = "PASS" if check.passed else "WARN" if check.name.startswith(("Env:", "Project:", "Portfolio")) else "FAIL"
        print(f"  [{icon}] {check.name}: {check.message}")

    print(f"\n{'─'*60}")
    print(f"  {passed}/{len(checks)} checks passed", end="")
    if required_failures:
        print(f" | {len(required_failures)} required failures")
    elif optional_warnings:
        print(f" | {len(optional_warnings)} optional warnings")
    else:
        print(" | all clear")
    print(f"{'─'*60}\n")

    if required_failures:
        print("  Required fixes:")
        for c in required_failures:
            print(f"    - {c.name}: {c.message}")
        print()

    return 1 if required_failures else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="THE_FACTORY environment health checker")
    parser.add_argument("--fix", action="store_true", help="attempt auto-fixes where possible")
    parser.add_argument("--json", action="store_true", help="output results as JSON")
    args = parser.parse_args()

    checks = run_all_checks()

    if args.json:
        results = [
            {"name": c.name, "passed": c.passed, "message": c.message}
            for c in checks
        ]
        print(json.dumps({"checks": results, "passed": sum(1 for c in checks if c.passed), "total": len(checks)}, indent=2))
        sys.exit(0 if all(c.passed or c.name.startswith(("Env:", "Project:", "Portfolio")) for c in checks) else 1)

    exit_code = print_results(checks)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
