# THE_FACTORY v2.1

## Session Protocol
- **Start:**
  1. Load this file.
  2. Check `.agent/state-snapshot.json` for prior session context. It contains decisions, dead ends, and key locations from the prior session — use them to skip re-exploration.
  3. Check `.agent/tasks.jsonl` for pending/in_progress work. Use `python scripts/ready.py` to find the next unblocked task. Claim it by setting `status: "in_progress"` before starting. Use its `id` (e.g. `tf-003`) as your task reference throughout the session.
  4. Check `.agent/questions.jsonl` for answered questions — load answers relevant to your task into context.
  5. Run `python scripts/check-read-state.py --stale-only` — only re-read stale files; trust cached summaries for fresh ones.
  6. Check `LEARNINGS.md` for environment constraints before installing dependencies.
  7. Load codebase orientation skill if working on a project.
- **Mid-session:** Load skills as needed via trigger table. Reference the claimed task ID in commits, run records, and incident logs.
- **When blocked by uncertainty:** Do NOT block the session waiting for the operator. Write a question to `.agent/questions.jsonl` (see schema in `.agent/schemas/question.schema.json`), then move to the next ready task via `python scripts/ready.py`. The operator answers async; the next session picks up the answer. Format:
  ```json
  {"id":"q-001","task":"tf-088","question":"Track all file reads or project dirs only?","options":["all reads","project dirs only"],"default":"project dirs only","impact":"Controls manifest size","status":"pending","asked":"2026-03-27T12:00:00Z","answered":null,"answer":null}
  ```
- **End:** Hooks enforce landing procedure. State snapshot written automatically. If you completed work, you MUST have written a run record to `.agent/runs.jsonl` with the task ID before the session ends.

## Oversight Policy

Two tiers: **routine** (low-risk, known pattern) = autonomous. **Everything else** = gated (pause at phase gates for operator). High-risk tasks additionally require an approved plan before any source mutations. See `docs/oversight-matrix.md` for details.

## What Hooks Enforce (don't duplicate in prose)
- Git guard: no commits to main, no force-push, no reset --hard (fail-closed, no jq dependency)
- Fix-attempt tracker: blocks after 2 source mutations (Edit/Write) without running tests; resets on test run. Compound budget: 10 total mutations per phase; resets on `budget-reset`. Circuit breakers: 4 edit-test cycles, 10 unique files.
- Risk classifier: reads task risk level (low/medium/high), blocks high-risk source mutations without approved plan
- Blast radius: cross-references Edit/Write paths against active task's section contract owned_paths; blocks out-of-scope mutations when section is assigned
- State snapshot: branch, commit, tasks, modified files, decisions, dead ends persisted at session end (valid JSON via Python). Mid-session lightweight snapshot fires every 15 mutations (PostToolUse on Edit/Write) — no pytest, atomic write.
- Audit run record: warns if no run record written during session
- Build integrity: warns (does not block) when editing infrastructure files (hooks, CI, packaging, settings, Dockerfiles, release scripts, .gitignore)
- Reference check: advisory — warns when Edit replaces a string that appears in evals/ or hooks/ (prevents rename→eval-failure rework)
- Langfuse trace: session metrics sent to Langfuse (when configured)

## Core Principles
- One operator agent. Specialist behavior via skills, not standing roles.
- Evals over docs. Repeated failures become test cases, not rules.
- Hooks enforce, skills inform. Deterministic enforcement > prompt discipline.
- Progressive disclosure. Load skills on trigger, not at startup.

## Flow Routing

Classify the task, load the flow. Don't blend flows.

| Signal | Flow | Posture |
|---|---|---|
| fix, bug, error, broken, regression, failing | `.claude/skills/debug-flow/` | Minimal change. Reproduce first. |
| implement, add, create, new, build, feature | `.claude/skills/feature-flow/` | Spec first. Human confirms. |
| refactor, extract, consolidate, simplify | `.claude/skills/refactor-flow/` | Read first. No behavior change. |
| brainstorm, ideate, applications of | `skills/brainstorm/SKILL.md` | Generate. Operator triages. |

## Trigger Table

Pipeline-level skills. Project-specific triggers live in each project's own CLAUDE.md.

| Task Pattern | Skill Location | Notes |
|---|---|---|
| Contract integrity / cross-layer | `[project]/skills/contract-integrity.md` | Field preservation, PRODUCER/CONSUMER |
| Handoff between domains | `skills/handoff/SKILL.md` | JSON Schema envelope |
| Project scaffolding | `skills/project-scaffold/SKILL.md` | .agent/ structure |
| Brainstorm / ideation | `skills/brainstorm/SKILL.md` | Research→candidates |
| Section review / audit / quality check | `skills/section-review/SKILL.md` | Three-pass: section→boundary→integration |
| Context feels heavy / turn > 25 | `skills/context-checkpoint/SKILL.md` | Compress before degradation |

## Three-Loop Control Model

THE_FACTORY operates at three speeds with different gate strictness:

| Loop | Speed | Mechanisms | Gate |
|---|---|---|---|
| **Inner** (edit→test→fix) | Seconds | fix-attempt-tracker (2-cap + compound budget), lint, unit tests | Automatic — hooks enforce |
| **Middle** (design→implement→integrate) | Minutes | section boundary checks, blast-radius scope check, plan-gate, risk classifier, spec approval | Semi-automatic — hooks + operator at checkpoints |
| **Outer** (release→observe→learn) | Days/weeks | assess.py trends, DORA-like metrics, run record analysis, calibration reviews | Operator-driven — data informs threshold tuning |

New enforcement mechanisms belong in the loop matching their speed. Inner-loop gates must be fast and deterministic. Middle-loop gates can require operator input. Outer-loop mechanisms are observational — they feed future threshold changes, not real-time blocks.

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
~98 tests: conventions (including section boundary enforcement), flows (including hook tests), handoffs (including task closure), mining regressions, behavioral checks.
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
│   ├── tasks.jsonl        ← work queue (use scripts/ready.py)
│   ├── questions.jsonl    ← async decision queue
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
- **Current:** v3.0.0 (2026-03-27)
- **Previous:** v2.1.1 → v2.1.0 → v2.0 → v1.9.2 → v1.9 → v1.8 (archived in `support/`)
- **v3.0 changelog:** 44 improvements from consolidated research (12 proposals, Claude + GPT). Risk classifier, blast radius, circuit breaker, compound error budget, pre-flight checks, oversight matrix, pipeline SLOs, CI workflows, JSON schemas, ADRs, artifact taxonomy, portable hooks, doctor script, standalone experiments, context efficiency. See `.claude/plans/v22-consolidated-improvement-plan.md`.
- **Mining results:** `support/v2/conversation-mining-results.md`

## Critical Reminders (recency-anchored)
- **Run record required.** Every session that completes work MUST write a run record before ending.
- **2-attempt cap.** After 2 failed fix attempts, STOP and escalate. Do not iterate blindly.
- **Don't block on uncertainty.** If a decision requires operator input, write to `.agent/questions.jsonl` and move to the next ready task. Never wait in-session for an answer the operator can give async.
- **3-probe-then-ask.** After 3 failed environment/hardware probes (network checks, port scans, device lookups), ask the user before continuing to investigate. A simple "is the device powered on?" saves 25+ wasted tool calls.
- **Single-writer model.** All Edit/Write stays in the main agent. Subagents are read-only.
- **Subagent prompts: be specific.** Use "Extract [specific data] from [specific files] as [format]" — not "read all X files." Vague prompts produce summaries that require re-reading.
- **Prefer Edit over Write for tested files.** Full rewrites of files with eval coverage obscure changes and increase error surface. Use Edit for targeted changes; reserve Write for new files.
- **Sub-agent concurrency cap.** Limit concurrent Agent tool calls to 3. Read-only agents (Explore, Plan) may run in parallel. Agents that produce artifacts should run sequentially to avoid merge conflicts in handoffs.
- **Context gate.** If turn count exceeds 40 or context feels degraded (forgotten paths, repeated reads), end the session with a handoff snapshot. Fresh context beats loaded context.
