# Review And Revision Process Research

Date: 2026-03-20
Scope: Research synthesis and workspace-specific recommendations for refining THE_FACTORY's review, revision, evaluation, and observability process for multi-agent project delivery.

## 1. Core Question

How should THE_FACTORY structure its review and revision process so that it improves quality and efficiency without drifting back into unnecessary agent-role complexity?

This includes:

- review cadence,
- improvement logging,
- evaluation design,
- per-task and per-agent cost tracking,
- qualitative pipeline assessment,
- and whether specialist external agents should exist before, during, or after implementation.

## 2. Bottom Line

The best-supported direction is:

1. keep the default delivery loop lean,
2. make protocol improvement primarily eval-driven rather than prompt-edit-driven,
3. use specialist agents only when they solve a specific ambiguity, subjectivity, or parallelization problem,
4. separate correctness review from experiential review,
5. and instrument the pipeline so you can measure quality, rework, and cost at the task level.

In practical terms, that means:

- retain a small core execution loop such as `operator -> implementer -> validator -> QA/user review when needed`,
- keep the improvements log,
- keep the Protocol Enforcer as a propagation/sync function,
- but stop treating additional reviewers or pre-implementer specialists as default standing roles unless evals show a real gain.

The current organic design is directionally strong. The main upgrade needed is not "more roles." It is a stronger review system based on:

- structured run records,
- explicit incident logging,
- representative eval sets,
- and scheduled ops reviews that feed protocol changes only after evidence.

## 3. What The Research Says

### 3.1 Start with the simplest workflow that works

Recent production guidance is much more conservative about role proliferation than early multi-agent "AI software company" patterns.

- Anthropic's guidance on effective agents recommends starting with the simplest pattern and adding workflow structure only when necessary. [1]
- Anthropic's multi-agent research write-up shows that multi-agent systems can help when a task has real parallel breadth, but they come with substantially higher token and coordination costs. [3]
- The software-engineering paper Agentless is especially relevant: a simpler localization/repair/validation flow outperformed more complex agent systems on SWE-bench Lite while using fewer resources. [8]

Implication for THE_FACTORY:

- Lean default flows are not a compromise. They are the current best-practice baseline.
- Additional roles should be treated as exceptions that need evidence, not as the default posture.

### 3.2 Early multi-agent role systems were useful, but they are not the final answer

Early papers such as ChatDev and MetaGPT are still useful for one key lesson: explicit artifacts, SOPs, and staged communication improve coherence relative to unstructured chat. [9] [10]

But those papers do not prove that many standing roles are optimal for day-to-day project execution. More recent operational guidance suggests:

- explicit artifacts are good,
- critique and revision loops are good,
- verification is essential,
- but unnecessary role multiplication becomes coordination overhead.

Implication for THE_FACTORY:

- Keep artifacts and gates.
- Trim standing personas.
- Promote specialization only when it changes outcomes on a representative task set.

### 3.3 Review systems work best when they are eval-driven

Anthropic's eval guidance and OpenAI's eval guidance both point toward the same operational pattern:

- define representative tasks,
- score outcomes consistently,
- inspect failures,
- and only then change prompts, scaffolds, or workflow. [2] [4] [5]

This matters because prompt-only revision tends to produce:

- local improvements on a recent failure,
- accidental regressions on other task classes,
- and expanding instructions without measured gains.

Implication for THE_FACTORY:

- protocol review should be framed as a regression-management and eval-improvement process,
- not mainly as a document-editing ritual.

### 3.4 Observability is not optional for agent systems

OpenAI's tracing, trace grading, and usage/cost APIs reflect a broader pattern: agent systems need structured telemetry at the run and step level if you want to improve them responsibly. [5] [6] [7]

Useful systems record:

- run identifiers,
- step boundaries,
- task class,
- prompt/version lineage,
- token usage,
- wall-clock time,
- outcome,
- and human quality signals.

Implication for THE_FACTORY:

- the current improvement log is valuable but insufficient by itself,
- because it captures notable failures but not overall rates, cost distribution, or false-pass behavior.

### 3.5 Specialist agents are useful when they address a specific failure mode

The strongest case for extra specialist agents is not "more eyes are always better." It is one of these:

- ambiguity needs structured clarification before implementation,
- subjective UX/taste questions need a design-oriented or user-advocate pass,
- live behavior needs experiential assessment beyond static validation,
- or the task genuinely has independent subproblems that can be parallelized.

Implication for THE_FACTORY:

- a blind-to-code interviewer can be valuable for eliciting intent and constraints,
- but should not be the final authority passed directly to implementers without code-aware reconciliation,
- and a post-build experiential reviewer is often more valuable than a generic extra reviewer before coding starts.

## 4. Recommended Operating Model For THE_FACTORY

## 4.1 Default delivery loop

Use one lean default loop for most work:

`operator -> implementer -> validator -> QA or user-advocate only when needed`

This should be the baseline unless a task clearly triggers a special path.

Why:

- it minimizes handoff overhead,
- keeps ownership clear,
- makes evals easier to interpret,
- and reduces correlated failure introduced by too many agents sharing the same flawed assumptions.

## 4.2 Specialist-agent trigger model

Treat specialist agents as opt-in paths, not standing roles for every task.

Recommended triggers:

- `Spec interviewer` before planning:
  - Use when user intent is ambiguous, goals are under-specified, priorities are conflicting, or UX quality is central.
- `Code-aware architect/planner` before implementation:
  - Use when integration risk is high, interfaces are unclear, or decomposition quality is the main determinant of success.
- `Experiential QA / user-advocate` after implementation:
  - Use when workflow quality, usability, trust, or cross-screen behavior matters more than static correctness alone.
- `Parallel specialist agents`:
  - Use only when the work can be decomposed into independent questions or ownership slices with clear boundaries.

Default answer to "should there be an extra agent here?" should be "not unless a trigger fires."

## 4.3 Review layers

Separate review into three different functions:

### Layer A: Task validation

Goal: Did this task satisfy its contract?

Checks:

- scope compliance,
- acceptance criteria,
- tests,
- obvious regressions,
- artifact completeness,
- declared interface impact.

Owner:

- Validator.

### Layer B: Experiential review

Goal: Does the delivered behavior feel right to a user or operator?

Checks:

- UX clarity,
- friction,
- workflow coherence,
- perceived polish,
- confidence/trust,
- appropriateness of defaults.

Owner:

- QA tester, user-advocate mode, or operator review.

### Layer C: Pipeline review

Goal: Is the system itself producing quality efficiently?

Checks:

- false passes,
- avoidable rework,
- role overhead,
- ambiguous handoffs,
- cost hotspots,
- prompt bloat,
- operator burden.

Owner:

- periodic protocol review using logs, metrics, sampled transcripts, and eval outcomes.

These three layers should not be collapsed into one generic "reviewer."

## 4.4 Protocol improvement loop

Keep the existing capture-and-batch idea, but make it more explicitly evidence-based.

Recommended flow:

1. During work, log:
   - incidents,
   - friction,
   - surprising successes,
   - and operator burden.
2. Weekly, run a short ops review:
   - look at rates, not just anecdotes.
3. Monthly, run a protocol review:
   - only promote changes backed by repeated failure, meaningful friction, or eval gains.
4. Before making a durable protocol change:
   - test it on a representative eval set.
5. After approval:
   - update root protocol and templates,
   - then run the Enforcer/propagation step on project infrastructure.

This makes the Enforcer the deployment mechanism for protocol changes, not the source of truth for whether a change is justified.

## 5. Recommended Cadence

### 5.1 Per task

Every task should produce a structured run record.

Minimum fields:

- `run_id`
- `project`
- `feature`
- `task_id`
- `task_class`
- `workflow_path`
- `agents_invoked`
- `prompt_versions`
- `artifact_versions`
- `start_time`
- `end_time`
- `result`
- `rework_required`
- `validator_result`
- `qa_result`
- `operator_score`
- `input_tokens`
- `output_tokens`
- `tool_calls`
- `estimated_cost`

### 5.2 Weekly ops review

Recommended duration: 30 to 45 minutes.

Goal:

- detect quality/cost trends before they harden into protocol debt.

Review:

- first-pass pass rate,
- rework rate,
- most common block reasons,
- false-pass and false-fail examples,
- highest-cost task classes,
- highest-friction task classes,
- and top recurring ambiguity sources.

Outputs:

- quick mitigations,
- deferred investigations,
- candidates for protocol review.

### 5.3 Monthly protocol review

Recommended cadence:

- once per month,
- or earlier if a P0 failure occurs repeatedly or a major workflow shift happens.

Use this for:

- protocol text changes,
- template changes,
- role-policy changes,
- eval-set updates,
- and propagation plans.

### 5.4 Quarterly structural review

Recommended cadence:

- once per quarter.

Use this for larger questions:

- whether a standing role should be removed,
- whether a specialist path should be promoted,
- whether a new eval track is needed,
- whether the system has accumulated unnecessary handoffs or duplicated documents.

This is where role changes belong, not in the heat of single failures.

## 6. Measurement Framework

## 6.1 Outcome metrics

Track at minimum:

- `first_pass_success_rate`
- `escaped_defect_rate`
- `rework_rate`
- `validator_false_pass_rate`
- `validator_false_fail_rate`
- `qa_disagreement_rate`
- `operator_override_rate`

Interpretation:

- If first-pass success is low, planning/spec quality may be weak.
- If false passes are high, validation is too shallow or over-trusting.
- If overrides are high, the system is not aligned with operator expectations.

## 6.2 Efficiency metrics

Track:

- `cycle_time_per_task`
- `wall_clock_time_per_workflow`
- `handoff_count_per_task`
- `average_review_time`
- `operator_minutes_per_task`
- `retry_count`
- `blocked_rate`

Interpretation:

- If handoff count rises faster than quality, you are over-specializing.
- If operator minutes stay high despite more agents, the process is not really offloading cognition.

## 6.3 Cost and token metrics

Track by task, agent, and workflow path:

- `input_tokens`
- `output_tokens`
- `reasoning_tokens` when available
- `tool_calls`
- `dollars_per_task`
- `dollars_per_successful_task`
- `tokens_per_rework`

This is where newer API observability patterns are helpful. OpenAI's usage/cost APIs and trace structures are good reference models for the shape of data worth preserving, even if your implementation differs. [5] [6] [7]

## 6.4 Qualitative metrics

You specifically asked about pipeline qualia. That is worth tracking, but it should be formalized so it can be compared over time.

Recommended scorecard after sampled tasks:

- `clarity`: Was the task framing clear?
- `confidence`: How much did the operator trust the result before reading deeply?
- `surprise`: How unexpectedly did the agent behave?
- `auditability`: How easy was it to reconstruct what happened?
- `friction`: How annoying was the process?
- `taste_alignment`: For UI or product work, did the output feel aligned with intent?

Use a 1-5 scale and require one sentence of evidence for unusually high or low scores.

This turns subjective discomfort into a comparable signal instead of a vague aftertaste.

## 7. Suggested Artifacts To Add

Your current `PROTOCOL_IMPROVEMENTS.md` pattern is good, but it should sit alongside a small observability layer.

Recommended additions:

### 7.1 Run ledger

One append-only per-project file, for example:

- `docs/agents/runs.jsonl`

One line per workflow run or task execution.

Purpose:

- trend analysis,
- cost analysis,
- and reconstructing pipeline behavior without reading scattered artifacts first.

### 7.2 Incident log

For notable failures, false passes, and regressions.

Suggested fields:

- `incident_id`
- `date`
- `project`
- `task_id`
- `severity`
- `failure_type`
- `detected_by`
- `escaped_stage`
- `root_cause_guess`
- `linked_run_id`
- `protocol_change_candidate`

This complements the improvements log by making incident analysis more explicit.

### 7.3 Eval set manifest

Small but representative.

Suggested fields:

- `eval_id`
- `task_class`
- `difficulty`
- `requires_ui`
- `requires_parallelism`
- `requires_qa`
- `golden_outcome_definition`
- `scoring_notes`

This is what protocol changes should be tested against before full adoption.

### 7.4 Reviewer scorecard

For Validator, QA, or operator experiential review.

Suggested fields:

- `correctness`
- `scope_fit`
- `user_value`
- `clarity`
- `friction`
- `confidence`
- `change_needed`

## 8. Implications For Your Current Reviewer/Enforcer Pattern

Your current pattern was:

- log protocol improvements,
- have a reviewer assess and triage them,
- revise the handoff/prompt layer,
- then have an enforcer sync projects.

That pattern is fundamentally sound. The main changes I recommend are:

### 8.1 Keep the improvement log, but enrich the evidence feeding it

Do not rely on the log alone.

Feed it with:

- run metrics,
- incident records,
- sampled transcript review,
- false-pass analysis,
- and operator scorecards.

### 8.2 Treat the reviewer as an evaluation function, not necessarily a permanent role

The "reviewer" can still exist as an Architect-mode or review-mode agent, but its job should be:

- cluster failures,
- distinguish anecdote from trend,
- propose the smallest effective change,
- and predict how the change should alter eval outcomes.

That is different from merely rewriting prompts.

### 8.3 Keep the enforcer, but move it later in the chain

The Enforcer should run after:

- evidence review,
- change approval,
- and at least a lightweight regression check on a representative eval set.

That keeps project sync work from propagating unproven protocol edits.

### 8.4 Prefer one review function during execution, not many

For ordinary task execution, avoid stacking:

- architect,
- designer,
- reviewer,
- doer,
- assessor,
- and post-reviewer

unless the task clearly benefits.

For most tasks, one good implementer plus one independent validator is the highest-leverage combination.

## 9. Recommended Decision Rules For Extra External Agents

Use this policy:

### Add a pre-implementation external agent when:

- the user brief is ambiguous,
- product taste matters substantially,
- there are conflicting goals,
- or the implementation risk depends heavily on decomposition quality.

### Add an in-flight assessor when:

- the work has meaningful branching options,
- the cost of going down the wrong path is high,
- or there is a specific question that can be answered without blocking all progress.

### Add a post-implementation assessor when:

- static correctness is insufficient,
- UX/workflow quality matters,
- or trust, clarity, and real usage behavior are central.

### Do not add an extra agent when:

- it would only restate the same context in different words,
- it has no independent evaluation lens,
- it cannot change the decision outcome materially,
- or its main value is emotional reassurance rather than new signal.

## 10. Suggested Default Policy

If you want a crisp operating rule for THE_FACTORY, this is the one I recommend:

1. Default to one implementer and one validator.
2. Add a pre-implementation interviewer only for ambiguity-heavy or UX-heavy tasks.
3. Add a code-aware planner only for high-risk or integration-heavy tasks.
4. Add experiential QA only when behavior matters beyond static correctness.
5. Add standing roles only after repeated failures or measured eval gains.
6. Change protocol only after evidence and representative re-testing.
7. Propagate protocol changes with the Enforcer only after approval and basic regression confidence.

## 11. Workspace-Specific Observations

These observations came from reading the current THE_FACTORY root docs during this research pass.

### 11.1 Current protocol direction is already strong

The current protocol already contains two important principles that align with the research:

- add a new role or phase only after repeated failure or clear eval improvement,
- and keep a lightweight protocol eval set. See [OPERATOR_PROTOCOL.md:75](/Users/brach/Documents/THE_FACTORY/OPERATOR_PROTOCOL.md#L75) and [OPERATOR_PROTOCOL.md:1557](/Users/brach/Documents/THE_FACTORY/OPERATOR_PROTOCOL.md#L1557).

That is a strong foundation.

### 11.2 The current cadence is still more feature-count-driven than signal-driven

The current wording recommends protocol review every 5-10 features. See [OPERATOR_PROTOCOL.md:1509](/Users/brach/Documents/THE_FACTORY/OPERATOR_PROTOCOL.md#L1509).

That is workable, but the research-backed upgrade is to make cadence depend more on:

- incident rate,
- false-pass rate,
- rework rate,
- and workflow-change pressure,

with weekly ops review plus monthly protocol review.

### 11.3 The improvements log currently has a reliability gap in this workspace state

During this research pass, `PROTOCOL_IMPROVEMENTS.md` was referenced by protocol docs and tracked in git, but absent from the working tree on 2026-03-20. That is not a design criticism of the protocol itself, but it is an operational reliability issue because a missing root backlog weakens auditability and review discipline.

## 12. Source Notes

The sources below were chosen because they are either:

- primary product/engineering guidance from teams actively shipping agent systems, or
- widely cited research directly relevant to multi-agent software-development workflows.

I put more weight on newer operational guidance and newer SWE evidence than on older "AI company" role-simulation papers when they conflicted.

## 13. Sources

1. Anthropic, "Building effective agents"  
   [https://www.anthropic.com/engineering/building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents)

2. Anthropic, "Demystifying evals for AI agents"  
   [https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

3. Anthropic, "How we built our multi-agent research system"  
   [https://www.anthropic.com/engineering/multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system)

4. OpenAI, "Evaluation best practices"  
   [https://developers.openai.com/api/docs/guides/evaluation-best-practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)

5. OpenAI, "Agent evals"  
   [https://developers.openai.com/api/docs/guides/agent-evals](https://developers.openai.com/api/docs/guides/agent-evals)

6. OpenAI, "Trace grading"  
   [https://developers.openai.com/api/docs/guides/trace-grading](https://developers.openai.com/api/docs/guides/trace-grading)

7. OpenAI API Reference, "Costs"  
   [https://developers.openai.com/api/reference/resources/organization/subresources/audit_logs/methods/get_costs](https://developers.openai.com/api/reference/resources/organization/subresources/audit_logs/methods/get_costs)

8. Agentless, "Demystifying LLM-based Software Engineering Agents"  
   [https://arxiv.org/abs/2407.01489](https://arxiv.org/abs/2407.01489)

9. ChatDev, "Communicative Agents for Software Development"  
   [https://arxiv.org/abs/2307.07924](https://arxiv.org/abs/2307.07924)

10. MetaGPT, "Meta Programming for A Multi-Agent Collaborative Framework"  
   [https://openreview.net/forum?id=VtmBAGCN7o](https://openreview.net/forum?id=VtmBAGCN7o)
