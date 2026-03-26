---
status: APPROVED
project_root: [FILL: /absolute/path/to/project]
revision_of: [FILL: artifact path or "none"]
supersedes: [FILL: artifact path(s) or "none"]
superseded_by: [FILL: artifact path(s) or "none"]
dispatch_status: [FILL: READY | READY WITH EXPLICIT ASSUMPTIONS | NOT READY]
---

# Handoff Packet: [FILL: TASK_ID]

## Dispatch
- Mode: [FILL: ORCHESTRATOR DISPATCH | DIRECT DISPATCH]
- Output path: [FILL: exact artifact path this agent must write before ending the session]
- Parallel wave: [FILL: wave ID or "none"]

## Objective
[FILL: One sentence — what must be true when this task is done.]

## Scope Boundary
- Files this agent MAY read/modify:
  - [FILL: explicit file paths or glob patterns]
- Files this agent must NOT touch:
  - [FILL: explicit exclusions]

## Context Files
- [FILL: relevant spec, plan, tasks, interfaces, findings, or skill files]

## Interface Contracts
- [FILL: exact contract file(s), payloads, signatures, or "none"]
- [FILL: if parallel work exists, state ownership split and shared boundary]

## Required Output
- Write: `[FILL: same exact path from Dispatch > Output path]`
- If you supersede an existing artifact, mark it `SUPERSEDED` before session end.
- If you discover backlog-worthy out-of-scope improvements, capture them in `## Follow-Up Items` of the session summary.

## Constraints
- [FILL: non-negotiable rule]
- [FILL: non-negotiable rule]

## Acceptance Criteria
- [ ] [FILL: specific, testable condition]
- [ ] [FILL: specific, testable condition]
- [ ] All pre-existing tests pass

## Dependencies
- Requires completion of: [FILL: TASK_ID(s) or "none"]
- Blocks: [FILL: TASK_ID(s) or "none"]

## Open Questions
- [FILL: unresolved item or "none"]

> If `## Open Questions` is non-empty for a code-changing task, do not dispatch yet.

## Replan Triggers
<!-- If any of these become true during execution, STOP and return to the operator. Do not continue. -->
- A required file or interface referenced in Context Files is missing or has changed shape
- Acceptance criteria conflict with implementation reality
- Unrelated failures block proof of correctness (test infra broken, environment down)
- More than one out-of-scope area must change to complete the task
- A hidden dependency invalidates the plan
- [FILL: task-specific replan trigger or "none beyond defaults"]

## Verification Procedure
<!-- How the Validator (or separate-context verifier) should check this work. -->
- [ ] [FILL: specific check the verifier must perform]
- [ ] [FILL: specific check the verifier must perform]
- [ ] Acceptance criteria from above are independently confirmed
- [ ] No scope violations detected

## Evidence Required
<!-- What proof must exist before this task can be marked complete. -->
- [FILL: e.g., "Passing test output for [test file]"]
- [FILL: e.g., "Screenshot of [UI state]" or "API response matching [shape]"]
- [FILL: or "Acceptance criteria passing is sufficient"]

## Assumptions In Force
<!-- Assumptions accepted for this dispatch. If any are invalidated during execution, trigger replan. -->
- [FILL: assumption — confidence: [HIGH | MEDIUM | LOW], invalidation signal: [what would prove this wrong]]
- [FILL: or "None — all inputs are confirmed"]

---

# Abstain Packet Template

> Use this format when escalating to the operator via AskUserQuestion. Structured
> escalation prevents vague "I'm stuck" messages and gives the operator enough
> context to unblock quickly.

## blocked_because
[FILL: One sentence — what specific condition prevents progress.]

Example: "The spec requires OAuth2 PKCE flow but the auth library (v2.1) doesn't
support PKCE. Upgrading to v3.0 would be a breaking change across 4 consumers."

## missing_evidence
[FILL: What information or decision is needed to proceed.]

Example: "Need operator decision: (a) upgrade auth library to v3.0 and accept
breaking changes, (b) implement PKCE manually using the existing library, or
(c) drop the PKCE requirement and use standard OAuth2."

## recommended_safe_default
[FILL: What the agent would do if forced to continue without operator input.
Must be the most conservative option that doesn't make irreversible changes.]

Example: "If no response: skip PKCE implementation, document it as a known gap
in the spec's Change Log, and continue with standard OAuth2 flow."

## reply_with
[FILL: What format or content the operator's reply should take. Be specific
about what constitutes a sufficient answer.]

Example: "Reply with one of: (a), (b), or (c) from missing_evidence above.
If choosing (a), confirm that breaking change to auth consumers is acceptable."
