# THE_FACTORY

THE_FACTORY is a reusable operating system for software projects run with AI agents.

## Operating Model (v1.9.1)

One default operator agent. Specialist behavior via skills, not standing roles.

- **CLAUDE.md** — hot runtime constitution (always loaded, ≤200 lines)
- **Flow skills** — predefined step sequences loaded by task type (debug, feature, refactor)
- **Domain skills** — project-specific knowledge loaded by trigger table
- **Structured state** — task tracking in `.agent/tasks.jsonl`, not markdown session files
- **Eval-first improvement** — every repeated failure becomes a test case before it becomes a rule

## Root Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Constitution: core principles, trigger table, flow routing, session protocol |
| `OPERATOR_PROTOCOL.md` | Governance: artifact schemas, review cadence, rollout policy, logging |
| `INIT.md` | Onboarding: routes a fresh agent into the current model |
| `IMPLEMENTATION_PROMPT.md` | Scaffolding: bootstraps or syncs a project's `.agent/` and skill infrastructure |
| `PROTOCOL_REVIEW_PROMPT.md` | Review: evidence-driven protocol improvement process |
| `PROTOCOL_IMPROVEMENTS.md` | Backlog: running log of protocol-level observations |

## Workspace Layout

```
THE_FACTORY/
├── CLAUDE.md              ← constitution (hot, always loaded)
├── OPERATOR_PROTOCOL.md   ← governance layer
├── INIT.md                ← onboarding entry point
├── PROTOCOL_IMPROVEMENTS.md ← canonical backlog
├── .agent/
│   ├── VERSION.md         ← version history + scoring
│   ├── tasks.jsonl        ← root-level task tracker
│   ├── runs.jsonl         ← run telemetry ledger
│   ├── incidents.jsonl    ← structured incident log
│   ├── reviews/           ← experiential review scorecards
│   ├── evals/             ← eval suite + manifest
│   ├── schemas/           ← JSON schemas (handoff envelope, run, incident)
│   └── metrics/           ← metric definitions and targets
├── .claude/skills/        ← flow skills (debug, feature, refactor)
├── skills/                ← portfolio-level domain skills
├── templates/             ← canonical artifact templates
├── projects/
│   ├── CRUCIBLE/
│   ├── DjTools/
│   └── Tinyshop/
└── support/               ← archived reviews, historical reference
```

## Quick Start

1. **Human:** Read this file.
2. **Fresh agent:** Give it `INIT.md`. It routes into the current model.
3. **New project:** Use `IMPLEMENTATION_PROMPT.md` to scaffold `.agent/`, skills, and project CLAUDE.md.
4. **Existing project:** Load CLAUDE.md → classify task → load flow skill → execute.

## Core Idea

Agents coordinate through structured files on disk, not shared memory.

Pattern: `human intent → artifact → skill-driven agent → artifact → next decision`

Flow skills define the **sequence** (what steps to follow).
Domain skills define the **knowledge** (what patterns and constraints apply).
Both load simultaneously. The flow drives the steps; the domain informs decisions.

## Protocol Evolution

- Protocol changes require evidence (run records, incident logs, eval results)
- Classify failures before proposing fixes: specification, handoff, or verification layer
- Fix scaffolds before swapping models
- See `PROTOCOL_REVIEW_PROMPT.md` for the full review process

## Version

- **Current:** v1.9.1 (2026-03-20)
- **Previous:** v1.8 archived at `support/v1.8/`
- **Migration docs:** `support/v1.9/`
