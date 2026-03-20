# RESPECTIVE AGENT STRENGTHS suggestions-gpt

Date: 2026-03-20
Status: Draft

## Objective

Translate the strongest, lowest-risk findings from:

- `support/v1.9/Improvement Research/RESPECTIVE-AGENT-STRENGTHS-research-gpt.md`
- `support/v1.9/Improvement Research/RESPECTIVE-MODEL-STRENGTHS research-claude`
- root THE_FACTORY protocol files

into implementation suggestions for THE_FACTORY's pipeline.

Only include changes that are likely to improve pipeline quality regardless of which frontier model is used.

## Executive Summary

The research does support a few concrete pipeline improvements, but it mostly validates ideas THE_FACTORY already has:

- externalized state,
- self-contained dispatch,
- independent verification,
- and role separation between planning, execution, validation, and QA.

The strongest new takeaway is not "pick a different default model." It is:

1. make re-planning triggers explicit,
2. make verification expectations more explicit inside handoffs,
3. and encode in protocol review that scaffold improvements beat model churn.

Those changes are small, concrete, and directly supported by the research.

## What THE_FACTORY Already Gets Right

The current protocol already aligns well with the research on the most important points:

- `OPERATOR_PROTOCOL.md` already treats artifacts as the durable memory layer.
- `templates/orchestrator-state.md` already externalizes project state instead of trusting chat memory.
- `templates/handoff-packet.md` already requires bounded scope, explicit outputs, and interface contracts.
- `Validator` and `QA Tester` are already separated, which matches the research distinction between contract validation and live-behavior verification.
- Claude Code guidance already requires complete handoff content inline when spawning subagents.

This matters because the research repeatedly says harness quality and workflow design are more important than small frontier-model deltas.

## Improvements Worth Taking

### 1. Add first-class checkpoint and re-plan triggers to handoffs

Why this is strongly supported:

- Both research documents say long-horizon planning remains weak across models.
- The safest pattern is externalized state plus checkpoint-based re-planning.
- THE_FACTORY already externalizes state, but handoffs do not yet force the Orchestrator to define when execution should stop and return for re-planning.

Recommended change:

Add a section to `templates/handoff-packet.md` and the matching schema in `OPERATOR_PROTOCOL.md`:

```markdown
## Replan Triggers
- Stop and return to Orchestrator if: [condition]
- Stop and return to Orchestrator if: [condition]
- Otherwise continue: [YES | NO]
```

Good trigger examples:

- required file or interface is missing,
- acceptance criteria conflict with discovered implementation reality,
- more than one out-of-scope file would need to change,
- tests fail for unrelated reasons,
- a hidden dependency blocks completion.

Expected benefit:

- fewer bad autonomous runs,
- less drift during execution,
- cleaner escalation when reality changes.

### 2. Add explicit verification procedure and evidence requirements to handoffs

Why this is strongly supported:

- The research repeatedly shows that workflow quality depends on the scaffold, especially how subtasks are specified and how outputs are checked.
- THE_FACTORY handoffs define success conditions, but they do not always define exactly what proof the downstream validator should expect.
- This gap is model-independent, so tightening it should help regardless of vendor choice.

Recommended change:

Add a section to `templates/handoff-packet.md`:

```markdown
## Verification Procedure
- Required checks: [tests, commands, artifact checks, manual verification boundaries]
- Evidence required in session summary: [what must be reported]
- Evidence required for Validator PASS: [what must be observable]
```

Then extend the Validator guidance in `OPERATOR_PROTOCOL.md` so verdicts check the task against this section, not just against generic acceptance criteria.

Expected benefit:

- fewer false passes,
- more consistent validation quality,
- clearer contracts between Developer and Validator.

### 3. Update protocol review to prefer scaffold fixes before model-routing fixes

Why this is strongly supported:

- Both research documents state that scaffold quality often matters more than swapping between top frontier models.
- THE_FACTORY's review loop should encode that principle directly so future improvements do not overfit to transient benchmark differences.

Recommended change:

Add one explicit rule to `PROTOCOL_REVIEW_PROMPT.md`:

- Before proposing model-selection changes, first evaluate whether the issue would be better fixed by a schema change, hook, checklist, eval, or dispatch-quality improvement.

Expected benefit:

- more stable protocol evolution,
- less churn driven by benchmark headlines,
- more improvements landing at the actual failure layer.

## Improvements I Do Not Recommend Yet

### 1. Do not hard-code a detailed model routing matrix into the core protocol

Reason:

- The research does show real model specialization.
- But the root workspace currently contains two different operating shapes:
  - the role-based `OPERATOR_PROTOCOL.md` system,
  - and the leaner skill-based `CLAUDE.md` constitution.
- Hard-coding model-routing guidance before the operating model is fully unified would add ambiguity faster than it would add quality.

Safer alternative:

- keep model selection as an implementation note or appendix,
- do not make it a core protocol dependency yet.

### 2. Do not add more standing roles based on the strengths research alone

Reason:

- The research supports specialization of behavior.
- It does not support role proliferation as the default answer.
- THE_FACTORY already has enough separation of concerns for planning, execution, validation, and QA.

Safer alternative:

- improve dispatch contracts,
- improve handoff schema,
- improve verification gates,
- and use skills or temporary modes before adding new standing roles.

### 3. Do not trust self-assessment as a primary quality gate

Reason:

- Both research documents explicitly reject self-assessment as a reliable standalone mechanism.
- THE_FACTORY is already stronger here than most systems because it separates producer summaries from Validator judgment.

Implication:

- keep self-report fields in session summaries,
- but do not expand the protocol in ways that let agents certify their own correctness.

## Concrete File Targets

If these suggestions are adopted, the best insertion points are:

- `templates/handoff-packet.md`
- `OPERATOR_PROTOCOL.md` section `2.1 Handoff Packet`
- `OPERATOR_PROTOCOL.md` section `2.7 Validator Verdict`
- `PROTOCOL_REVIEW_PROMPT.md`

## Bottom Line

The strongest pipeline improvement from the agent/model-strengths research is not a vendor switch.

It is a tighter execution scaffold:

- explicit re-plan triggers,
- explicit verification evidence,
- and protocol-review bias toward scaffold fixes over model churn.

Those changes fit THE_FACTORY's current strengths and should improve quality even if the underlying model roster changes later.
