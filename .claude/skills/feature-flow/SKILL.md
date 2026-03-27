---
name: feature-flow
description: >
  Use when the task involves building new functionality, adding a capability,
  implementing a user story, creating a new endpoint/resolver/component, or
  extending existing behavior. Signals: "implement", "add", "create", "new",
  "build", "feature", "endpoint", "resolver", "component".
inputs:
  - task entry in .agent/tasks.jsonl with feature description
  - spec document (templates/spec.md) or sufficient intent for Phase 0
outputs:
  - implementation commits with tests
  - run record in .agent/runs.jsonl
success_criteria:
  - spec exists with defined inputs, outputs, edge cases
  - all acceptance criteria covered by tests
  - all tests pass, no regressions
  - run record written with task_id cross-reference
failure_policy: >
  After 2 failed implementation attempts, stop. Escalate to operator
  using the abstain packet format (templates/handoff-packet.md).
---

# Feature Flow

Phases: Intent → Spec → Plan → Implement → Test → Verify. Standard feature development — the value below is in the pre-flight and non-obvious parts.

## Intent Check (Phase 0)
Confirm the dispatch has: user/stakeholder, problem statement, desired outcome, non-goals, constraints, testable acceptance criteria. If any are missing, ask — do NOT assume.

## Pre-Flight (before writing code)
1. **Acceptance criteria exist** and are testable. If missing, ask the operator.
2. **Section assignment.** If files span multiple sections, flag as cross-boundary.
3. **Risk level set** on the task. If missing, classify now.
4. **Baseline tests pass.** Record pre-existing failures.
5. **No conflicting in-progress tasks** touching the same files.
6. **Prior work check.** Check state-snapshot.json — changes may already exist from a prior session.
7. **Ambiguity check.** Flag vague terms ("improve", "optimize") WITHOUT quantified criteria.

## Non-Obvious Rules
- **Spec before code.** Human confirmation required before implementation.
- **Session scope budgeting.** If spec + plan + implement + tests > context window, split NOW.
- **Dependency audit.** New `import` statements must be declared in pyproject.toml / package.json.
- **Separate-context verification** against spec criteria, not just "does it compile."

## Context Gate
End the session with `result: "partial"` if: turn count > 40, re-reading files, forgetting prior decisions, or working on 2+ objectives.

## Close
1. Set task `status: "complete"`, `flowPhase: "verify"` in tasks.jsonl.
2. Write run record with: `run_id`, `date`, `project_id`, `task_id`, `task_type`, `result` (success|partial|failed|blocked|escalated), `summary`. Also: `operator_interventions`, `agent_escalations`.
3. Git commit: `close: run record + verify for {task-id}`.
4. **Section check:** Did this feature add files outside existing sections? Update contracts if needed.

## Subagent Policy
Use Agent tool (subagent_type=Explore) for codebase exploration spanning 3+ files. Give each a **specific file scope**. **All Edit/Write operations stay in the main agent.** Subagents are read-only.

## Do NOT
- Do NOT start implementing before the spec is confirmed by the human.
- Combine feature work with refactoring.
- Skip Phase 0 intent check.
- Retry more than 2 times without escalating.
- Close without a run record.
