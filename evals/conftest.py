"""Shared fixtures for THE_FACTORY eval suite."""

import json
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCUE_ROOT = ROOT / "projects" / "DjTools" / "scue"
AGENT_DIR = ROOT / ".agent"


@pytest.fixture
def root() -> Path:
    return ROOT


@pytest.fixture
def scue_root() -> Path:
    return SCUE_ROOT


@pytest.fixture
def agent_dir() -> Path:
    return AGENT_DIR


@pytest.fixture
def scue_python_files(scue_root: Path) -> list[Path]:
    """All Python source files in SCUE (excluding tests and venv)."""
    files = []
    for p in scue_root.rglob("*.py"):
        parts = str(p.relative_to(scue_root))
        if ".venv" in parts or "node_modules" in parts:
            continue
        if parts.startswith("tests/"):
            continue
        files.append(p)
    return files


@pytest.fixture
def scue_ts_files(scue_root: Path) -> list[Path]:
    """All TypeScript source files in SCUE (excluding node_modules)."""
    files = []
    frontend = scue_root / "frontend" / "src"
    if frontend.exists():
        for p in frontend.rglob("*.ts"):
            files.append(p)
        for p in frontend.rglob("*.tsx"):
            files.append(p)
    return files


@pytest.fixture
def tasks_jsonl(agent_dir: Path) -> list[dict[str, Any]]:
    """All tasks from the task tracker."""
    path = agent_dir / "tasks.jsonl"
    if not path.exists():
        return []
    tasks = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            tasks.append(json.loads(line))
    return tasks


@pytest.fixture
def runs_jsonl(agent_dir: Path) -> list[dict[str, Any]]:
    """All run records."""
    path = agent_dir / "runs.jsonl"
    if not path.exists():
        return []
    runs = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            runs.append(json.loads(line))
    return runs


@pytest.fixture
def handoff_schema(agent_dir: Path) -> dict[str, Any]:
    """The handoff envelope JSON schema."""
    path = agent_dir / "schemas" / "handoff-envelope.json"
    return json.loads(path.read_text())


@pytest.fixture
def session_transcripts(agent_dir: Path) -> list[Path]:
    """Available session transcript markdown files."""
    convos = agent_dir / "conversations"
    if not convos.exists():
        return []
    return sorted(convos.glob("*.md"), key=lambda p: p.stat().st_size, reverse=True)
