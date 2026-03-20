# Meta-Infrastructure Constitution (v1.9)

## Core Principles
- One default operator agent. Specialist behavior via skills, not standing roles.
- Documentation earns its context window. If not loaded on demand, validated automatically,
  used by humans regularly, or recording an irreversible decision — delete it.
- Evals over docs. Every repeated failure becomes a test case before it becomes a rule.
- Structured state over prose. Task tracking in JSONL, not markdown session files.
- Progressive disclosure. Advertise skill names at startup. Load full skill on trigger.
  Load references during execution. Never load everything.

## Trigger Table
> Project-specific skills live in `[project]/skills/`. Portfolio-level skills live in `skills/`.

| Task Pattern | Skill Location | Notes |
|---|---|---|
| Audio analysis / beatgrid / rekordbox | `scue/skills/audio-analysis.md` | Pioneer/Serato metadata, offline analysis |
| Beat-link bridge / Pro DJ Link | `scue/skills/beat-link-bridge.md` | Layer 0 lifecycle, message types |
| Pioneer hardware / CDJ / XDJ / DJM | `scue/skills/pioneer-hardware.md` | Hardware variants, protocol, metadata |
| Frontend / React / TypeScript / Zustand | `scue/skills/react-typescript-frontend.md` | SCUE component patterns |
| Python / FastAPI / asyncio backend | `scue/skills/python-fastapi.md` | Routers, testing, async patterns |
| Contract integrity / cross-layer changes | `[project]/skills/contract-integrity.md` | Field preservation, PRODUCER/CONSUMER |
| E2B sandbox / code execution | `CRUCIBLE/skills/e2b-sandbox.md` | SDK patterns, TTL, artifact flush |
| Langfuse / tracing / observability | `CRUCIBLE/skills/langfuse-tracing.md` | SDK type gotchas, trace patterns |
| TypeScript / Node.js / ESM / NodeNext | `CRUCIBLE/skills/typescript-node.md` | Module resolution, barrel files |
| Anthropic SDK / Claude API | `Tinyshop/skills/anthropic-sdk.md` | SDK usage patterns |
| Handoff between domains | `skills/handoff/SKILL.md` | JSON Schema envelope, validation |
| New project scaffolding | `skills/project-scaffold/SKILL.md` | .agent/ structure, CLAUDE.md template |
| Protocol review / meta-infra | `skills/protocol-review/SKILL.md` | Review process, scoring rubric |

## Task-Type Flow Routing

Before starting any task, classify it and load the appropriate flow skill.
If a task spans multiple types, choose the PRIMARY type and note the secondary.
Do NOT blend flows — complete one flow, then start the next if needed.

| Signal in task description | Flow to load | Posture |
|---|---|---|
| fix, bug, error, broken, regression, failing, crash, timeout | `.claude/skills/debug-flow/` | Minimal change. Reproduce first. |
| implement, add, create, new, build, feature, endpoint, resolver | `.claude/skills/feature-flow/` | Spec first. Human confirms before coding. |
| refactor, extract, consolidate, clean up, simplify, reorganize | `.claude/skills/refactor-flow/` | Read first. No behavior change. |
| migrate, upgrade, convert, move from X to Y | _(future: migration-flow/)_ | Use feature-flow with extra caution. |
| write tests, test coverage, add tests for | _(future: test-gen-flow/)_ | Use feature-flow Phase 4 expanded. |
| investigate, research, understand, analyze, why does | _(future: investigation-flow/)_ | Read-only, report to human. |

Flow skills define the SEQUENCE (what steps to follow).
Domain skills define the KNOWLEDGE (what patterns and constraints apply).
Both may be loaded simultaneously. The flow drives the steps; the domain informs decisions.

## Session Protocol
- **Start:** Load this constitution. Read trigger table. Begin work.
- **Mid-session:** Load skills as needed. Do not preload.
- **End ("Land the Plane"):**
  1. Update task tracker (`.agent/tasks.jsonl`) with status of all touched tasks:
     ```json
     {"id":"TASK-ID","taskType":"debug|feature|refactor","flowPhase":"phase stopped at","status":"complete|partial|blocked","summary":"one-line result","blockers":[],"plan_checkpoints":["phases completed"],"updated":"ISO-8601"}
     ```
  2. Append a run record to `.agent/runs.jsonl`:
     ```json
     {"run_id":"run-YYYY-MM-DD-NNN","date":"ISO-8601","project_id":"project","task_id":"TASK-ID","task_type":"debug|feature|refactor","workflow_path":"flow skill used","result":"success|partial|failed|blocked|escalated","rework_required":false,"attempt_count":1}
     ```
     Include optional fields (`input_tokens`, `output_tokens`, `tool_calls`, `latency_ms`, `estimated_cost`) when you can estimate them. Omit fields you cannot measure.
  3. If a failure occurred (iteration cap hit, false pass, escaped defect), append to `.agent/incidents.jsonl`:
     ```json
     {"incident_id":"inc-YYYY-MM-DD-NNN","date":"ISO-8601","project":"project","task_id":"TASK-ID","severity":"critical|high|medium|low","failure_type":"description","detected_by":"agent|verifier|human","root_cause_classification":"SPECIFICATION_OR_SYSTEM_DESIGN|HANDOFF_OR_ALIGNMENT|VERIFICATION_OR_TERMINATION","protocol_change_candidate":false}
     ```
     No incident = good. Only write incidents for actual failures.
  4. If an architecture decision was made that meets ADR threshold, write ADR in affected repo.
  5. If a new failure pattern was observed and is likely to recur, file an eval case in `.agent/evals/` BEFORE adding a doc rule.
  6. Discard session scratch. Do not create session artifact files.

## Git Protocol
- **Branch:** Create a branch from the project's current branch before starting work.
  Name: `{task-type}/{task-id}-{slug}` (e.g., `fix/TASK-042-waveform-offset`).
- **Commit at phase boundaries:** Each flow-skill phase that produces working changes = one commit.
  Message format: `{phase}: {what changed}` (e.g., `reproduce: add failing test for offset bug`).
- **Final commit:** Include the `.agent/runs.jsonl` append in the last commit on the branch.
- **Never** commit directly to `main`. Always branch.
- **Never** amend. A new commit preserves the phase trail.
- **Never** force-push. If you need to fix a commit, make a new one.
- **Never** merge or push unless the human explicitly asks.
- **If blocked:** Commit partial progress before escalating. Uncommitted work is unrecoverable.

## Handoff Protocol
- Handoffs use the v1.0.0 JSON Schema envelope (see `skills/handoff/schema.json`).
- Validate before delivery. Reject malformed handoffs.
- Handoffs are for genuine domain boundary crossings, not sequential tasks.

## Task Tracker
- Each project has `.agent/tasks.jsonl` — one JSON line per task.
- Query: `scripts/tasks.sh ready|blocked|all`
- Never create markdown TODO/plan/session files for tracking state.

## Quality Gates
- Convention violations → write eval case in `.agent/evals/` BEFORE adding a doc rule.
- Eval suite: `.agent/evals/run-evals.sh`
- A rule without a corresponding eval is an unverified hope.

## Memory Tiers
- **Hot (always loaded):** This file. Project-level CLAUDE.md files.
- **Warm (per-task):** Skills loaded via trigger table. ~100 tokens advertised, full SKILL.md on trigger.
- **Cold (on-demand):** Architecture specs, ADRs, research findings. Retrieved by explicit reference.

## ADR Threshold
Write an ADR only when the decision:
- Affects >1 project
- Changes a shared interface
- Would take >1 day to reverse
ADRs live in the repo they affect, not centrally. Use MADR lightweight template.

## What NOT To Do
- Do not create session artifact markdown files.
- Do not copy-paste preambles. Skills are loaded on demand.
- Do not add rules to this file without a corresponding eval case.
- Do not create a new agent role. Create a skill instead.
- Do not preload all skills. Use the trigger table.

## Workspace Layout
```
THE_FACTORY/
├── CLAUDE.md              ← this file (constitution)
├── .agent/
│   ├── VERSION.md         ← version history + scoring
│   ├── tasks.jsonl        ← root-level task tracker
│   ├── evals/             ← eval suite
│   └── schemas/           ← JSON schemas (handoff envelope, etc.)
├── skills/                ← portfolio-level skills (progressive disclosure)
├── projects/
│   ├── CRUCIBLE/
│   ├── DjTools/
│   └── Tinyshop/
├── templates/             ← canonical artifact templates
└── support/               ← archived reviews, historical reference
```

## Project-Level CLAUDE.md
Each project has its own CLAUDE.md (≤200 lines) containing:
- Stack and architecture summary
- Build/test commands
- Critical rules specific to that project
- Project-specific trigger table (if beyond portfolio-level skills)
- Gotchas section (highest-signal failure patterns)

## Version
- **Current:** v1.9.2 (2026-03-20)
- **Previous:** v1.9.1 → v1.9 → v1.8 (archived at `support/v1.8/`)
- **Migration docs:** `support/v1.9/`
- **Scoring rubric:** `.agent/evals/meta-scoring.md`
- **Version history:** `.agent/VERSION.md`
