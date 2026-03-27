# Task Lifecycle

What happens when a task is started, worked on, and completed in THE_FACTORY.

## Overview

Every Claude Code session follows the same lifecycle: boot → claim → work → land.
Hooks enforce guardrails at every stage — the agent doesn't need to remember the rules.

**Core principle:** Hooks enforce, skills inform.

## Phase 1: Session Start

```
┌──────────────────────────────────────────────────────────────────┐
│                       SESSION BOOT                               │
│                                                                  │
│  1. Load CLAUDE.md (pipeline + project)                         │
│  2. Read .agent/state-snapshot.json (prior session context)     │
│  3. Read .agent/tasks.jsonl → ready.py picks next unblocked     │
│  4. Read .agent/questions.jsonl (answered Qs from operator)     │
│  5. check-read-state.py --stale-only (skip fresh files)         │
│  6. Read LEARNINGS.md (env constraints)                         │
│  7. Load codebase orientation skill (if working in a project)   │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
```

The state snapshot carries forward decisions, dead ends, and key file locations from the
prior session so the agent doesn't re-explore from scratch.

## Phase 2: Claim Task

```
┌──────────────────────────────────────────────────────────────────┐
│                       CLAIM TASK                                 │
│                                                                  │
│  Set status: "in_progress" in tasks.jsonl                       │
│                                                                  │
│  Flow-route by signal word:                                     │
│    fix / bug / error    → .claude/skills/debug-flow/            │
│    implement / add      → .claude/skills/feature-flow/          │
│    refactor / extract   → .claude/skills/refactor-flow/         │
│                                                                  │
│  Load matching flow skill                                       │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
```

The task ID is referenced in all commits, run records, and incident logs for
traceability.

## Phase 3: Work Loop

Every tool call passes through a gauntlet of hooks before and after execution.

### Pre-checks on Edit / Write

```
┌──────────────────────────────────────────────────────────────────┐
│                PreToolUse hooks (Edit / Write)                   │
│                                                                  │
│  ┌─ risk-classifier ───┐  Is task high-risk?                    │
│  │  Reads task risk     │  YES → BLOCK without approved plan    │
│  └─────────────────────┘  NO  → pass                           │
│                                                                  │
│  ┌─ blast-radius ──────┐  File in section's owned_paths?        │
│  │  Checks scope        │  NO  → BLOCK (out of scope)          │
│  └─────────────────────┘  YES → pass                           │
│                                                                  │
│  ┌─ fix-attempt-tracker┐  >2 edits without test run?            │
│  │  Mutation counter    │  YES → BLOCK (run tests first)       │
│  │  Budget: 10/phase    │  >10 total mutations? → BLOCK        │
│  │  Circuit: 4 cycles   │  >4 edit-test loops? → BLOCK         │
│  │          10 files    │  >10 unique files? → BLOCK           │
│  └─────────────────────┘                                        │
│                                                                  │
│  ┌─ plan-gate ─────────┐  Phase gate requires approval?         │
│  └─────────────────────┘  YES → pause for operator             │
│                                                                  │
│  ┌─ build-integrity ───┐  Editing infra file?                   │
│  └─────────────────────┘  YES → WARN (non-blocking)            │
│                                                                  │
│  ┌─ reference-check ───┐  String appears in evals/hooks?        │
│  └──── (Edit only) ────┘  YES → WARN (advisory)               │
└──────────────────────────────────────────────────────────────────┘
```

### Pre-checks on Bash

```
┌──────────────────────────────────────────────────────────────────┐
│                PreToolUse hooks (Bash)                            │
│                                                                  │
│  git-guard.sh           No commits to main, no force-push,      │
│                         no reset --hard                          │
│                                                                  │
│  fix-attempt-tracker    Counts mutations toward budget           │
│                                                                  │
│  bash-risk-logger.sh    Logs command for audit trail             │
│                                                                  │
│  LLM risk classifier    SAFE → allow                            │
│                         MODERATE → allow + log                   │
│                         DANGEROUS → ask user                    │
└──────────────────────────────────────────────────────────────────┘
```

### Post-mutation tracking

```
┌──────────────────────────────────────────────────────────────────┐
│                PostToolUse hooks                                 │
│                                                                  │
│  After Edit/Write:                                              │
│    mid-session-snapshot.py   Every 15 mutations → atomic write  │
│                              of state-snapshot.json              │
│                                                                  │
│  After Read:                                                    │
│    read-state-logger.py      Tracks which files were read       │
│                              (enables stale-file detection)     │
└──────────────────────────────────────────────────────────────────┘
```

### When blocked by uncertainty

```
┌──────────────────────────────────────────────────────────────────┐
│  Write question → .agent/questions.jsonl                        │
│  Move to next ready task via ready.py                           │
│  (Never wait in-session for operator answers)                   │
└──────────────────────────────────────────────────────────────────┘
```

### Context checkpoint (mid-session)

When context feels heavy (turn > 25) or between major sub-tasks, the agent
can load `skills/context-checkpoint/SKILL.md` to compress completed work:

```
┌──────────────────────────────────────────────────────────────────┐
│  Context Checkpoint (skills/context-checkpoint/SKILL.md)        │
│                                                                  │
│  1. Summarize completed work                                    │
│  2. Write → .agent/context-checkpoints/{task-id}-{n}.md         │
│  3. Update state-snapshot.json with checkpoint reference         │
│  4. Continue with compressed context                            │
│                                                                  │
│  Triggers: turn > 25, between phases, before big sub-task       │
└──────────────────────────────────────────────────────────────────┘
```

### Sub-agent concurrency

When spawning sub-agents (Agent tool), limit to 3 concurrent. Read-only
agents (Explore, Plan) may run in parallel. Agents that produce artifacts
run sequentially. See `skills/index.json` for the full skill inventory.

## Phase 4: Session End

```
┌──────────────────────────────────────────────────────────────────┐
│                       SESSION LANDING                            │
│                                                                  │
│  Stop hooks:                                                    │
│    langfuse-trace.py     Send session metrics to Langfuse       │
│    audit-run-record.sh   WARN if no run record was written      │
│                                                                  │
│  SessionEnd hooks:                                              │
│    state-snapshot.py     Persist: branch, commit, tasks,        │
│                          modified files, decisions, dead ends   │
│                                                                  │
│  Agent responsibilities:                                        │
│    Write run record → .agent/runs.jsonl (with task ID)          │
│    Set task status → "complete" in tasks.jsonl                  │
└──────────────────────────────────────────────────────────────────┘
```

## Three-Loop Model

The hooks above operate at different speeds:

| Loop | Speed | What enforces it | Gate type |
|------|-------|------------------|-----------|
| **Inner** (edit → test → fix) | Seconds | fix-attempt-tracker, lint, unit tests | Automatic |
| **Middle** (design → implement → integrate) | Minutes | blast-radius, plan-gate, risk-classifier | Semi-automatic (hooks + operator) |
| **Outer** (release → observe → learn) | Days | assess.py trends, run record analysis | Operator-driven |

## Hook Summary

| Hook | Trigger | Behavior | Blocking? |
|------|---------|----------|-----------|
| `git-guard` | Bash | No main commits, force-push, reset --hard | Yes |
| `fix-attempt-tracker` | Edit/Write/Bash | 2-cap, 10 budget, 4-cycle / 10-file circuit breaker | Yes |
| `risk-classifier` | Edit/Write | Blocks high-risk mutations without approved plan | Yes |
| `blast-radius` | Edit/Write | Blocks out-of-scope file mutations | Yes |
| `plan-gate` | Edit/Write | Pauses at phase gates for operator approval | Yes |
| `build-integrity` | Edit/Write | Warns on infra file edits | No (warn) |
| `reference-check` | Edit | Warns if renamed string exists in evals/hooks | No (warn) |
| `bash-risk-logger` | Bash | Logs commands | No (log) |
| `LLM risk classifier` | Bash | Classifies SAFE/MODERATE/DANGEROUS | Asks on DANGEROUS |
| `mid-session-snapshot` | Edit/Write (post) | Atomic state snapshot every 15 mutations | No (passive) |
| `read-state-logger` | Read (post) | Tracks file reads for staleness detection | No (passive) |
| `langfuse-trace` | Stop | Sends session metrics | No (passive) |
| `audit-run-record` | Stop | Warns if no run record written | No (warn) |
| `state-snapshot` | SessionEnd | Persists full session state | No (passive) |
