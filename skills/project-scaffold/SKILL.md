---
name: project-scaffold
description: Use when bootstrapping a new project or syncing an existing project after a protocol change. Creates the .agent/ structure, project CLAUDE.md, and task tracker.
---

# Project Scaffold Skill

## When to Use
- Bootstrapping a new project into the portfolio
- Syncing an existing project after a meta-infrastructure version change

## New Project Structure
```
projects/[ProjectName]/
├── CLAUDE.md              ← project-level constitution (≤200 lines)
├── .agent/
│   ├── tasks.jsonl        ← structured task tracker
│   └── evals/             ← project-specific eval cases
├── skills/                ← project-specific domain skills
├── docs/
│   ├── interfaces.md      ← canonical cross-layer contracts
│   └── DECISIONS.md       ← ADRs (only if threshold met)
└── [source code]
```

## Project CLAUDE.md Template
```markdown
# [Project Name]

[One-line description]

## Stack
- [technology list]

## Architecture
- [brief layer/component description]

## Commands
- [build, test, run commands]

## Critical Rules
- [project-specific invariants]

## Gotchas
- [highest-signal failure patterns from experience]
```

## Task Tracker Setup
Create `.agent/tasks.jsonl` with initial tasks:
```json
{"id": "task-001", "status": "pending", "summary": "...", "blockers": [], "updated": "ISO-8601"}
```

## Inheriting from Meta
- Projects inherit the meta-level `CLAUDE.md` automatically
- Do NOT duplicate meta-level rules in project CLAUDE.md
- Project CLAUDE.md contains only project-specific content
