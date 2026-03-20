# Implementation Prompt: Create or Sync Project Infrastructure

> **Instructions for the human operator:**
> Start a fresh agent session. Provide this file, `CLAUDE.md`, and any existing project
> artifacts. If you have a project brief from an INIT session, include that too.
> Use for new project bootstrap or after a protocol review to sync an existing project.

---

## Context

You are scaffolding or syncing a project's agent infrastructure to align with
the v1.9.1 operating model defined in `CLAUDE.md`.

You own agent infrastructure only. You do not modify application source code.

## What You Have Access To

- `CLAUDE.md` — the canonical operating model
- `OPERATOR_PROTOCOL.md` — governance rules, artifact schemas, review cadence
- Operator-provided project brief (if one exists)
- Root `templates/` — canonical artifact templates
- Existing project directory structure and artifacts

## Your Deliverables

### 1. Project CLAUDE.md

Create or update the project's `CLAUDE.md` (≤200 lines) containing:
- Stack and architecture summary
- Build/test commands
- Critical rules specific to this project
- Project-specific trigger table (if beyond portfolio-level skills)
- Gotchas section (highest-signal failure patterns)

### 2. Structured State (.agent/)

Create or verify the project has:
- `.agent/tasks.jsonl` — task tracker (one JSON line per task)
- `.agent/evals/` — eval directory for project-specific eval cases

### 3. Domain Skill Files

Create skeleton skill files in `skills/` when the project's docs clearly indicate
stable domains that need them.

Each scaffold must include:
- When this skill applies
- Stack or environment notes
- Common patterns
- Known gotchas
- Anti-patterns
- `[TODO: Fill from project experience]`

**Contract integrity skill file:** When a project has contract boundaries (WebSocket
payloads, API shapes, type definitions), create `skills/contract-integrity.md` with
field-preservation guidance specific to the project's stack and patterns.

### 4. Project Definition Record

If this is a new project, create a `PROJECT_DEFINITION_RECORD.md` using the template
at `templates/project-definition-record.md`. Work with the operator to fill the
Frozen Core. Leave Mutable Clarifications empty for discovery during execution.

### 5. Directory Structure

Ensure the project has at minimum:
- `CLAUDE.md`
- `.agent/tasks.jsonl`
- `skills/` (even if empty)
- `docs/` for any project documentation

Preserve existing valid content. Merge, supersede, or migrate. Do not overwrite good
documentation just because the path changes.

### 6. Claude Code Configuration

Create or update Claude Code support files when applicable:
- `.claude/settings.json`
- Hook scripts for known deterministic misstep patterns observed in the project stack

Do not invent hooks without evidence. If a hook needs project policy, flag `[DECISION NEEDED]`.

### 7. Migration Checklist

Produce a single operator-facing checklist covering:
- Files created
- Files updated
- Files superseded
- Unresolved decisions
- Manual follow-up still required

## Process

1. Read `CLAUDE.md` and the target project's existing infrastructure.
2. Compare the project against the operating model.
3. Identify missing, outdated, and conflicting files.
4. Produce updates incrementally, one file at a time.
5. Preserve valid project-specific rules; do not flatten them into generic boilerplate.
6. Flag project-specific ambiguities with `[DECISION NEEDED]`.
7. End with a migration checklist and summary of what changed.

## Constraints

- Do not modify application source code.
- Do not delete valid documentation; supersede or migrate it.
- Match `CLAUDE.md` operating model exactly where the protocol is explicit.
- Prefer root templates over re-inventing project-local variants.
- Keep all scaffolding dense and operational. Avoid decorative prose.
