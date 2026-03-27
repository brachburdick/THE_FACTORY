---
name: refactor-flow
description: >
  Use when the task involves restructuring code without changing behavior.
  Signals: "refactor", "extract", "consolidate", "clean up", "simplify",
  "reorganize", "dedup", "reduce complexity", "split", "merge module".
inputs:
  - task entry in .agent/tasks.jsonl with refactor scope
  - existing test suite for behavioral baseline
outputs:
  - refactor commits preserving all existing behavior
  - run record in .agent/runs.jsonl
success_criteria:
  - test results identical to baseline (same passes, same failures)
  - no behavioral changes introduced
  - scope stayed within defined refactor boundary
  - run record written with task_id cross-reference
failure_policy: >
  If tests fail after transform and 2 revert-fix cycles don't resolve it,
  stop. Revert to pre-transform state. Escalate to operator using the
  abstain packet format (templates/handoff-packet.md).
---

# Refactor Flow

Phases: Scope → Snapshot → Transform → Verify. Standard refactoring — the value below is in the pre-flight and constraints.

## Pre-Flight (before any code changes)
1. **Preservation criteria exist.** What behavior must NOT change? What structural goals? If missing, ask.
2. **Section assignment.** If files span multiple sections, flag as cross-boundary.
3. **Risk level set** on the task. If missing, classify now.
4. **Baseline tests pass.** Record results as the behavioral snapshot. If coverage is insufficient, write characterization tests FIRST.
5. **No conflicting in-progress tasks** touching the same files.
6. **Ambiguity check.** Flag "clean up", "simplify" WITHOUT structural criteria ("extract X into module", "reduce from N to M lines").

## Non-Obvious Rules
- **Read ALL files in scope** before changing any. Understand current structure first.
- **Incremental transforms.** Run tests after each significant change.
- **Separate-context verification** comparing post-refactor test results to the Phase 2 snapshot.

## Context Gate
End the session with `result: "partial"` if: turn count > 40, re-reading files, forgetting prior decisions, or working on 2+ objectives.

## Close
1. Run full test suite. Results must match baseline (same passes, same failures).
2. Set task `status: "complete"`, `flowPhase: "verify"` in tasks.jsonl.
3. Write run record with: `run_id`, `date`, `project_id`, `task_id`, `task_type`, `result` (success|partial|failed|blocked|escalated), `summary`.
4. Git commit: `close: run record + verify for {task-id}`.
5. **Section check:** Did this refactor move files across section boundaries? Update contracts if needed.

## Subagent Policy
Use Agent tool (subagent_type=Explore) for codebase exploration spanning 3+ files. Give each a **specific file scope**. **All Edit/Write operations stay in the main agent.** Subagents are read-only.

## Do NOT
- Do NOT change behavior during a refactor. Cardinal rule.
- Do NOT add new features. File separate feature tasks.
- Fix bugs found during refactoring. File separate debug-flow tasks.
- Delete tests that "get in the way." Fix the refactor, not the tests.
- Retry more than 2 times without escalating.
- Close without a run record.
