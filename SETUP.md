# THE_FACTORY — Workspace Setup

## Prerequisites

- **Python 3.11+** (tested on 3.13)
- **Git**
- **Claude Code** (for running agent sessions)

## Quick Start

```bash
git clone <repo-url> THE_FACTORY
cd THE_FACTORY
python -m venv .venv
.venv/bin/pip install -e '.[evals]'

# Verify setup
.venv/bin/python scripts/doctor.py
```

## Operating Modes

THE_FACTORY supports two modes. The pipeline works in both — the difference is
which scripts have access to project repos.

### Standalone Mode (pipeline only)

Use this when working on THE_FACTORY itself — its skills, hooks, evals,
experiment framework, and documentation.

**What works:**
- All evals: `.venv/bin/python -m pytest evals/ -v`
- Doctor: `python scripts/doctor.py`
- Standalone experiment tasks: `tasks/standalone/`
- All skills, hooks, templates

**What doesn't work:**
- Project-specific experiment tasks (e.g., `tasks/fix-short-track-bpm.py`)
- SCUE mining regression tests (auto-skipped when project absent)
- assess.py trend analysis (needs run history from project sessions)

### Portfolio Mode (pipeline + project repos)

Use this when working on projects that use THE_FACTORY as their agent
orchestration layer.

```
THE_FACTORY/
└── projects/
    ├── DjTools/scue/    ← SCUE project repo (own git)
    ├── CRUCIBLE/         ← CRUCIBLE project repo (own git)
    ├── Tinyshop/         ← Tinyshop project repo (own git)
    └── enable/           ← other projects
```

Each project under `projects/` is its own git repository. THE_FACTORY's
`.gitignore` excludes all project source — **project code is never tracked
by the pipeline repo.**

**Additional setup for portfolio mode:**
```bash
# Clone project repos into projects/
mkdir -p projects/DjTools
git clone <scue-url> projects/DjTools/scue

# Install project-specific dependencies per project README
```

## Dependency Profiles

Install only what you need:

```bash
# Evals only (pytest)
.venv/bin/pip install -e '.[evals]'

# Experiments (Inspect AI + PyYAML)
.venv/bin/pip install -e '.[experiments]'

# Observability (Langfuse)
.venv/bin/pip install -e '.[observability]'

# Everything
.venv/bin/pip install -e '.[all]'
```

## Environment Variables

All optional — features degrade gracefully when absent.

| Variable | Purpose | Required for |
|---|---|---|
| `LANGFUSE_PUBLIC_KEY` | Langfuse tracing | Session observability |
| `LANGFUSE_SECRET_KEY` | Langfuse tracing | Session observability |
| `LANGFUSE_BASE_URL` | Langfuse host URL | Session observability |

## Health Check

Run the doctor script to validate your setup:

```bash
.venv/bin/python scripts/doctor.py         # human-readable output
.venv/bin/python scripts/doctor.py --json  # machine-readable output
```

It checks: Python version, virtual environment, required directories and files,
settings.json validity, hook script existence, JSONL integrity, environment
variables, and portfolio repo presence.

## Running Evals

```bash
.venv/bin/python -m pytest evals/ -v
```

Tests auto-skip when their dependencies (project repos, transcripts, incidents)
are absent. A clean standalone checkout should pass all non-skipped tests.

## Running Experiments

```bash
# List available tasks
.venv/bin/python scripts/experiment.py --list-tasks

# Run a standalone task
.venv/bin/python scripts/experiment.py --task tasks/standalone/fix-off-by-one.py

# Compare variants
.venv/bin/python scripts/experiment.py --task tasks/standalone/fix-off-by-one.py \
    --variants variants/baseline.yaml variants/minimal.yaml
```

## Scaffolding New Projects

Use the project-scaffold skill (see `skills/project-scaffold/SKILL.md`).
Each new project gets:
- Its own git repo under `projects/`
- A `CLAUDE.md` with project-specific triggers
- An `.agent/` directory for task tracking
- Section contracts if the project warrants decomposition
