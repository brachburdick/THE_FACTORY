# THE_FACTORY

THE_FACTORY is a reusable operating system for software projects run with AI agents.

## Operating Model (v2.0)

One operator agent. Specialist behavior via skills, not standing roles.
Deterministic enforcement via Claude Code hooks, not prompt discipline.

- **CLAUDE.md** — hot runtime constitution (always loaded, ≤100 lines)
- **Flow skills** — predefined step sequences loaded by task type (debug, feature, refactor)
- **Domain skills** — project-specific knowledge loaded by trigger table
- **Hooks** — deterministic enforcement (git guard, state snapshot, trace)
- **Eval suite** — executable pytest tests for conventions, flows, and regression
- **Experiment framework** — Inspect AI + assess.py for variant testing and improvement

## Root Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Constitution: core principles, trigger table, flow routing, session protocol |
| `INIT.md` | Onboarding: routes a fresh agent into the current model |
| `PROTOCOL_IMPROVEMENTS.md` | Backlog: running log of protocol-level observations |

## Workspace Layout

```
THE_FACTORY/
├── CLAUDE.md              ← constitution (hot, always loaded)
├── INIT.md                ← onboarding entry point
├── PROTOCOL_IMPROVEMENTS.md ← canonical backlog
├── .agent/
│   ├── VERSION.md         ← version history + scoring
│   ├── tasks.jsonl        ← root-level task tracker
│   ├── runs.jsonl         ← run telemetry ledger
│   ├── incidents.jsonl    ← structured incident log
│   ├── state-snapshot.json← session continuity (written by hook)
│   ├── evals/             ← eval specs (.eval.md)
│   └── schemas/           ← JSON schemas
├── .claude/
│   ├── hooks/             ← deterministic enforcement (git-guard, state-snapshot, langfuse-trace)
│   ├── settings.json      ← hook wiring
│   ├── skills/            ← flow skills (debug, feature, refactor)
│   └── plans/             ← migration plans
├── evals/                 ← executable eval suite (pytest)
├── scripts/               ← assess.py, experiment.py
├── skills/                ← portfolio-level domain skills
├── projects/
│   ├── CRUCIBLE/
│   ├── DjTools/
│   └── Tinyshop/
└── support/               ← archives, research, migration docs
```

## Quick Start

1. **Human:** Read this file.
2. **Fresh agent:** Give it `INIT.md`. It routes into the current model.
3. **New project:** Use `skills/project-scaffold/SKILL.md` to scaffold `.agent/`, skills, and project CLAUDE.md.
4. **Existing project:** Load CLAUDE.md → classify task → load flow skill → execute.

## Core Idea

Agents coordinate through structured files on disk, not shared memory.

Pattern: `human intent → artifact → skill-driven agent → artifact → next decision`

Flow skills define the **sequence** (what steps to follow).
Domain skills define the **knowledge** (what patterns and constraints apply).
Both load simultaneously. The flow drives the steps; the domain informs decisions.

## Improvement Loop

1. Run `scripts/assess.py --last 20` to score recent sessions against baselines
2. Run `pytest evals/ -v` to check convention/flow drift
3. Triage improvement candidates (accept/defer/reject)
4. For accepted improvements: edit the relevant skill or hook, add an eval case, re-run evals
5. For A/B testing: create a variant YAML, run with `scripts/experiment.py`

## Version

- **Current:** v2.0.0 (2026-03-23)
- **Previous:** v1.9.2 → v1.9 → v1.8 (archived in `support/`)
- **Migration plan:** `.claude/plans/v2-migration.md`
- **Mining results:** `support/v2/conversation-mining-results.md`
