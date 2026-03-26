# Context Checkpointing Research

**Task:** tf-069
**Date:** 2026-03-27
**Status:** Research — prototype when validated by usage patterns

## Problem

Each new Claude Code session starts cold. The state-snapshot.py hook captures
branch, commit, tasks, and modified files — but not the *reasoning* that led
to the current state. This creates a 10% ramp-up tax (per conversation mining)
where agents re-read files, re-discover constraints, and re-derive conclusions
that the previous session already worked through.

## What State-Snapshot Already Captures

```json
{
  "branch": "v3.0",
  "last_commit": "abc123",
  "modified_files": ["src/main.py"],
  "active_tasks": [...]
}
```

This is the **what** — what files changed, what tasks are active. Missing is
the **why** — why those files were changed, what alternatives were considered,
what constraints were discovered.

## Proposed: Session Knowledge Capture

At session end, write a lightweight knowledge checkpoint to
`.agent/session-knowledge/` containing:

### 1. Files Read (with purpose)

```json
{
  "files_read": [
    {"path": "src/auth.py", "purpose": "understand current token handling"},
    {"path": "tests/test_auth.py", "purpose": "identify existing test coverage"}
  ]
}
```

**Why:** The next session can skip reading files that were already
understood and haven't changed since (check git diff).

### 2. Decisions Made

```json
{
  "decisions": [
    {
      "decision": "Use JWT instead of session cookies",
      "rationale": "Stateless auth needed for horizontal scaling",
      "alternatives_considered": ["session cookies", "OAuth tokens"],
      "constraints": ["must work behind load balancer"]
    }
  ]
}
```

**Why:** Re-deriving decisions is the biggest source of ramp-up waste.
A decision log lets the next session adopt prior conclusions.

### 3. Hypotheses (confirmed and rejected)

```json
{
  "hypotheses": [
    {
      "hypothesis": "Bug is caused by race condition in db write",
      "status": "rejected",
      "evidence": "Added logging, writes are sequential"
    },
    {
      "hypothesis": "Bug is in the cache invalidation path",
      "status": "confirmed",
      "evidence": "Cache TTL was set to 0, never refreshes"
    }
  ]
}
```

**Why:** Dead ends are the second biggest ramp-up cost. If a prior session
already ruled out a hypothesis, the next session shouldn't re-investigate it.

### 4. Open Questions

```json
{
  "open_questions": [
    "Does the auth middleware handle token refresh?",
    "Is there a rate limit on the external API?"
  ]
}
```

**Why:** Explicit continuity markers so the next session knows what to
investigate first.

## Schema

```json
{
  "session_id": "abc-123",
  "timestamp": "2026-03-27T06:00:00Z",
  "task_ids": ["tf-069"],
  "files_read": [...],
  "decisions": [...],
  "hypotheses": [...],
  "open_questions": [...],
  "duration_minutes": 45
}
```

## Implementation Options

### Option A: Hook-based (automatic)

Extend state-snapshot.py to extract knowledge from the conversation
transcript. Parse tool calls (Read → files_read), AskUserQuestion calls
(→ decisions/open questions), and diagnostic patterns (→ hypotheses).

**Pro:** Zero agent effort, always captured.
**Con:** Extraction quality depends on parsing heuristics. Can't capture
reasoning that wasn't explicitly stated.

### Option B: Skill-based (agent-driven)

Add a "checkpoint" skill that agents invoke at session end. The skill
prompts the agent to summarize decisions, hypotheses, and open questions.

**Pro:** Higher quality — the agent knows its own reasoning.
**Con:** Requires agent discipline. Can be skipped under context pressure.

### Option C: Hybrid (recommended)

- Hook captures files_read automatically (parse Read tool calls)
- Agent invokes checkpoint skill for decisions/hypotheses/questions
- Both write to the same `.agent/session-knowledge/` directory

## Storage

- One file per session: `.agent/session-knowledge/{session-id}.json`
- Prune after 30 days (old knowledge is stale)
- Index in a manifest: `.agent/session-knowledge/index.jsonl`
- At session start, read the most recent checkpoint for the active task

## Metrics to Track

Before building, measure the baseline:
- How many Read tool calls are repeats of prior sessions? (parse transcripts)
- How often do agents re-derive the same conclusions? (compare decision logs)
- What % of ramp-up time is spent on already-resolved questions?

These metrics determine whether checkpointing is worth the overhead.

## Risks

| Risk | Mitigation |
|---|---|
| Stale knowledge misleads next session | Always check git diff since checkpoint, flag stale files |
| Checkpoint is too verbose | Cap at 20 entries per category |
| Agent skips checkpoint under context pressure | Hook captures minimum (files_read) automatically |
| Knowledge capture adds overhead | Keep format simple, < 100 lines of JSON |

## Next Steps

1. Analyze 10 recent session transcripts for repeat-read patterns
2. If > 20% of Read calls are repeats, prototype Option C
3. Run 5 sessions with checkpointing, measure ramp-up reduction
4. If ramp-up drops by > 30%, integrate into session protocol
