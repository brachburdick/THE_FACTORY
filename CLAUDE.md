# THE_FACTORY v2.0

## Core Principles
- One operator agent. Specialist behavior via skills, not standing roles.
- Evals over docs. Repeated failures become test cases, not rules.
- Hooks enforce, skills inform. Deterministic enforcement > prompt discipline.
- Progressive disclosure. Load skills on trigger, not at startup.

## Trigger Table

| Task Pattern | Skill Location | Notes |
|---|---|---|
| SCUE session start / any SCUE work | `projects/DjTools/scue/skills/codebase-orientation.md` | Load first. File map, data flows, gotchas. |
| Audio analysis / beatgrid / rekordbox | `projects/DjTools/scue/skills/audio-analysis.md` | Pioneer/Serato metadata |
| Beat-link bridge / Pro DJ Link | `projects/DjTools/scue/skills/beat-link-bridge.md` | Lifecycle, messages, API reference |
| Pioneer hardware / CDJ / XDJ / DJM | `projects/DjTools/scue/skills/pioneer-hardware.md` | Hardware variants, device specifics |
| Frontend / React / TypeScript / Zustand | `projects/DjTools/scue/skills/react-typescript-frontend.md` | SCUE component patterns |
| Python / FastAPI / asyncio backend | `projects/DjTools/scue/skills/python-fastapi.md` | Routers, testing, async patterns |
| Contract integrity / cross-layer | `[project]/skills/contract-integrity.md` | Field preservation, PRODUCER/CONSUMER |
| E2B sandbox / code execution | `projects/CRUCIBLE/skills/e2b-sandbox.md` | SDK patterns, TTL |
| Langfuse / tracing | `projects/CRUCIBLE/skills/langfuse-tracing.md` | SDK gotchas, trace patterns |
| TypeScript / Node.js / ESM | `projects/CRUCIBLE/skills/typescript-node.md` | Module resolution |
| Anthropic SDK / Claude API | `projects/Tinyshop/skills/anthropic-sdk.md` | SDK usage |
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
- Git guard: no commits to main, no force-push, no reset --hard
- State snapshot: branch, commit, tasks, modified files persisted at session end
- Langfuse trace: session metrics sent to Langfuse (when configured)

## What's NOT Enforced by Hooks (still important)
- Update `.agent/tasks.jsonl` with status of touched tasks
- Append run record to `.agent/runs.jsonl` on task completion
- Log incidents to `.agent/incidents.jsonl` on failure
- File eval cases for recurring failure patterns

## Eval Suite
Run: `.venv/bin/python -m pytest evals/ -v`
42 tests covering conventions, flows, handoffs, and mining-derived regression checks.

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
├── projects/              ← CRUCIBLE, DjTools/scue, Tinyshop
├── templates/             ← spec, plan, handoff, tasks
└── support/               ← archives, research, migration docs
```

## Version
- **Current:** v2.0.0 (2026-03-23)
- **Previous:** v1.9.2 → v1.9 → v1.8 (archived in `support/`)
- **Migration plan:** `.claude/plans/v2-migration.md`
- **Mining results:** `support/v2/conversation-mining-results.md`
