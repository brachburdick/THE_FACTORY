---
name: refactor-flow
description: >
  Use when the task involves restructuring code without changing behavior.
  Signals: "refactor", "extract", "consolidate", "clean up", "simplify",
  "reorganize", "dedup", "reduce complexity", "split", "merge module".
---

# Refactor Flow: Scope → Snapshot → Transform → Verify

## Phase 1: Scope
**Goal:** Define exactly what will change and what must be preserved.
**Steps:**
1. Read the refactor request. Identify the target code.
2. Read ALL files in the affected area. Understand the current structure before changing it.
3. Define the refactor boundary:
   - What files/modules are in scope?
   - What behavior must be preserved? (List specific tests or observable behaviors.)
   - What is explicitly out of scope?
4. If the refactor crosses project boundaries, identify all affected projects.

**Gate:** Scope boundary is defined. Preservation criteria are stated.

## Phase 2: Snapshot
**Goal:** Establish a behavioral baseline before any changes.
**Steps:**
1. Run the existing test suite for the affected area. Record results.
2. If test coverage is insufficient to verify behavior preservation, write
   characterization tests FIRST that capture current behavior.
3. **Git:** Commit characterization tests separately: `snapshot: characterization tests for {area}`.

**Gate:** Test suite passes. You have sufficient coverage to detect behavioral changes.

## Phase 3: Transform
**Goal:** Restructure the code while preserving all behavior.
**Steps:**
1. Make structural changes incrementally. After each significant change, run tests.
2. Do NOT change behavior. If you find a bug while refactoring, file a separate
   bug fix task. Do NOT fix it as part of the refactor.
3. Do NOT add new features. If the refactored structure enables a new capability,
   file a separate feature task.

**Git:** Commit the transform: `refactor: {summary of structural change}`.

**Gate:** All structural changes are complete. Tests still pass.

## Phase 4: Verify & Close
**Steps:**
1. Run the full test suite. Compare results to the Phase 2 snapshot.
   Results must be identical (same passes, same failures — no new failures,
   no mysteriously fixed tests).
2. **Separate-context verification:** Before closing, run a verification step in a
   separate context (subagent or fresh review). The context that performed the
   refactor must NOT be the only context that certifies behavior preservation.
3. Update task tracker: `status: complete`, attach summary of structural changes.
4. Write a run record to `.agent/runs.jsonl`.
5. **Git:** Commit the run record: `close: run record + verify for {task-id}`.
6. If the refactor established a new pattern (e.g., extracted a component library,
   established a service boundary), document it in the relevant domain skill or
   project CLAUDE.md gotchas section.

## Negative Constraints — Do NOT:
- Do NOT change behavior during a refactor. This is the cardinal rule.
- Do NOT skip the snapshot phase. Without a baseline, you can't verify preservation.
- Do NOT refactor and add features simultaneously. Ever.
- Do NOT fix bugs found during refactoring. File them as separate debug-flow tasks.
- Do NOT silently retry more than 3 times. Log an incident and escalate.
- Do NOT skip the separate-context verification in Phase 4.
- Do NOT close the task without a run record in `.agent/runs.jsonl`.
- Do NOT expand scope beyond the defined refactor boundary without updating the plan.
- Do NOT delete tests that "get in the way" of the refactor. Fix the refactor, not the tests.
