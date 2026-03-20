# Meta-Layer Recommendations for THE_FACTORY

Date: 2026-03-20
Purpose: Extract the highest-value changes from the two META-LAYER research documents and map them onto THE_FACTORY's current root protocol.

## Inputs Reviewed

- `support/v1.9/Improvement Research/META-LAYER research - claude`
- `support/v1.9/Improvement Research/META-LAYER research - gpt.md`
- `README.md`
- `INIT.md`
- `OPERATOR_PROTOCOL.md`
- `IMPLEMENTATION_PROMPT.md`
- `PROTOCOL_REVIEW_PROMPT.md`
- root `templates/`

## Executive Decision

THE_FACTORY should adopt a lightweight meta-project control plane above execution work.

That control plane should formalize:

1. structured intent capture,
2. explicit assumptions and unknowns,
3. evidence-driven review between execution waves,
4. and a stronger dispatch-readiness gate.

It should not introduce a large new cast of standing roles, and it should not turn the system into a heavyweight spec-as-source workflow.

## What THE_FACTORY Already Has

The current protocol already contains strong pieces of this architecture:

- artifact-first coordination,
- ask-don't-assume behavior,
- a Feature Rationale Check before detailed spec work,
- explicit validation and QA gates,
- an Orchestrator state artifact,
- and a protocol-improvement loop.

Those pieces are good and should stay.

The gap is that THE_FACTORY is still stronger at execution governance than at project-definition governance. It lacks one durable artifact for "what we currently believe about the product" and one explicit artifact for "what implementation just taught us."

## What To Take From The Research

### 1. Add a stable project-definition artifact

Take directly:

- the research consensus that elicitation is iterative,
- the frozen/stable-core idea,
- explicit non-goals and constraints,
- quality priorities,
- UX intent,
- decision-right boundaries,
- and tagged assumptions / known unknowns.

Recommended implementation:

- Add `PROJECT_DEFINITION_RECORD.md` as a project-level artifact.
- Make it the durable intent record that sits above feature specs.
- Use a two-part structure:
  - `Frozen Core`: operator-authored problem, users, outcomes, non-goals, hard constraints.
  - `Mutable Clarifications`: agent-added clarifications, discovered requirements, approved refinements, and assumption updates.

Minimum fields:

- Problem statement
- Target users / stakeholders
- Key scenarios / jobs-to-be-done
- Desired outcomes
- Success metrics
- Non-goals
- Hard constraints
- Quality priorities
- UX intent
- Decision rights
- Known assumptions with confidence
- Known unknowns with discovery path

Why this matters in THE_FACTORY:

- `INIT.md` and the Pre-Bootstrap Brief collect some of this.
- Phase 3.5 Feature Rationale collects some of this.
- `spec.md` captures feature behavior.

But there is no single durable project-definition artifact that survives across discovery, planning, and implementation without being rewritten into a new shape every time.

### 2. Add an explicit evidence-review artifact

Take directly:

- the outer-loop review concept,
- evidence-based revision,
- drift detection,
- and the recommendation to update direction based on prototypes, QA, and implementation surprises.

Recommended implementation:

- Add `EVIDENCE_REVIEW_PACKET.md`.
- Generate it at event-driven checkpoints, not after every micro-task.

Minimum fields:

- What changed since last review
- Evidence observed
- Assumptions invalidated
- Assumptions strengthened
- New questions surfaced
- Requirement changes proposed
- UX changes proposed
- Architecture/plan changes proposed
- Do not change yet
- Next-slice recommendation
- Dispatch status: `READY | READY WITH EXPLICIT ASSUMPTIONS | NOT READY`

Why this matters in THE_FACTORY:

- `docs/agents/orchestrator-state.md` is already a status ledger.
- Session summaries already record task-local execution.
- Validator and QA verdicts already record task-level verification.

What is missing is the artifact that turns those raw signals into revised project understanding.

### 3. Keep the role model flat

Take directly:

- the warning from both research documents that more roles are not the answer,
- and the recommendation to implement this as a control-plane routine rather than a new org chart.

Recommended implementation:

- Do not add a standing "Meta Manager," "Requirements Governor," or "Review Agent" role.
- Implement this as either:
  - an expanded Architect/Orchestrator workflow in the current v1.8 protocol, or
  - a future `discovery-governance` flow skill if the v1.9 flow-skill direction becomes canonical.

This fits the current protocol's own rule: prefer a checklist, mode, or skill before adding a new role.

### 4. Strengthen the questioning protocol before dispatch

Take directly:

- the finding that structured clarification beats vague briefing,
- the value of deliberate ambiguity surfacing,
- and the importance of prototypes/examples as elicitation tools.

Recommended implementation:

- Expand the current `INIT.md` and Phase 3.5 Feature Rationale Check with a mandatory question set.

Required question categories:

- Product reality: user pain, users, obvious value, failure mode
- UX intent: feeling, acceptable friction, betrayal points, trust expectations
- Decision boundaries: what agents may infer, what must be escalated
- Quality priorities: speed, clarity, reliability, polish, explainability, reversibility, cost
- Evidence plan: what can only be learned after a prototype, and what artifact will teach it

This should become a repeatable protocol step, not just a good Architect session when someone happens to ask strong questions.

### 5. Upgrade dispatch readiness from "fully specified task" to "safe-to-build slice"

Take directly:

- the research recommendation that execution should not begin until the next slice is explicitly safe,
- plus the idea of `READY / READY WITH EXPLICIT ASSUMPTIONS / NOT READY`.

Recommended implementation:

- Expand the existing Dispatch Readiness Gate in `OPERATOR_PROTOCOL.md`.

Add checks for:

- explicit user / problem / outcome,
- explicit non-goals,
- explicit hard constraints,
- explicit success signal for the next slice,
- explicit unresolved assumptions if dispatch proceeds anyway,
- and an explicit operator decision when the slice is going out with accepted uncertainty.

This is the cleanest way to reduce assumption drift without blocking all progress until full certainty.

### 6. Make review cadence event-driven

Take directly:

- the recommendation to review when reality changes understanding, not on a fixed timer.

Recommended implementation:

Run an Evidence Review when any of these happens:

- after the first clickable or runnable prototype,
- after the first end-to-end thin slice,
- after notable operator discomfort with the UX,
- after an architectural surprise,
- after repeated Validator or QA failure patterns,
- after 2-5 uncertain execution tasks,
- before committing to a large implementation batch.

This should become a formal outer-loop checkpoint between execution waves.

### 7. Add assumption tracking and traceability

Take directly:

- the frozen/mutable spec logic,
- explicit changedelta handling,
- and requirement traceability.

Recommended implementation:

- Add an `Assumptions In Force` section to handoff packets when needed.
- Add confidence-tagged assumptions to the Project Definition Record.
- Require Evidence Review Packets to say which assumptions were invalidated or strengthened.
- Require revised specs or plans to cite which project-definition item or evidence packet caused the revision.

THE_FACTORY already values artifact lineage. This extends that lineage to intent changes, not just implementation artifacts.

### 8. Extend protocol evals to cover intent quality

Take directly:

- the research emphasis on measuring whether the layer actually reduces waste.

Recommended implementation:

Add these metrics to the existing lightweight protocol evals:

- number of `[ASK OPERATOR]` incidents discovered late,
- number of mid-build requirement reversals,
- Validator or QA failures caused by missing intent,
- operator-reported UX dissatisfaction,
- assumption invalidation frequency,
- and how often work dispatches as `READY WITH EXPLICIT ASSUMPTIONS`.

If those do not improve, the meta layer is adding ceremony without value.

## What To Adapt Rather Than Copy Literally

### 1. Do not add a separate `progress.md`

The Claude research recommended a distinct progress ledger.

For THE_FACTORY, that should be adapted, not copied directly.

Reason:

- `docs/agents/orchestrator-state.md` already serves as the durable project-status ledger.
- session summaries already provide cycle-level execution logs.

Recommendation:

- keep the Orchestrator State Snapshot as the progress ledger,
- and add the Evidence Review Packet as the learning ledger.

That avoids duplicate bookkeeping.

### 2. Do not replace feature `spec.md` with the Project Definition Record

The new artifact should sit above feature specs, not replace them.

Recommended separation:

- `PROJECT_DEFINITION_RECORD.md` = project intent, boundaries, assumptions, quality priorities
- `spec.md` = feature behavior and implementation-facing requirements
- `plan.md` / `tasks.md` = execution decomposition
- `EVIDENCE_REVIEW_PACKET.md` = what reality just taught us

### 3. Do not turn every task into a re-planning ceremony

The research supports iterative review, but it also warns against overhead.

Recommendation:

- only trigger the outer loop when evidence meaningfully changes understanding,
- not after every isolated implementation task.

## What Not To Take

- Do not add multiple permanent meta-layer personas.
- Do not move to full spec-as-source development.
- Do not let agents rewrite the whole project narrative after every learning event.
- Do not make review sessions produce documents with no routing consequence.
- Do not let assumptions remain implicit once discovered.

## Concrete Changes Needed In THE_FACTORY

### Root protocol and prompts

`OPERATOR_PROTOCOL.md`

- Add a new artifact schema for `PROJECT_DEFINITION_RECORD.md`.
- Add a new artifact schema for `EVIDENCE_REVIEW_PACKET.md`.
- Expand Phase 1 and Phase 3.5 to formalize structured discovery questions.
- Add an event-driven outer-loop review step between execution waves.
- Expand Dispatch Readiness Gate with intent and assumption checks.
- State explicitly that `docs/agents/orchestrator-state.md` is the status ledger and the Evidence Review Packet is the learning ledger.

`INIT.md`

- Change the Pre-Bootstrap Brief from a light summary into a seed for the Project Definition Record.
- Add required prompts for UX intent, decision boundaries, quality priorities, and known assumptions / unknowns.

`README.md`

- Describe the meta layer as part of the standard startup path.
- Make clear that the system has both execution artifacts and discovery / review artifacts.

`IMPLEMENTATION_PROMPT.md`

- Require the Protocol Enforcer to create templates for the two new artifacts.
- Require startup prompts to load the Project Definition Record in discovery, architecture, and orchestration phases.

`PROTOCOL_REVIEW_PROMPT.md`

- Add review questions for failures caused by weak discovery, missing assumptions, or missing evidence-review checkpoints.

### Root templates

Add:

- `templates/project-definition-record.md`
- `templates/evidence-review-packet.md`

Update:

- `templates/handoff-packet.md` to support `Assumptions In Force` and dispatch status when needed
- `templates/orchestrator-state.md` to reference the latest evidence review packet
- `templates/spec.md` and `templates/plan.md` to reference upstream project-definition items or evidence packets when revised

## Immediate Housekeeping Issues Exposed By This Review

These are not the main meta-layer recommendations, but they should be fixed before rollout because they will create confusion:

1. Root documentation repeatedly references `PROTOCOL_IMPROVEMENTS.md`, but that file is not present at the root.
2. `OPERATOR_PROTOCOL.md` requires YAML frontmatter for durable artifacts, but `templates/spec.md` still uses blockquote metadata.
3. `OPERATOR_PROTOCOL.md` describes a meta-level `constitution.md`, but no root `constitution.md` currently exists.

The meta-layer work will be easier if those inconsistencies are cleaned up first.

## Recommended Rollout Order

### Phase A: Minimal pilot

1. Add `PROJECT_DEFINITION_RECORD.md`
2. Add `EVIDENCE_REVIEW_PACKET.md`
3. Expand Dispatch Readiness Gate
4. Pilot on one new feature or one new project bootstrap

### Phase B: Protocol integration

1. Update root prompts and templates
2. Update startup prompts to load the new artifacts
3. Add event-driven review triggers to the workflow
4. Add intent-quality metrics to protocol evals

### Phase C: Keep only what earns its cost

After a small pilot, keep the layer only if it reduces:

- late operator clarifications,
- requirement reversals,
- validation escapes caused by missing intent,
- and operator frustration with UX outcomes.

If it does not, simplify it further.

## Final Recommendation

The right move is to add a lightweight discovery-and-review control plane, not a new bureaucracy.

The most valuable version for THE_FACTORY is:

- a stable Project Definition Record,
- an event-driven Evidence Review Packet,
- a stronger dispatch-readiness gate,
- structured questioning before build work,
- and explicit assumption tracking across the lifecycle.

That takes the strongest ideas from both research documents while fitting THE_FACTORY's current artifact-first architecture and avoiding the exact failure mode the research warns about: adding complexity faster than it adds clarity.
