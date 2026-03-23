# THE_FACTORY v2.0

## Core Principles
- One operator agent. Specialist behavior via skills, not standing roles.
- Evals over docs. Repeated failures become test cases, not rules.
- Hooks enforce, skills inform. Deterministic enforcement > prompt discipline.
- Progressive disclosure. Load skills on trigger, not at startup.

## Trigger Table

Pipeline-level skills. Project-specific triggers live in each project's own CLAUDE.md.

| Task Pattern | Skill Location | Notes |
|---|---|---|
| Contract integrity / cross-layer | `[project]/skills/contract-integrity.md` | Field preservation, PRODUCER/CONSUMER |
| Handoff between domains | `skills/handoff/SKILL.md` | JSON Schema envelope |
| Project scaffolding | `skills/project-scaffold/SKILL.md` | .agent/ structure |
| Brainstorm / ideation | `skills/brainstorm/SKILL.md` | Research→candidates |

## Flow Routing

Classify the task, load the flow. Don't blend flows.

| Signal | Flow | Posture |
|---|---|---|
| fix, bug, error, broken, regression, failing | `.claude/skills/debug-flow/` | Minimal change. Reproduce first. |
| implement, add, create, new, build, feature | `.claude/skills/feature-flow/` | Spec first. Human confirms. |
| refactor, extract, consolidate, simplify | `.claude/skills/refactor-flow/` | Read first. No behavior change. |
| brainstorm, ideate, applications of | `skills/brainstorm/SKILL.md` | Generate. Operator triages. |

## Session Protocol
- **Start:** Load this file. Check `.agent/state-snapshot.json` for prior session context. Load codebase orientation skill if working on a project.
- **Mid-session:** Load skills as needed via trigger table.
- **End:** Hooks enforce landing procedure. State snapshot written automatically.

## What Hooks Enforce (don't duplicate in prose)
- Git guard: no commits to main, no force-push, no reset --hard (fail-closed, no jq dependency)
- Fix-attempt tracker: blocks after 3 source edits without running tests
- State snapshot: branch, commit, tasks, modified files persisted at session end (valid JSON via Python)
- Audit run record: warns if no run record written during session
- Langfuse trace: session metrics sent to Langfuse (when configured)

## What's NOT Enforced by Hooks (still important)
- Update `.agent/tasks.jsonl` with status of touched tasks
- Append run record to `.agent/runs.jsonl` on task completion
- Log incidents to `.agent/incidents.jsonl` on failure
- File eval cases for recurring failure patterns

## Eval Suite
Run: `.venv/bin/python -m pytest evals/ -v`
~48 tests: conventions, flows, handoffs, mining regressions, behavioral checks.
SCUE-specific tests auto-skip when /projects absent.

## Workspace Layout
```
THE_FACTORY/
├── CLAUDE.md              ← this file
├── .claude/
│   ├── hooks/             ← deterministic enforcement
│   ├── settings.json      ← hook wiring
│   ├── skills/            ← flow skills (debug, feature, refactor)
│   └── plans/             ← migration plans
├── .agent/
│   ├── tasks.jsonl        ← work queue
│   ├── runs.jsonl         ← run records
│   ├── state-snapshot.json← session continuity
│   ├── evals/             ← eval specs (.eval.md)
│   └── schemas/           ← JSON schemas
├── evals/                 ← executable eval suite (pytest)
├── skills/                ← portfolio-level skills
├── projects/              ← CRUCIBLE, DjTools/scue, Tinyshop, enable/
├── templates/             ← spec, plan, handoff, tasks
└── support/               ← archives, research, migration docs
```

## Experiment Framework
Run: `python scripts/experiment.py --list-tasks` / `--list-variants`
Compare: `python scripts/experiment.py --task tasks/fix-short-track-bpm.py --variants variants/baseline.yaml variants/minimal.yaml`
Assess: `python scripts/assess.py --last 20`

## Version
- **Current:** v2.1.0 (2026-03-23)
- **Previous:** v2.0 → v1.9.2 → v1.9 → v1.8 (archived in `support/`)
- **Migration plan:** `.claude/plans/v2-migration.md`
- **Mining results:** `support/v2/conversation-mining-results.md`
