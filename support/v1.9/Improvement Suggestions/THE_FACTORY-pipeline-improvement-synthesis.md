# THE_FACTORY Pipeline Improvement Synthesis

Date: 2026-03-20
Status: Draft

## Objective

Translate the strongest ideas from:

- `support/v1.9/Improvement Research/REVIEW PROTOCOL research - claude.docx`
- `support/v1.9/Improvement Research/REVIEW-PROTOCOL research - gpt.md`
- root documentation in `THE_FACTORY`

into a concrete recommendation set for improving THE_FACTORY's agentic pipeline.

## Executive Summary

THE_FACTORY should take six things from the review research:

1. Keep one lean default operating model. Do not add more standing roles unless evals prove they help.
2. Make protocol improvement evidence-driven, not prompt-edit-driven.
3. Add first-class observability for runs, incidents, costs, and false passes.
4. Separate task validation, experiential review, and pipeline review.
5. Route failures by root cause instead of patching everything in the Enforcer or prompt layer.
6. Use specialist passes only when a trigger fires: ambiguity, integration risk, experiential QA need, or real parallelizable breadth.

The biggest immediate issue is not missing theory. It is architectural drift between the root protocol docs and the current meta-infrastructure. `OPERATOR_PROTOCOL.md` still presents a v1.8 role-heavy system, while root `CLAUDE.md` and `.agent/` already reflect a leaner v1.9.1 model built around one default operator agent, skills, structured state, and evals. That split makes the pipeline harder to review, harder to bootstrap correctly, and harder to improve safely.

## What The Research Strongly Supports

### 1. Lean defaults beat role proliferation

Both research documents converge on the same rule: start with the simplest workflow that works, then add structure only when a failure pattern justifies it. The research does support artifacts, gates, critique loops, and verification. It does not support large standing rosters as a default execution model.

What THE_FACTORY should take:

- Preserve a lean default path.
- Treat specialist behavior as triggered modes, skills, or temporary passes.
- Require evidence before promoting a new standing role, phase, or reviewer layer.

### 2. Evaluation should drive protocol change

The strongest repeated theme is that protocol change should follow repeated evidence, not a recent frustrating session. The research recommends representative evals, structured scoring, and regression checks before workflow changes propagate.

What THE_FACTORY should take:

- Keep the improvements log.
- Stop treating the improvements log as sufficient evidence by itself.
- Require metrics, incident evidence, or eval deltas before making durable workflow changes.

### 3. Observability is mandatory

Both documents argue that agent systems need run-level telemetry, not just artifact files and anecdotal notes. The research repeatedly points to run IDs, task classes, token and cost attribution, wall-clock time, retry loops, and quality signals as the minimum substrate for responsible iteration.

What THE_FACTORY should take:

- Add structured run logging.
- Add incident logging.
- Track cost, retries, false passes, and rework.
- Record prompt and flow version lineage in each run.

### 4. Review functions should be separated

The research consistently separates:

- contract/task validation,
- user-experience or experiential review,
- and review of the pipeline itself.

What THE_FACTORY should take:

- Keep validation independent from implementation.
- Keep experiential QA distinct from static validation.
- Treat protocol review as a separate evidence-analysis activity, not just another reviewer persona during delivery.

### 5. Root-cause routing matters

The Claude research is especially strong here: failures should be classified before fixes are proposed. Otherwise the system patches symptoms in the wrong layer.

What THE_FACTORY should take:

- Classify failures before editing prompts or templates.
- Route fixes to the layer that failed:
  - specification/system design,
  - handoff/inter-agent alignment,
  - verification/termination.

### 6. Progressive disclosure is the right context strategy

The research backs the direction already captured in `CLAUDE.md`: advertise capabilities cheaply, load full context only on trigger, and avoid broad context preload. This aligns directly with the current v1.9.1 skills model.

What THE_FACTORY should take:

- Keep skills-as-lazy-context.
- Make that strategy canonical across all root docs.
- Avoid any workflow wording that implies broad, repeated preamble loading as the normal path.

## Current-State Reading Of THE_FACTORY

### 1. The good news

Important parts of the research are already present somewhere in the workspace:

- `OPERATOR_PROTOCOL.md` already says new roles/phases should be added only after repeated failure or eval improvement.
- `OPERATOR_PROTOCOL.md` already includes a lightweight protocol eval idea.
- `CLAUDE.md` already moves toward the research-backed direction:
  - one default operator agent,
  - skills over standing roles,
  - structured state in `.agent/tasks.jsonl`,
  - eval-first anti-drift,
  - progressive disclosure.
- `.agent/metrics/README.md` already starts a metrics layer.
- `.agent/evals/` already exists.

This means THE_FACTORY does not need a fresh philosophical reset. It needs consolidation and hardening.

### 2. The main gap: the docs describe two different systems

The root layer currently mixes two operating models:

- `OPERATOR_PROTOCOL.md` version `1.8` describes a role-based multi-agent workflow with project preambles, session summaries, startup prompts, and a Protocol Enforcer sync model.
- `CLAUDE.md` version `v1.9.1` describes a much leaner model with one default operator agent, flow skills, structured task state, eval-first governance, and progressive disclosure.

This is the single most important pipeline issue surfaced by reading the workspace. If the source of truth is split, then:

- bootstrap can install the wrong infrastructure,
- protocol reviews can optimize the wrong system,
- and research findings cannot be applied consistently.

### 3. There is also an operational source-of-truth mismatch

The root docs repeatedly refer to `PROTOCOL_IMPROVEMENTS.md` at workspace root, but the current workspace state shows:

- `.agent/PROTOCOL_IMPROVEMENTS.md` exists and is populated,
- `PROTOCOL_IMPROVEMENTS.md` at root is tracked but currently absent from the working tree.

That mismatch weakens the review loop because operators and agents are not being pointed at one reliable backlog location.

## What THE_FACTORY Should Take And Apply

### Priority 0: Canonicalize the operating model

This should happen before adding new review mechanics.

Recommendation:

- Decide whether v1.9.1 is the canonical direction.
- If yes, rewrite the root docs so they describe the actual skills-and-evals architecture instead of the older role-heavy one.
- Archive or explicitly label the v1.8 role-based protocol as legacy reference material rather than presenting both as live truth.

Why this is the first move:

- Every later improvement depends on a clear source of truth.
- The research strongly favors the leaner architecture already visible in `CLAUDE.md`.

Concrete implications:

- `README.md` should describe the current canonical workflow, not a legacy one.
- `INIT.md` should route new users into the actual pipeline.
- `OPERATOR_PROTOCOL.md` should either be upgraded to the v1.9.1 operating model or split into `legacy` and `current`.
- `IMPLEMENTATION_PROMPT.md` should scaffold the actual system being recommended.
- `PROTOCOL_REVIEW_PROMPT.md` should review the actual system in production.

### Priority 1: Upgrade protocol improvement from backlog review to evidence review

Keep the capture-and-batch model. Expand the inputs.

Recommendation:

- Preserve the improvements log as a qualitative backlog.
- Add structured evidence alongside it:
  - run ledger,
  - incident log,
  - eval manifest,
  - reviewer or operator scorecards.

Minimum artifacts to add:

- `.agent/runs.jsonl`
- `.agent/incidents.jsonl`
- `.agent/evals/manifest.md` or equivalent structured manifest
- `.agent/reviews/scorecards.jsonl` or equivalent

Minimum run record fields:

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

Important synthesis point:

The current `.agent/tasks.jsonl` is useful, but it is task state, not full observability. The research argues for preserving execution telemetry, not just current status.

### Priority 1: Add root-cause classification to protocol review

The next protocol review prompt should require classification before proposal.

Recommendation:

Add a mandatory classification step to `PROTOCOL_REVIEW_PROMPT.md`:

- `SPECIFICATION_OR_SYSTEM_DESIGN`
- `HANDOFF_OR_ALIGNMENT`
- `VERIFICATION_OR_TERMINATION`

Then require each proposal to answer:

- What failed?
- What evidence shows it?
- Why did the current gate miss it?
- What is the smallest fix in the correct layer?
- What eval or metric should improve if this change works?

This is the highest-leverage idea from the Claude research because it prevents downstream patching of upstream failures.

### Priority 1: Make cadence signal-driven instead of feature-count-driven

The current protocol says to run review periodically every `5-10 features`. That is better than nothing, but the research recommends a more operational cadence.

Recommendation:

- Per task: emit structured run data.
- Weekly: short ops review using rates and incidents.
- Monthly: protocol review for durable workflow changes.
- Quarterly: structural review for bigger architecture changes such as role additions, flow merges, or workflow removals.

Use triggers as well as cadence:

- repeated false passes,
- rising rework rate,
- rising operator override rate,
- repeated ambiguity in one task class,
- or cost-per-successful-task spikes.

### Priority 1: Separate three review layers clearly

THE_FACTORY should explicitly distinguish:

1. `Task validation`
2. `Experiential review`
3. `Pipeline review`

Suggested local interpretation:

- Task validation:
  - Did the output satisfy the explicit contract?
  - Use validator logic, tests, schema checks, and scope checks.
- Experiential review:
  - Does the behavior actually feel right in use?
  - Use QA, user testing, or operator review.
- Pipeline review:
  - Is the system producing quality efficiently?
  - Use runs, incidents, costs, retries, and sampled traces.

This separation already partially exists in the root docs through Validator vs QA. The missing piece is a formal pipeline-review layer with metrics and root-cause routing.

### Priority 2: Formalize specialist triggers, but do not create new standing roles by default

The research does support specialist intervention. It does not support always-on reviewer stacks.

Recommendation:

Use explicit trigger rules:

- Pre-implementation clarification pass:
  - only when the brief is ambiguous, conflicting, or UX-heavy.
- Planning or architecture pass:
  - only when interface risk or decomposition quality is decisive.
- Post-implementation experiential pass:
  - only when live behavior, workflow, trust, or polish matter beyond static correctness.
- Parallel agent work:
  - only when work divides cleanly into independent subproblems.

Practical synthesis for THE_FACTORY:

- Keep the v1.9.1 instinct of skill-triggered specialization.
- Do not reintroduce a permanent Reviewer or User Advocate role unless evals show a meaningful gain.
- If a "reviewer" exists, make it a review mode or scoring function, not a permanent delivery-stage persona.

### Priority 2: Harden validator and refinement-loop behavior

The research strongly warns against unbounded retry loops and verifier drift.

Recommendation:

- Make validators check against the task contract or spec, not an unconstrained personal judgment.
- Add hard iteration caps:
  - doer/verifier loop: cap at 3,
  - reviewer refinement loop: cap at 2.
- When a cap is hit, log an incident and escalate instead of silently retrying.

Metrics to add:

- `validator_false_pass_rate`
- `validator_false_fail_rate`
- `revision_loop_rate`
- `tokens_per_rework`
- `cost_per_successful_task`

### Priority 2: Expand the metrics layer beyond token profiling

The existing `.agent/metrics/README.md` is a good start, but it is still mostly infrastructure-efficiency-oriented.

Recommendation:

Track four metric families:

### Outcome metrics

- `first_pass_success_rate`
- `escaped_defect_rate`
- `rework_rate`
- `qa_disagreement_rate`
- `operator_override_rate`

### Efficiency metrics

- `cycle_time_per_task`
- `handoff_count_per_task`
- `blocked_rate`
- `operator_minutes_per_task`

### Cost metrics

- `input_tokens`
- `output_tokens`
- `tool_calls`
- `estimated_cost`
- `cost_per_successful_task`

### Qualitative metrics

- `clarity`
- `confidence`
- `auditability`
- `friction`
- `surprise`
- `taste_alignment` for UX-heavy work

### Priority 3: Add variant testing for prompt, skill, and flow changes

This is not the first improvement to make, but it is the right long-term habit.

Recommendation:

- Version prompts, skills, and major flow changes explicitly.
- Record that version lineage in the run ledger.
- Before promoting material protocol changes, run a small representative eval set against old vs new variants.

This turns prompt editing into controlled change management instead of intuition-driven tweaking.

## What Not To Take

The research is also useful for what it argues against.

THE_FACTORY should not take these paths:

- Do not add more standing roles just because more roles feel safer.
- Do not create a full reviewer stack for routine tasks.
- Do not rely on a backlog file alone as the protocol-improvement system.
- Do not patch symptoms at the Enforcer stage before locating the real failure layer.
- Do not allow unbounded refinement or retry loops.
- Do not use mesh-like agent communication topologies for normal delivery work.
- Do not fork the source of truth between legacy docs and current implementation.

## Recommended File-Level Changes

### `README.md`

Update to explain the current canonical architecture in one paragraph:

- one default operating model,
- skills loaded on trigger,
- eval-first improvement,
- structured state and observability.

Remove ambiguity about whether the system is role-heavy or skill-heavy.

### `INIT.md`

Update onboarding so new agents are routed into the actual current operating model. If the current model is skills-first, `INIT.md` should not teach a legacy role roster as the default mental model.

### `OPERATOR_PROTOCOL.md`

This is the highest-effort file and the most important one.

It should absorb:

- canonical architecture choice,
- review-layer separation,
- signal-driven cadence,
- run/incident/eval artifacts,
- root-cause classification,
- capped iteration loops,
- cost and false-pass metrics,
- and explicit propagation rules after eval checks.

### `PROTOCOL_REVIEW_PROMPT.md`

Add:

- evidence inputs beyond the backlog,
- failure classification step,
- required metric review,
- expected eval impact for each proposal,
- and a "do not propagate before regression check" rule.

### `IMPLEMENTATION_PROMPT.md`

If v1.9.1 is canonical, this file should scaffold:

- `.agent/tasks.jsonl`
- `.agent/runs.jsonl`
- `.agent/incidents.jsonl`
- `.agent/evals/`
- `.agent/metrics/`
- skills and trigger-table structures
- any required validation or logging hooks

It should not primarily scaffold the older preamble-heavy model if that is no longer the intended architecture.

### `PROTOCOL_IMPROVEMENTS.md`

Re-establish one clear path.

Recommendation:

- either restore it at root and make `.agent/PROTOCOL_IMPROVEMENTS.md` the mirrored implementation copy,
- or officially move the source of truth into `.agent/` and update every root reference accordingly.

Right now the protocol references a backlog location that is not reliably present.

## Suggested Adoption Order

1. Canonicalize the architecture and source-of-truth files.
2. Restore a single improvements backlog path.
3. Add runs and incidents logging.
4. Update protocol review to classify failures and require evidence.
5. Expand metrics from context efficiency to quality, cost, and false-pass tracking.
6. Add iteration caps and escalation rules.
7. Add variant testing for flow and prompt changes.

## Bottom Line

The right move for THE_FACTORY is not to become more agent-heavy. It is to become more measurable, more explicit about failure routing, and more consistent about what its canonical pipeline actually is.

The research supports the direction already visible in `CLAUDE.md` and `.agent/`: lean execution, progressive disclosure, eval-first governance, and structured state. The improvements THE_FACTORY should take now are the missing operational pieces around observability, review taxonomy, cadence, and source-of-truth consistency.
