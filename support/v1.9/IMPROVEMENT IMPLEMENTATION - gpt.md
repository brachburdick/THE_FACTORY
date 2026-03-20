# THE_FACTORY Improvement Implementation Plan

Date: 2026-03-20
Prepared by: GPT
Status: Recommended rollout plan

## Inputs Synthesized

- `support/v1.9/Improvement Suggestions/META-LAYER IMPLEMENTATION - claude.md`
- `support/v1.9/Improvement Suggestions/META_LAYER_PIPELINE_RECOMMENDATIONS.md`
- `support/v1.9/Improvement Suggestions/RESPECTIVE AGENT STRENGTHS suggestions-claude.md`
- `support/v1.9/Improvement Suggestions/RESPECTIVE AGENT STRENGTHS suggestions-gpt.md`
- `support/v1.9/Improvement Suggestions/REVIEW PROTOCOL IMPLEMENTATION - claude.md`
- `support/v1.9/Improvement Suggestions/THE_FACTORY-pipeline-improvement-synthesis.md`

Cross-checked against the live root workspace:

- `README.md`
- `INIT.md`
- `CLAUDE.md`
- `OPERATOR_PROTOCOL.md`
- `IMPLEMENTATION_PROMPT.md`
- `PROTOCOL_REVIEW_PROMPT.md`
- `templates/`
- `.agent/`
- `.claude/skills/`

## Executive Decision

THE_FACTORY should not become more role-heavy, more review-heavy, or more model-routed.

It should consolidate around the lean v1.9.1 architecture already visible in `CLAUDE.md`, `.agent/`, and `.claude/skills/`, then add the missing layers that the improvement documents consistently point to:

1. stronger intent capture before execution,
2. stronger observability during execution,
3. stronger evidence-driven review after execution.

The right implementation shape is:

- one canonical operating model,
- lightweight new artifacts,
- stronger gates,
- structured telemetry,
- trigger-based specialist behavior,
- and eval-gated propagation.

## Decisions To Lock Immediately

These should be treated as rollout assumptions, not open design questions.

### 1. Canonical architecture

Adopt the v1.9.1 skill-and-flow model as the canonical system of record.

- `CLAUDE.md` remains the hot runtime constitution.
- `.claude/skills/` remains the flow layer.
- `.agent/` remains the structured state, schema, eval, and metrics layer.
- `OPERATOR_PROTOCOL.md` must be rewritten to describe that same system, not the legacy v1.8 role-heavy workflow.

### 2. Backlog source of truth

Restore `PROTOCOL_IMPROVEMENTS.md` at root as the operator-facing canonical backlog.

Reason:

- root docs and onboarding already point there,
- it is discoverable to humans,
- and the current mismatch is already causing drift.

If you still want a machine-facing copy in `.agent/`, treat it as a mirror, not a competing source of truth.

### 3. New artifacts

Adopt exactly two new control-plane artifacts first:

- `PROJECT_DEFINITION_RECORD.md`
- `EVIDENCE_REVIEW_PACKET.md`

Do not add more meta artifacts until these prove their value.

### 4. Review model

Keep three distinct review layers:

1. Task validation
2. Experiential review
3. Pipeline review

Do not collapse them into one generic reviewer pass.

### 5. Specialization model

Keep specialization trigger-based.

- Skills, modes, and temporary passes are allowed.
- New standing roles are deferred unless evals prove a meaningful gain.

### 6. Model routing

Defer multi-model routing and any detailed routing matrix.

The documents are aligned that scaffold quality is the bigger lever right now.

## Current-State Problems This Plan Solves

1. The root docs currently describe two different systems.
   - `README.md`, `INIT.md`, `OPERATOR_PROTOCOL.md`, and `IMPLEMENTATION_PROMPT.md` still teach a role-heavy workflow.
   - `CLAUDE.md`, `.agent/`, and `.claude/skills/` already implement a leaner v1.9.1 model.

2. The protocol improvements backlog has a source-of-truth mismatch.
   - Root docs point to `PROTOCOL_IMPROVEMENTS.md`.
   - The populated file currently lives at `.agent/PROTOCOL_IMPROVEMENTS.md`.
   - `git status` also shows the root file deleted in the working tree.

3. Intent capture is not yet durable enough.
   - There is no single project-level artifact for frozen intent, quality priorities, UX intent, assumptions, and unknowns.

4. Dispatch is still more artifact-complete than intent-complete.
   - The system can be formally ready while still being unsafe to build.

5. Handoffs are missing some key execution controls.
   - explicit replan triggers,
   - explicit verification procedure,
   - explicit evidence expectations,
   - explicit assumptions in force.

6. Observability is not yet strong enough to support disciplined protocol improvement.
   - `.agent/tasks.jsonl` tracks task state,
   - but there is no structured run ledger, incident log, or review scorecard layer.

7. Metrics currently lean toward infrastructure efficiency.
   - outcome quality,
   - false passes,
   - rework,
   - operator overrides,
   - and cost-per-successful-task
   are not yet first-class.

## Target End State

When this rollout is complete, THE_FACTORY should have:

- one unambiguous root operating model,
- one clear protocol backlog path,
- one durable project-definition artifact above feature specs,
- one event-driven learning artifact between execution waves,
- one stronger safe-to-build dispatch gate,
- one structured telemetry layer for runs, incidents, reviews, and eval lineage,
- and one protocol review loop that classifies failures before proposing fixes.

## Rollout Plan

## Phase 0: Canonicalize The System Of Record

### Goal

Eliminate architectural drift before adding new machinery.

### Actions

1. Publish one explicit root-level decision that v1.9.1 is canonical.
2. Rewrite `README.md` so it describes:
   - one default operator agent,
   - flow skills + domain skills,
   - structured state in `.agent/`,
   - eval-first improvement.
3. Rewrite `INIT.md` so it routes users into the current model rather than a legacy role roster.
4. Rewrite `OPERATOR_PROTOCOL.md` into the current architecture.
   - `CLAUDE.md` should own hot runtime rules.
   - `OPERATOR_PROTOCOL.md` should own governance, artifact schemas, review cadence, logging, and rollout policy.
5. Rewrite `IMPLEMENTATION_PROMPT.md` so it scaffolds the current system rather than preambles/startup-prompts as the default center of gravity.
6. Rewrite `PROTOCOL_REVIEW_PROMPT.md` so it reviews the actual current system.
7. Restore root `PROTOCOL_IMPROVEMENTS.md` and reconcile or retire `.agent/PROTOCOL_IMPROVEMENTS.md`.
8. Normalize template metadata rules.
   - `templates/spec.md` currently still uses blockquote metadata despite the protocol's frontmatter rule.
9. Mark legacy v1.8 material as archived reference in `support/v1.8/` rather than leaving it mixed into live root docs.

### Files In Scope

- `README.md`
- `INIT.md`
- `OPERATOR_PROTOCOL.md`
- `IMPLEMENTATION_PROMPT.md`
- `PROTOCOL_REVIEW_PROMPT.md`
- `PROTOCOL_IMPROVEMENTS.md`
- `.agent/PROTOCOL_IMPROVEMENTS.md`
- `templates/spec.md`

### Exit Criteria

- A fresh agent reading only the root docs learns one system, not two.
- Every root reference to the improvements backlog points to a file that actually exists.
- Root templates and protocol rules agree on metadata format.

## Phase 1: Add The Lightweight Intent Layer

### Goal

Prevent assumption drift without turning the pipeline into spec bureaucracy.

### Actions

1. Add `templates/project-definition-record.md`.
2. Define the Project Definition Record with two sections:
   - `Frozen Core`
   - `Mutable Clarifications`
3. Minimum frozen fields:
   - problem statement,
   - target users / stakeholders,
   - key scenarios / jobs-to-be-done,
   - desired outcomes,
   - success metrics,
   - non-goals,
   - hard constraints,
   - quality priorities,
   - UX intent,
   - decision rights,
   - Always / Ask First / Never boundaries.
4. Minimum mutable fields:
   - discovered requirements,
   - clarifications,
   - approved refinements,
   - architectural decisions,
   - known assumptions with confidence,
   - known unknowns with discovery path,
   - open questions awaiting operator input.
5. Add `templates/evidence-review-packet.md`.
6. Define the Evidence Review Packet to capture:
   - what changed since last review,
   - evidence observed,
   - assumptions invalidated,
   - assumptions strengthened,
   - new questions surfaced,
   - proposed requirement / UX / architecture changes,
   - items intentionally deferred,
   - next-slice recommendation,
   - dispatch status: `READY | READY WITH EXPLICIT ASSUMPTIONS | NOT READY`.
7. Update `templates/spec.md` so feature specs reference upstream project-definition items and evidence packets.
8. Add a light traceability rule:
   - if a spec, plan, or task changes because of new evidence, it must cite the upstream Project Definition Record item or Evidence Review Packet that caused the change.
9. Update `templates/orchestrator-state.md` to include:
   - latest evidence packet reference,
   - recent session digest,
   - active assumptions in force when relevant.

### Important Constraint

Do not create a separate standing "meta manager" or "requirements governor" role for this.

Start by integrating the question set into `INIT.md` and `feature-flow`.
Only create a dedicated `discovery-governance` skill later if repeated evidence shows it is necessary.

### Files In Scope

- `templates/project-definition-record.md`
- `templates/evidence-review-packet.md`
- `templates/spec.md`
- `templates/plan.md`
- `templates/orchestrator-state.md`
- `README.md`
- `INIT.md`
- `.claude/skills/feature-flow/SKILL.md`

### Exit Criteria

- Every new project or major feature can point to one durable intent artifact.
- Execution waves can point to one explicit learning artifact.
- Requirement changes become traceable instead of conversational.

## Phase 2: Upgrade Dispatch From "Complete" To "Safe To Build"

### Goal

Prevent downstream drift by making dispatch gates intent-aware, not just artifact-aware.

### Actions

1. Expand the dispatch readiness gate so execution cannot start unless the next slice has:
   - explicit user,
   - explicit problem,
   - explicit desired outcome,
   - explicit non-goals,
   - explicit hard constraints,
   - explicit success signal,
   - explicit accepted assumptions if uncertainty remains.
2. Add a structured questioning protocol before implementation.
3. Minimum question categories:
   - product reality,
   - UX intent,
   - decision boundaries,
   - quality priorities,
   - data and integration,
   - evidence plan,
   - success criteria.
4. Upgrade `templates/handoff-packet.md` with these sections:
   - `Replan Triggers`
   - `Verification Procedure`
   - `Evidence Required`
   - `Assumptions In Force`
   - `Dispatch Status`
5. Add examples of good replan triggers:
   - a required file or interface is missing,
   - acceptance criteria conflict with implementation reality,
   - unrelated failures block proof of correctness,
   - more than one out-of-scope area must change,
   - a hidden dependency invalidates the plan.
6. Extend Validator behavior so verdicts are anchored to the stated verification procedure, not generic judgment alone.
7. Add hard loop caps:
   - doer/verifier retry loop: max 3,
   - review/refinement loop: max 2.
8. When a cap is hit:
   - log an incident,
   - escalate,
   - do not silently keep retrying.

### Files In Scope

- `templates/handoff-packet.md`
- `templates/validator-verdict.md`
- `INIT.md`
- `OPERATOR_PROTOCOL.md`
- `PROTOCOL_REVIEW_PROMPT.md`
- `.claude/skills/feature-flow/SKILL.md`
- `.agent/schemas/handoff-envelope.json`
- `scripts/validate-handoff.sh`

### Exit Criteria

- No build task can start without a safe-to-build slice.
- Every handoff tells the receiver when to stop, what proof to produce, and what uncertainty is being accepted.
- Retry behavior is bounded and observable.

## Phase 3: Add Observability And Separate The Review Layers

### Goal

Make protocol change evidence-driven instead of anecdote-driven.

### Actions

1. Add `.agent/runs.jsonl`.
2. Add `.agent/incidents.jsonl`.
3. Add `.agent/reviews/scorecards.jsonl`.
4. Add `.agent/evals/manifest.md` for prompt/skill/flow version lineage.
5. Define minimum run fields:
   - `run_id`
   - `date`
   - `project_id`
   - `task_id`
   - `task_type`
   - `workflow_path`
   - `agents_or_skills_invoked`
   - `prompt_or_skill_versions`
   - `result`
   - `rework_required`
   - `validator_result`
   - `qa_result`
   - `attempt_count`
   - `input_tokens`
   - `output_tokens`
   - `tool_calls`
   - `latency_ms`
   - `estimated_cost`
6. Define minimum incident fields:
   - `incident_id`
   - `date`
   - `project`
   - `task_id`
   - `severity`
   - `failure_type`
   - `detected_by`
   - `escaped_stage`
   - `root_cause_guess`
   - `protocol_change_candidate`
7. Add an experiential scorecard model for QA or operator review:
   - clarity,
   - confidence,
   - friction,
   - surprise,
   - taste alignment where relevant.
8. Expand `.agent/metrics/README.md` beyond token profiling to four families:
   - outcome,
   - efficiency,
   - cost,
   - qualitative.
9. Track at least these outcome-quality metrics:
   - first-pass success rate,
   - escaped defect rate,
   - rework rate,
   - validator false pass rate,
   - validator false fail rate,
   - qa disagreement rate,
   - operator override rate.
10. Track at least these efficiency and cost metrics:
   - cycle time per task,
   - handoff count per task,
   - blocked rate,
   - operator minutes per task,
   - cost per successful task.
11. Formalize review cadence:
   - per task: append run data,
   - event-driven: issue Evidence Review Packets,
   - weekly: ops review,
   - monthly: protocol review,
   - quarterly: structural review.

### Files In Scope

- `.agent/runs.jsonl`
- `.agent/incidents.jsonl`
- `.agent/reviews/scorecards.jsonl`
- `.agent/evals/manifest.md`
- `.agent/metrics/README.md`
- `PROTOCOL_REVIEW_PROMPT.md`
- `skills/protocol-review/SKILL.md`

### Exit Criteria

- You can answer quality, rework, false-pass, and cost questions without manual archaeology.
- Task validation, experiential review, and pipeline review are operationally distinct.
- Protocol reviews are backed by structured evidence, not just backlog entries.

## Phase 4: Harden Runtime Execution Behavior

### Goal

Improve execution quality without reintroducing standing roles.

### Actions

1. Add checkpoint-based replanning to the structured state layer.
2. Extend task tracking with checkpoint fields such as:
   - `plan_checkpoint`
   - `last_checkpoint_at`
   - `replan_triggers`
   - `verification_context`
3. Update flow skills so phase transitions write or update checkpoints.
4. Require a separate-context verification step for code-changing work.
   - The same context that wrote the change should not be the only context that certifies it.
5. Keep self-assessment as a signal, not a gate.
6. Standardize explicit negative constraints in all flow skills.
   - `debug-flow`, `feature-flow`, and `refactor-flow` already have anti-pattern sections.
   - Preserve that pattern and make it part of the rollout standard.
7. Ensure handoff schema and validation support the new handoff fields from Phase 2.
8. Keep specialist passes trigger-based:
   - ambiguity,
   - integration risk,
   - experiential QA need,
   - or genuinely parallelizable breadth.

### Files In Scope

- `.claude/skills/debug-flow/SKILL.md`
- `.claude/skills/feature-flow/SKILL.md`
- `.claude/skills/refactor-flow/SKILL.md`
- `.agent/tasks.jsonl`
- `.agent/schemas/`
- `scripts/tasks.sh`
- `.agent/schemas/handoff-envelope.json`
- `scripts/validate-handoff.sh`

### Exit Criteria

- Plans survive across sessions better.
- The pipeline has explicit replan points instead of drift-by-continuation.
- Verification is independent enough to reduce self-certification risk.

## Phase 5: Make Protocol Change Eval-Gated

### Goal

Only keep new process weight that earns its cost.

### Actions

1. Version prompts, skills, major flow changes, and major template changes.
2. Record that version lineage in the run ledger.
3. Update `PROTOCOL_REVIEW_PROMPT.md` to require failure classification before proposals:
   - `SPECIFICATION_OR_SYSTEM_DESIGN`
   - `HANDOFF_OR_ALIGNMENT`
   - `VERIFICATION_OR_TERMINATION`
4. Require each protocol change proposal to answer:
   - What failed?
   - What evidence shows it?
   - Why did the current gate miss it?
   - What is the smallest fix in the correct layer?
   - What eval or metric should improve if this works?
5. Add an explicit rule to review protocol changes in this order:
   - scaffold fix first,
   - hook or validation fix second,
   - prompt wording fix third,
   - model-routing fix last.
6. Before promoting a material workflow change, run a small representative old-vs-new eval bundle.
7. Remove or simplify any new artifact or rule that does not improve the agreed metrics.

### Files In Scope

- `PROTOCOL_REVIEW_PROMPT.md`
- `.agent/evals/`
- `.agent/evals/manifest.md`
- `.agent/metrics/README.md`
- `.agent/VERSION.md`

### Exit Criteria

- Protocol changes are traceable to evidence.
- You can compare old and new workflow variants deliberately.
- The pipeline keeps only changes that reduce waste, escapes, or operator friction.

## Pilot Strategy

Do not roll this out everywhere at once.

Use one pilot project or one major new feature slice first.

### Pilot the minimum viable set

1. Canonical source-of-truth cleanup
2. `PROJECT_DEFINITION_RECORD.md`
3. `EVIDENCE_REVIEW_PACKET.md`
4. Stronger dispatch readiness gate
5. Handoff replan triggers + verification procedure
6. `runs.jsonl` + `incidents.jsonl`

### Pilot success measures

Track these before and after:

- late `[ASK OPERATOR]` incidents,
- mid-build requirement reversals,
- validation or QA failures caused by missing intent,
- validator false passes,
- operator override rate,
- rework rate,
- cost per successful task,
- operator-reported friction or UX dissatisfaction.

If those do not improve, simplify before expanding.

## Explicit Deferrals

These ideas showed up in the documents, but should stay out of the first rollout.

1. Detailed multi-model routing matrix
2. New standing roles
3. Heavy spec-as-source development
4. Mesh-like agent communication topologies
5. LLM-as-judge as a primary quality gate
6. Re-planning ceremonies after every task
7. Broad new documentation that does not change routing, scope, or verification

## Recommended Implementation Order

1. Phase 0: canonicalize the root source of truth and fix the backlog path
2. Phase 1: add the Project Definition Record and Evidence Review Packet
3. Phase 2: strengthen dispatch readiness, handoffs, and verification contracts
4. Phase 3: add run, incident, scorecard, and metrics infrastructure
5. Phase 4: harden flow execution with checkpoints and separate-context verification
6. Phase 5: require eval-backed promotion and prune anything that does not earn its cost

## Bottom Line

The improvement documents converge on one answer:

THE_FACTORY does not need more permanent agents.
It needs a cleaner canonical architecture, stronger intent capture, better telemetry, stronger dispatch and verification contracts, and a review loop that fixes the right layer for the right reason.

The best rollout is therefore:

- unify around v1.9.1,
- add two lightweight control-plane artifacts,
- strengthen handoffs and gates,
- add real observability,
- and make protocol evolution evidence-backed.

That gives you a pipeline that stays lean in daily use but becomes much more measurable, much harder to drift, and much easier to improve safely.
