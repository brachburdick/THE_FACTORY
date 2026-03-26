---
name: feature-flow
description: >
  Use when the task involves building new functionality, adding a capability,
  implementing a user story, creating a new endpoint/resolver/component, or
  extending existing behavior. Signals: "implement", "add", "create", "new",
  "build", "feature", "endpoint", "resolver", "component".
---

# Feature Flow: Intent → Spec → Plan → Implement → Test → Verify

## Phase 0: Intent Check
**Goal:** Confirm the feature has sufficient intent capture before any work begins.
**Steps:**
1. Check that the dispatch has explicit: user/stakeholder, problem statement, desired outcome,
   non-goals, hard constraints, testable acceptance criteria.
2. If a Project Definition Record exists, verify the feature traces to a PDR item.
3. If dispatching with uncertainty, confirm assumptions are stated explicitly.
4. Run the structured questioning protocol if any of these are missing:
   - **Product reality:** What problem does this solve? Who are the target users?
   - **UX intent:** What should the experience feel like? What should it resemble?
   - **Decision boundaries:** What is Always OK / Ask First / Never?
   - **Quality priorities:** Performance, correctness, polish — rank them.
   - **Data and integration:** What external systems, APIs, or data sources?
   - **Evidence plan:** How will we know it works before shipping?
   - **Success criteria:** What are the testable acceptance criteria?

**Gate:** Dispatch readiness met. All required intent fields are explicit. If any are missing,
escalate to operator — do NOT proceed with assumptions.

## Phase 1: Spec
**Goal:** Define what will be built, clearly enough that implementation is mechanical.
**Steps:**
1. Read the task description and any linked requirements.
2. If the feature touches a domain with a domain skill (audio analysis, DMX/lighting,
   GraphQL federation, AWS infra), load that skill now for domain-specific constraints.
3. Write a spec (or confirm one exists) using `templates/spec.md` that includes:
   - Frozen Intent section referencing the PDR
   - Mutable Specification with behavior, inputs, outputs, edge cases, scope boundaries
4. If the spec is ambiguous or missing critical details, ask the human. Do NOT assume.

**Git:** Commit the spec: `spec: {feature name}`.

**Gate:** Spec exists with defined inputs, outputs, edge cases, and scope boundaries.
Human confirmation required before proceeding.

## Phase 2: Plan
**Goal:** Break the spec into ordered implementation steps.
**Steps:**
1. Identify which files need to be created or modified.
2. List implementation steps in dependency order (e.g., schema first, then resolver,
   then tests).
3. Estimate whether this is a single-session task or needs to be broken into sub-tasks
   in the task tracker.
4. If the feature requires changes across multiple projects in the portfolio, identify
   which projects are affected and in what order changes must land.

**Gate:** Implementation plan exists with ordered steps and file list.

## Phase 2.5: Pre-Flight Readiness Check
**Goal:** Verify the task and environment are ready before writing any code. Catches missing
context that causes mid-build reversals, scope creep, and wasted fix-attempts.

**Checklist — all must pass before entering Phase 3:**
1. **Acceptance criteria exist:** The task (in `.agent/tasks.jsonl` or the spec) has testable
   acceptance criteria. If missing, ask the operator — do NOT invent criteria.
2. **Section assignment:** If the project uses sections (`sections/SECTIONS.md`), the task's
   affected files map to a known section. If files span multiple sections, flag this to the
   operator as a cross-boundary change.
3. **Risk level set:** The task has a `risk` field in `.agent/tasks.jsonl` (low/medium/high).
   If missing, classify it now using the risk-classifier heuristics (tf-024).
4. **Baseline tests pass:** Run the test suite for the affected area. If tests are already
   failing, record the pre-existing failures before proceeding — do NOT let them become
   your regressions.
5. **No conflicting in-progress tasks:** Check `.agent/tasks.jsonl` for other `in_progress`
   tasks touching the same files or section. If a conflict exists, coordinate with the
   operator or wait.
6. **Prior work check:** For each file in the plan's scope, check: does it already contain
   the expected changes? Check `.agent/state-snapshot.json` — a prior session may have
   partially completed this work.

**Gate:** All 6 checks pass. If any fail, resolve before entering Phase 3.

## Phase 3: Implement
**Goal:** Build the feature according to the plan.
**Steps:**
1. Follow the plan step by step. Do NOT skip ahead or reorder without updating the plan.
2. After each significant step, run any relevant existing tests to catch regressions early.
3. If you discover the plan is wrong or incomplete, STOP implementation. Update the plan
   first, then resume.

**Git:** Commit implementation: `implement: {summary of what was built}`.

**Gate:** All planned implementation steps are complete.

## Phase 4: Test
**Goal:** Verify the feature works and doesn't break existing functionality.
**Steps:**
1. Write tests that cover the spec's defined behavior, edge cases, and error handling.
2. Run the new tests. All must pass.
3. Run the full test suite for the affected module(s). No regressions.
4. If the feature has a UI component, describe what manual verification the human
   should perform.

5. **Dependency audit:** If you added new `import` statements, verify they're declared in
   `pyproject.toml` (Python) or `package.json` (JS/TS). Transitive deps work in dev but crash in fresh envs.
6. **Capacity documentation:** If the feature accepts unbounded input (batch upload, bulk import),
   document the max tested batch size and expected behavior at the limit.

**Git:** Commit tests: `test: {what is covered}`.

**Gate:** All new tests pass. No regressions in existing tests. New imports are declared dependencies.

## Phase 5: Verify & Close
**Steps:**
1. **Separate-context verification:** Before closing, run a verification step in a
   separate context (subagent or fresh review). The context that wrote the code must
   NOT be the only context that certifies it. Verify against the spec's acceptance
   criteria, not just "does it compile."
2. **Close the task in `.agent/tasks.jsonl`:** Set `status: "complete"`, `flowPhase: "verify"`,
   update `summary` with what was built, and set `updated` to the current ISO timestamp.
   Use the task's `id` field (e.g. `tf-005`) — this is the through-line for traceability.
3. **Write a run record to `.agent/runs.jsonl`** with these required fields:
   `run_id`, `date`, `project_id`, `task_id` (must match the tasks.jsonl `id`),
   `task_type`, `result` (success|partial|failed|blocked|escalated), `summary`.
4. **Git:** Commit the run record: `close: run record + verify for {task-id}`.
5. If the feature introduced a new pattern that future features should follow,
   note it in the relevant domain skill's `references/` directory.
6. If the spec changed during implementation, update the spec to match reality
   and record the change in the spec's Change Log.
7. **Section check:** If the project has `sections/SECTIONS.md`, check whether this feature
   added files outside existing sections, changed a boundary contract, or grew a section
   past the split threshold. Update section contracts if needed.

## Subagent Guidance
When launching parallel Explore subagents for research or exploration:
- Give each agent a **specific file scope** (e.g., "read only `bridge/` files", "read only `frontend/src/components/`"). Do NOT launch two agents with overlapping directories.
- If a codebase orientation skill exists for the project, load it first — it eliminates most exploratory reads.
- Check `.agent/state-snapshot.json` at session start. It contains the branch, last commit, active tasks, and modified files from the prior session. Use it to skip re-exploration.

## Session Scope Budgeting
Before starting Phase 3, estimate whether the feature fits in one session:
- If the spec + plan + implementation + tests + verify will exceed context, split into sub-tasks NOW.
- Prefer splitting at layer boundaries (backend first, frontend second) or by phase (spec+plan in session 1, implement in session 2).
- A feature that requires changes across 3+ layers and includes bug fixes discovered along the way will almost certainly exhaust context. Plan for it.

## Feature Branch Guidance
- Start feature work on a feature branch: `git checkout -b feature/{name}`.
- If a bug is discovered mid-feature that is urgent: commit current feature work, fix the bug on the feature branch (not main), then continue. Do NOT switch to main for the fix — that causes branch abandonment.
- If the bug is unrelated to the feature, note it as a follow-up task rather than fixing it inline.

## Greenfield Variant
For projects scaffolded from scratch in a single session (e.g., a new tool or utility), the phase-by-phase commit protocol creates overhead without proportional value. In this case:
- Commit per-tier (e.g., "scaffold: backend models + API" then "scaffold: frontend components") rather than per-phase.
- Still run the full test + verify cycle before closing.

## Negative Constraints — Do NOT:
- Do NOT start implementing before the spec is confirmed by the human.
- Do NOT combine feature work with refactoring. File a separate refactor task.
- Do NOT write tests before implementation unless explicitly doing TDD.
- Do NOT skip Phase 0 intent check. Missing intent is the #1 cause of mid-build reversals.
- Do NOT silently retry more than 2 times. Log an incident and escalate.
- Do NOT skip the separate-context verification in Phase 5.
- Do NOT proceed past dispatch readiness gate with missing non-goals or constraints.
- Do NOT close the task without a run record in `.agent/runs.jsonl`.
- Do NOT modify the Frozen Intent section of the spec without operator approval.
