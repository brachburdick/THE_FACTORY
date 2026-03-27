---
name: debug-flow
description: >
  Use when the task involves fixing a bug, error, regression, failing test,
  unexpected behavior, or production incident. Signals: "fix", "broken",
  "failing", "error", "regression", "not working", "crash", "timeout".
inputs:
  - task entry in .agent/tasks.jsonl with bug description
  - reproduction steps or failing test path (if available)
outputs:
  - fix commit with passing reproduction test
  - run record in .agent/runs.jsonl
success_criteria:
  - reproduction test exists and passes after fix
  - no new test failures (regression-free)
  - root cause documented in commit message
  - run record written with task_id cross-reference
failure_policy: >
  After two fix attempts (2 failed), stop. Escalate to operator via AskUserQuestion
  using the abstain packet format (templates/handoff-packet.md).
---

# Debug Flow

Phases: Reproduce → Isolate → Diagnose → Fix → Verify. Standard debugging — the value below is in the non-obvious parts.

## Pre-Flight
Before writing any code:
1. **Reproduction test exists.** If not, write one. Do NOT proceed without a failing test.
2. **Risk level set** on the task in tasks.jsonl. If missing, classify now.
3. **Baseline tests pass** (except the reproduction). Record pre-existing failures.
4. **No conflicting in-progress tasks** touching the same files.
5. **Prior work check:** Has a prior session partially fixed this? Check state-snapshot.json.

## Non-Obvious Rules
- **Diagnostic before visual.** Run `tsc --noEmit` → console logs → network requests → THEN screenshots. Most rendering bugs are type errors. If visual debugging exceeds 3 cycles without progress, stop and re-diagnose.
- **Version delta first.** When a reference implementation works and yours doesn't, check dependency versions before anything else.
- **Flakiness handling.** If a test fails intermittently, rerun once before consuming a fix-attempt. Log the test name in `eval_failures` in the run record.
- **Separate-context verification.** The context that wrote the fix must NOT be the only context that certifies it. Use a subagent.

## Context Gate
End the session with `result: "partial"` if: turn count > 40, re-reading files, forgetting prior decisions, or working on 2+ objectives.

## Close
1. Set task `status: "complete"`, `flowPhase: "verify"` in tasks.jsonl.
2. Write run record with: `run_id`, `date`, `project_id`, `task_id`, `task_type`, `result` (success|partial|failed|blocked|escalated), `summary`.
3. Git commit: `close: run record + verify for {task-id}`.

## Subagent Policy
Use Agent tool (subagent_type=Explore) for codebase exploration spanning 3+ files. Give each a **specific file scope**. **All Edit/Write operations stay in the main agent.** Subagents are read-only.

## Do NOT
- Refactor while fixing. Separate task.
- Retry more than 2 times without escalating.
- Skip separate-context verification.
- Change test assertions to make them pass.
- Close without a run record.
