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

## Phase 2.5: Pre-Implementation Checklist
**Goal:** Avoid re-implementing work that already exists.
**Steps:**
1. For each file in the plan's scope, check: does it already contain the expected changes?
2. If code already exists for a planned step, mark that step as done and verify it works.
3. Check `.agent/state-snapshot.json` — a prior session may have partially completed this work.

This phase was added because conversation mining found agents spending ~40% of context
re-reading code only to discover tasks were already implemented.

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

**Git:** Commit tests: `test: {what is covered}`.

**Gate:** All new tests pass. No regressions in existing tests.

## Phase 5: Verify & Close
**Steps:**
1. **Separate-context verification:** Before closing, run a verification step in a
   separate context (subagent or fresh review). The context that wrote the code must
   NOT be the only context that certifies it. Verify against the spec's acceptance
   criteria, not just "does it compile."
2. Update task tracker: `status: complete`, attach summary of what was built.
3. Write a run record to `.agent/runs.jsonl`.
4. **Git:** Commit the run record: `close: run record + verify for {task-id}`.
5. If the feature introduced a new pattern that future features should follow,
   note it in the relevant domain skill's `references/` directory.
5. If the spec changed during implementation, update the spec to match reality
   and record the change in the spec's Change Log.

## Subagent Guidance
When launching parallel Explore subagents for research or exploration:
- Give each agent a **specific file scope** (e.g., "read only `bridge/` files", "read only `frontend/src/components/`"). Do NOT launch two agents with overlapping directories.
- If a codebase orientation skill exists for the project, load it first — it eliminates most exploratory reads.
- Check `.agent/state-snapshot.json` at session start. It contains the branch, last commit, active tasks, and modified files from the prior session. Use it to skip re-exploration.

## Negative Constraints — Do NOT:
- Do NOT start implementing before the spec is confirmed by the human.
- Do NOT combine feature work with refactoring. File a separate refactor task.
- Do NOT write tests before implementation unless explicitly doing TDD.
- Do NOT skip Phase 0 intent check. Missing intent is the #1 cause of mid-build reversals.
- Do NOT silently retry more than 3 times. Log an incident and escalate.
- Do NOT skip the separate-context verification in Phase 5.
- Do NOT proceed past dispatch readiness gate with missing non-goals or constraints.
- Do NOT close the task without a run record in `.agent/runs.jsonl`.
- Do NOT modify the Frozen Intent section of the spec without operator approval.
