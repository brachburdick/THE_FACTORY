# THE_FACTORY v2.1

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
| Section review / audit / quality check | `skills/section-review/SKILL.md` | Three-pass: section→boundary→integration |

## Flow Routing

Classify the task, load the flow. Don't blend flows.

| Signal | Flow | Posture |
|---|---|---|
| fix, bug, error, broken, regression, failing | `.claude/skills/debug-flow/` | Minimal change. Reproduce first. |
| implement, add, create, new, build, feature | `.claude/skills/feature-flow/` | Spec first. Human confirms. |
| refactor, extract, consolidate, simplify | `.claude/skills/refactor-flow/` | Read first. No behavior change. |
| brainstorm, ideate, applications of | `skills/brainstorm/SKILL.md` | Generate. Operator triages. |

## Session Protocol
- **Start:**
  1. Load this file.
  2. Check `.agent/state-snapshot.json` for prior session context.
  3. Check `.agent/tasks.jsonl` for pending/in_progress work. Claim a task by setting `status: "in_progress"` before starting. Use its `id` (e.g. `tf-003`) as your task reference throughout the session.
  4. Check `LEARNINGS.md` for environment constraints before installing dependencies.
  5. Load codebase orientation skill if working on a project.
- **Mid-session:** Load skills as needed via trigger table. Reference the claimed task ID in commits, run records, and incident logs.
- **End:** Hooks enforce landing procedure. State snapshot written automatically. If you completed work, you MUST have written a run record to `.agent/runs.jsonl` with the task ID before the session ends.

## Three-Loop Control Model

THE_FACTORY operates at three speeds with different gate strictness:

| Loop | Speed | Mechanisms | Gate |
|---|---|---|---|
| **Inner** (edit→test→fix) | Seconds | fix-attempt-tracker (2-cap), lint, unit tests | Automatic — hooks enforce |
| **Middle** (design→implement→integrate) | Minutes | section boundary checks, plan-gate, risk classifier, spec approval | Semi-automatic — hooks + operator at checkpoints |
| **Outer** (release→observe→learn) | Days/weeks | assess.py trends, DORA-like metrics, run record analysis, calibration reviews | Operator-driven — data informs threshold tuning |

New enforcement mechanisms belong in the loop matching their speed. Inner-loop gates must be fast and deterministic. Middle-loop gates can require operator input. Outer-loop mechanisms are observational — they feed future threshold changes, not real-time blocks.

## What Hooks Enforce (don't duplicate in prose)
- Git guard: no commits to main, no force-push, no reset --hard (fail-closed, no jq dependency)
- Fix-attempt tracker: blocks after 2 source mutations (Edit/Write) without running tests; resets on test run
- Risk classifier: reads task risk level (low/medium/high), blocks high-risk source mutations without approved plan
- State snapshot: branch, commit, tasks, modified files persisted at session end (valid JSON via Python)
- Audit run record: warns if no run record written during session
- Langfuse trace: session metrics sent to Langfuse (when configured)

## What's NOT Enforced by Hooks (still important)
- Update `.agent/tasks.jsonl` with status of touched tasks
- Append run record to `.agent/runs.jsonl` on task completion
- Log incidents to `.agent/incidents.jsonl` on failure
- File eval cases for recurring failure patterns

## Project Isolation
THE_FACTORY is the pipeline/process repo. **Project source code must never be tracked by this repo.** Each project under `projects/` has its own git repo and its own CLAUDE.md. The `.gitignore` enforces this — do not override it. If you need to reference project structure in pipeline docs, use generic examples, not real project paths or content.

## Section-Based Project Structure
Projects with sufficient complexity should be divided into **sections** — isolated review units defined by real dataflow boundaries, not just folders. Each section has a 1-page contract specifying purpose, owned paths, inputs, outputs, invariants, and verification command.

- **Skill:** `skills/section-review/SKILL.md` — three-pass review model (section → boundary → integration)
- **Template:** `templates/section-contract.md` — 1-page contract format
- **Principles:** `SYNTROPY.md` — 8 convergent principles for structured decomposition
- **Enforcement:** Section boundary imports and file coverage are checked by evals

**Re-evaluate sections after each session batch.** When a project completes a milestone, feature, or significant refactor, assess whether sections should be added, split, merged, or have their boundaries adjusted. Section structure is a living artifact — it evolves with the codebase. See `sections/SECTIONS.md` in each project for the current section map and split/merge criteria.

## Eval Suite
Run: `.venv/bin/python -m pytest evals/ -v`
~73 tests: conventions (including section boundary enforcement), flows (including hook tests), handoffs (including task closure), mining regressions, behavioral checks.
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
│   ├── reports/           ← generated dashboards (token-dashboard.html)
│   └── schemas/           ← JSON schemas
├── evals/                 ← executable eval suite (pytest)
├── scripts/               ← tooling (index, assess, experiment, token-dashboard)
├── skills/                ← portfolio-level skills
├── projects/              ← CRUCIBLE, DjTools/scue, Tinyshop, enable/
├── templates/             ← spec, plan, handoff, tasks
└── support/               ← archives, research, migration docs
```

## Experiment Framework
Run: `python scripts/experiment.py --list-tasks` / `--list-variants`
Compare: `python scripts/experiment.py --task tasks/fix-short-track-bpm.py --variants variants/baseline.yaml variants/minimal.yaml`
Assess: `python scripts/assess.py --last 20`

## Token Dashboard
Visualizes token consumption & context window usage across Claude Code sessions.
Run: `python3 scripts/token-dashboard.py --last 30` (or `--project SCUE`, `--context-size 1000000`)
Output: `.agent/reports/token-dashboard.html` (open in browser)
- **Monitor tab**: toggle sessions on/off, each gets burn rate + context fill charts (expandable to per-turn cost + tool breakdown)
- **Compare tab**: overlay burn rate and context fill curves for up to 5 sessions
- **Projects tab**: aggregate token stats per project
- **Filter bar**: recency (Last 10 / 24h / 7d / 30d / All) + project dropdown, persists across all tabs

## Version
- **Current:** v2.1.0 (2026-03-23)
- **Previous:** v2.0 → v1.9.2 → v1.9 → v1.8 (archived in `support/`)
- **Migration plan:** `.claude/plans/v2-migration.md`
- **Mining results:** `support/v2/conversation-mining-results.md`
