# New Project Init Prompt

> **Usage:** Copy the block below into a fresh Claude Code session at the THE_FACTORY root.
> Fill in the `[FILL]` fields before pasting. Everything else is ready to go.

---

```
I want to build a new project in THE_FACTORY.

## What I'm Building
- **Name:** [FILL: project name, e.g., "SoundCheck"]
- **One-liner:** [FILL: what it does in one sentence]
- **Location:** projects/[FILL: path, e.g., "SoundCheck" or "DjTools/soundcheck"]

## The Problem
[FILL: 2-3 sentences. What problem does this solve? Who is it for?]

## Stack Preferences
[FILL: any stack preferences, or "your call based on the problem"]
<!-- Examples: "Next.js + SQLite", "Python CLI", "FastAPI + React", "plain TypeScript" -->

## Scope for This Session
[FILL: what should be buildable in one session, or "scaffold + first working feature"]

## Non-Goals
- [FILL: what this project is NOT, or "none yet"]

## Hard Constraints
- [FILL: e.g., "must work offline", "no cloud dependencies", or "none"]

---

## Your Process

1. **Read `CLAUDE.md`** at repo root — follow the pipeline.
2. **Scaffold the project** using `skills/project-scaffold/SKILL.md`:
   - Create the directory structure (CLAUDE.md, .agent/, skills/, docs/)
   - Write a project CLAUDE.md (≤200 lines, project-specific only — don't duplicate meta rules)
   - Create `.agent/tasks.jsonl` with initial tasks
3. **Write a spec** using `templates/spec.md` for the first feature/MVP.
   - Fill Frozen Intent from what I wrote above.
   - Draft Mutable Specification — then stop and ask me to confirm before implementing.
4. **Follow feature-flow** (`feature-flow/SKILL.md`) for implementation:
   - Use the Greenfield Variant (commit per-tier, not per-phase)
   - Run tests before closing
5. **At session end**, hooks handle state snapshot automatically. Just make sure tasks.jsonl is current.

If anything above is ambiguous, ask me before proceeding. Do NOT assume.
```
