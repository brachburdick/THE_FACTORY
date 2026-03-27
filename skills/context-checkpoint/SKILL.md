---
name: context-checkpoint
description: >
  Use at natural task boundaries (after completing a sub-task, before starting
  a new phase) to compress context. Summarize completed work into a checkpoint
  file and offload details. Signals: "context feels heavy", "turn > 25",
  "compress context", "checkpoint".
---

# Skill: Context Checkpoint

## When to Use

- Turn count exceeds 25 and more work remains
- Context feels degraded (forgotten paths, repeated reads, losing track of decisions)
- After completing a sub-task, before starting a different phase
- Before loading a large new skill or reading many files

This is a **lighter alternative to ending the session**. Use this first; if context
is still degraded after checkpointing, trigger the full context gate (end session).

## Procedure

### 1. Summarize Completed Work

Write a checkpoint file to `.agent/context-checkpoints/{task-id}-{n}.md` where
`{n}` is an incrementing sequence number (start at 1).

The checkpoint should contain:

```markdown
# Checkpoint: {task-id} #{n}

## Completed
- [bullet list of what was done, with file paths]

## Decisions Made
- [key decisions and why]

## Current State
- [what's in progress, what's next]

## Key Locations
- [file paths and line numbers that matter for remaining work]
```

### 2. Update State Snapshot

Add the checkpoint reference to `.agent/state-snapshot.json` under
`session_knowledge.checkpoints`:

```json
{
  "session_knowledge": {
    "checkpoints": ["tf-042-1.md", "tf-042-2.md"]
  }
}
```

### 3. Continue

After writing the checkpoint, you can mentally "release" the detailed context
of completed work. The checkpoint file preserves it for later recovery if needed.

## Rules

- Do NOT checkpoint work that is still in progress — only completed sub-tasks
- Keep checkpoints concise (under 40 lines)
- Include file paths with line numbers for anything you might need to re-find
- If you've already written 3+ checkpoints in one session, use the context gate instead (end session with handoff)
