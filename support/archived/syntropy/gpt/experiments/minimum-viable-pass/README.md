# SYNTROPY Minimum Viable Pass

**Date:** 2026-03-22
**Purpose:** Dial SYNTROPY back to a "good enough" starting point, then test whether that starting point can solve a trivial software task.

---

## Why This Exists

The meta-chain can expand indefinitely.

This experiment package exists to answer a smaller question:

> what is the shallowest useful starting layer that still preserves intent, uses real verification, and can solve a trivial case?

If that shallow layer works, we can iterate upward only when needed.

---

## The Layer Ladder

### L0. Raw executor

- task brief only
- no explicit acceptance criteria
- no explicit planning
- verify only if the model remembers to

### L1. Goal + acceptance criteria

- task brief
- explicit acceptance criteria
- end-of-task verification
- still no explicit leaf planning

### L2. Good-enough starter model

- single agent
- explicit goal and acceptance criteria
- maximum 3-step plan
- one leaf at a time
- external verification after each meaningful change
- local replan allowed if verification fails

This is the recommended starting point.

### L3. Light decomposition model

- everything in L2
- lightweight leaf contract per step:
  - objective
  - artifact
  - verifier
  - dependency

### L4. Full SYNTROPY

- richer artifact set
- broader decomposition scorecard
- stronger boundary reasoning
- explicit coverage maps
- more formal replanning and comparative experiments

---

## Recommendation

Start at **L2**.

Why:

- It preserves the core of SYNTROPY without most of the overhead.
- It keeps acceptance criteria in view.
- It forces real verification.
- It is small enough to use reliably.
- It is easy to compare against L1 and L3 on the same tasks.

L2 is the best "good enough" starting point because it keeps the load-bearing parts and cuts most of the meta-structure.

---

## First Experiment

### Objective

Test whether the L2 starter model can solve a trivial software task with clear acceptance criteria and external verification.

### Case

`case-001-slugify`

This case asks the model to implement a small `slugify_title` utility in one file and satisfy a small unit-test suite.

Use [EXECUTION_PLAN.md](./case-001-slugify/EXECUTION_PLAN.md) to run the case from a clean starting state.

### Success Criteria

- all tests pass
- no more than 3 explicit plan steps
- no more than 1 local replan
- no extra artifacts beyond the task brief, tiny plan, and test output

### What This Does Not Prove

It does not prove full SYNTROPY.

It only proves that a shallow starting layer is enough to get off the ground on a trivial case.

That is useful because progress requires a floor, not a grand theory.

---

## Suggested Next Comparisons

Run the same trivial case across:

1. L1
2. L2
3. L3

Measure:

- pass/fail
- number of replans
- number of artifacts created
- time to green tests
- subjective overhead

If L2 beats L1 without feeling much heavier, keep it.
If L3 does not beat L2 on trivial cases, do not start there.
