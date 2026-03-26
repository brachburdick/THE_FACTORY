# Proposal: Human Involvement Improvements for THE_FACTORY

**Source document:** `/Users/brach/Downloads/deep-research-report Human Involvement.md`  
**Date:** 2026-03-26  
**Status:** Proposal  
**Intent:** Turn the report's findings into concrete, low-bureaucracy changes for THE_FACTORY.

## Executive Summary

The report's core lesson is not "add more humans." It is "put humans where risk, ambiguity, and recovery need judgment, and automate the rest aggressively."

For THE_FACTORY, that implies five shifts:

- move away from blanket human gates for all feature work
- keep review local and fast via separate-context verification, not centralized approval
- interrupt the operator only when intent is ambiguous, evidence is weak, or blast radius is high
- treat reruns, waiting, and manual triage as measurable pipeline debt
- keep humans in command at the policy and exception layer, not in every routine step

THE_FACTORY already has the right backbone for this: one operator agent, hooks, section boundaries, and separate-context verification. The missing layer is an evidence-driven oversight model.

## What Already Fits The Research

- `CLAUDE.md` already favors hooks over prose and evals over ritual.
- `.claude/skills/feature-flow/SKILL.md`, `.claude/skills/debug-flow/SKILL.md`, and `.claude/skills/refactor-flow/SKILL.md` already define checkpoints that can host better oversight rules.
- `templates/handoff-packet.md` already captures scope boundaries, assumptions, open questions, evidence, and replan triggers.
- `templates/tasks.md` already distinguishes when QA is required.
- Section contracts are a good proxy for blast radius.

## Gaps This Report Exposes

- Feature work currently uses a blanket human gate: `.claude/skills/feature-flow/SKILL.md` requires human confirmation before implementation even when risk is low.
- Task and run records do not encode risk, evidence strength, ambiguity, or review latency, so oversight cannot be calibrated.
- `scripts/assess.py` measures ramp-up and subagent usage, but not waiting, review speed, reruns, or interruption burden.
- `.agent/incidents.jsonl` is empty, which means noisy exception handling is not being captured as system debt.
- There is no standard "agent abstain" packet; clarification quality is still prompt-dependent.
- The repo currently lacks real task/run/incident schemas, so any new oversight metadata could drift unless the schema layer is added first.

## Recommended Change Set

| Priority | Change | Why | Primary implementation surface |
|---|---|---|---|
| 1 | Risk-tiered oversight matrix | Replace blanket human gates with selective ones | `templates/spec.md`, `templates/tasks.md`, `.claude/skills/*-flow/SKILL.md` |
| 2 | Standard abstain packet + ambiguity lint | Interrupt only when justified, and make the ask easy to answer | `templates/handoff-packet.md`, `templates/plan.md`, `templates/spec.md` |
| 3 | Fast peer review packet + latency SLO | Make separate-context verification behave like local peer review, not bureaucracy | `templates/handoff-packet.md`, `.agent/runs.jsonl`, `scripts/assess.py` |
| 4 | Restart budget + automatic incident logging | Stop hiding flaky verification behind human heroics | `.claude/hooks/`, `.agent/incidents.jsonl`, `.agent/runs.jsonl`, `scripts/assess.py` |
| 5 | Explicit human-in-command policy | Put approval thresholds and stop conditions in the protocol, not in operator mood | `CLAUDE.md`, flow skills, templates |
| 6 | Oversight telemetry + targeted manual QA | Measure whether humans are placed well, and reserve QA for uncertain/high-impact cases | `.agent/runs.jsonl`, `scripts/assess.py`, `templates/tasks.md`, `LEARNINGS.md` |

## 1. Introduce A Risk-Tiered Oversight Matrix

**Why:** The report argues that human involvement should vary by blast radius, evidence strength, and ambiguity. THE_FACTORY currently varies by task type, but not enough by risk.

**Proposal:**

- Add these fields to `templates/spec.md` and `templates/tasks.md`:
  - `risk_tier`: `low | medium | high`
  - `evidence_strength`: `strong | mixed | weak`
  - `ambiguity_status`: `clear | partial | blocked`
  - `oversight_mode`: `fully_automated | human_on_loop | human_in_loop | human_in_command`
- Update the flow skills so oversight mode is chosen from those fields instead of from task type alone.
- Remove the universal "human confirmation required before proceeding" rule from low-risk feature work.

**Suggested oversight matrix:**

| Conditions | Mode | Behavior |
|---|---|---|
| Low risk + strong evidence + clear intent | `fully_automated` or `human_on_loop` | Agent proceeds; human reviews only on anomaly or failed verification |
| Medium risk or mixed evidence | `human_on_loop` | Agent proceeds with separate-context verification; operator only resolves real open questions |
| High risk, weak evidence, or ambiguous intent | `human_in_loop` | Blocking approval before implementation and before closure |
| Policy thresholds and exceptions | `human_in_command` | Human sets the rules, thresholds, and stop conditions ahead of time |

**Initial high-risk triggers for THE_FACTORY:**

- cross-section changes
- multi-project changes
- security/auth/credentials work
- destructive or irreversible operations
- data/schema migrations
- no reliable baseline tests
- unclear ownership or rollback path

**Expected outcome:** fewer unnecessary pauses, with stricter review where it actually matters.

## 2. Add A Standard Abstain Packet And Ambiguity Lint

**Why:** The report recommends interrupting humans only when justified, and with calibrated, low-cognitive-load asks. THE_FACTORY should make "pause and ask" a protocol artifact, not a vibe.

**Proposal:**

- Extend `templates/handoff-packet.md` with a compact abstain block:
  - `Blocked because`
  - `Missing evidence`
  - `Recommended safe default`
  - `Reply with`
- Extend `templates/plan.md` or `templates/spec.md` with an ambiguity checklist for:
  - environment
  - blast radius
  - rollback path
  - success criteria
  - owner or approver
  - verification method
- Update flow skills so agents batch missing information into one packet instead of drip-feeding multiple questions.

**Decision rule:** if the agent cannot name the missing fact, the blocked decision, and a safe default, it should keep working; if it can, it should ask once with structure.

**Expected outcome:** fewer clarification turns, faster human responses, less rework caused by underspecified intent.

## 3. Recast Separate-Context Verification As Fast Peer Review

**Why:** The report is clear that local, peer-style review plus automation beats heavyweight approval structures. THE_FACTORY already has separate-context verification; it needs to optimize that mechanism for speed and clarity.

**Proposal:**

- Treat the verifier packet as the equivalent of a fast peer review, not an extra ceremony.
- Reuse `templates/handoff-packet.md` as the standard review packet with:
  - changed scope
  - acceptance criteria
  - evidence produced
  - residual risks
  - open questions
- Add review timing fields to `.agent/runs.jsonl`:
  - `review_started_at`
  - `review_completed_at`
  - `review_wait_minutes`
  - `review_blockers`
- Update `scripts/assess.py` to report review latency by risk tier.

**Operational rule:** keep operator review reserved for medium/high-risk or unresolved cases. Low-risk work should usually terminate at separate-context verification, not at a blocking human signoff.

**Expected outcome:** review remains local and auditable without becoming a CAB-style bottleneck.

## 4. Add A Restart Budget And Automatic Incident Logging

**Why:** The report shows that manual restarts and flaky verification are hidden throughput killers. THE_FACTORY already worries about pre-existing failures, but it does not yet make rerun behavior visible or costly.

**Proposal:**

- Add a restart budget for verification:
  - 2 identical verification reruns without a code change opens an incident
  - repeated "same pre-existing failures" cannot count as green unless they are on an explicit quarantine list
- Automatically append to `.agent/incidents.jsonl` when a session ends as:
  - `failed`
  - `blocked`
  - `escalated`
  - `rerun_budget_exceeded`
- Extend `.agent/runs.jsonl` with:
  - `verification_attempts`
  - `same_command_reruns`
  - `preexisting_failures_accepted`
  - `incident_id`
- Extend `scripts/assess.py` to report rerun rates and incident rates.

**Expected outcome:** fewer "green by repetition" sessions and a believable failure-learning loop.

## 5. Make Human-In-Command Policy Explicit

**Why:** The report's strongest governance point is that humans should set thresholds, risk budgets, and stop conditions, while automation executes within those bounds.

**Proposal:**

- Add a short `Oversight Policy` section to `CLAUDE.md` that defines:
  - which work can be fully automated
  - which work is human-on-the-loop by default
  - which work requires blocking human approval
  - what evidence is required to move between those modes
- Add matching fields to templates so policy becomes part of task artifacts, not just top-level prose.
- Add explicit stop-the-line triggers:
  - ambiguous intent
  - failing baseline tests
  - section boundary change without contract update
  - destructive operation
  - missing rollback or recovery path
  - unowned cross-project dependency

**Important constraint:** do not respond to this research by creating a protocol review board or mandatory human signoff for every spec. That would move THE_FACTORY in the wrong direction.

**Expected outcome:** more consistent operator decisions, less ad hoc gating, clearer audit trail.

## 6. Expand Oversight Telemetry And Make Manual QA Selective

**Why:** The report emphasizes that waiting, interruptions, and manual triage are real costs. THE_FACTORY cannot improve placement of humans if it does not measure those costs.

**Proposal:**

- Extend `.agent/runs.jsonl` with:
  - `oversight_mode`
  - `agent_escalations`
  - `operator_interrupts`
  - `clarification_rounds`
  - `operator_wait_minutes`
  - `uncertain_cases`
  - `manual_qa_required`
  - `manual_qa_reason`
- Update `scripts/assess.py` to report:
  - interruption rate
  - review latency
  - operator wait time
  - reruns per completed task
  - incident rate by risk tier
  - manual QA load
- Keep manual QA focused on uncertain or high-impact cases:
  - UI behavior
  - hardware mutation
  - external side effects
  - unresolved verification confidence
- Reuse the question-list QA style already documented in `LEARNINGS.md` so manual review stays precise.

**Expected outcome:** better human placement, fewer low-value interruptions, and clearer evidence for future threshold tuning.

## Rollout Plan

### Phase 1: Artifact And Policy Layer

- Create real JSON schemas for task, run, and incident records before adding new oversight fields.
- Add risk, evidence, ambiguity, and oversight fields to `templates/spec.md` and `templates/tasks.md`.
- Add the abstain packet and ambiguity checklist to templates.
- Update flow skills to use the oversight matrix.

### Phase 2: Runtime And Logging Layer

- Add restart-budget behavior and automatic incident creation.
- Extend run records with review, rerun, and interruption metadata.
- Update hooks only where deterministic enforcement makes sense; keep nuanced judgment in the flow skills.

### Phase 3: Assessment And Calibration

- Extend `scripts/assess.py` to trend oversight metrics by risk tier.
- Pilot the new model on THE_FACTORY's own internal tasks first.
- After 10-20 sessions, tune thresholds based on observed friction and escaped defects.

## Success Criteria

- Low-risk tasks are no longer blocked by universal human approval.
- Medium/high-risk tasks show clearer, faster, more structured review behavior.
- Empty incident history becomes impossible.
- `scripts/assess.py` reports waiting, reruns, and interruption metrics alongside current ramp-up metrics.
- Manual QA requests become narrower and more explicit.
- Escaped defects and reopened work do not increase after loosening low-risk gates.

## Anti-Goals

- Do not add a CAB-style approval board.
- Do not require human signoff on every spec, plan, or implementation step.
- Do not use model self-confidence alone as a gate.
- Do not hide flaky verification behind repeated reruns.
- Do not add more oversight prose without hooks, templates, or telemetry backing it.

## Bottom Line

The report does not argue for "more human involvement." It argues for **better human placement**.

For THE_FACTORY, the right move is to:

- loosen routine low-risk gates
- tighten exception handling
- standardize abstain behavior
- measure review and interruption costs
- keep humans in command of policy rather than buried in every execution path

That would turn human oversight from a source of friction into a deliberate control system.
