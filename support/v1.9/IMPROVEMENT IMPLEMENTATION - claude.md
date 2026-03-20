# THE_FACTORY Improvement Implementation Plan

**Date:** 2026-03-20
**Status:** Master Rollout Plan
**Source:** Synthesis of all six improvement suggestion documents in `support/v1.9/Improvement Suggestions/`

---

## Executive Summary

Six documents produced by two models (Claude + GPT) across three research domains (meta-layer, review protocol, agent strengths) converge on a single thesis:

> THE_FACTORY needs better **intent capture**, **observability**, and **source-of-truth consistency** — not more roles. Scaffold quality is a 12-22x bigger lever than model choice.

The biggest immediate blocker is **architectural drift**: `OPERATOR_PROTOCOL.md` (v1.8, role-heavy) and `CLAUDE.md` (v1.9.1, skills-first) describe two different systems. Every later improvement depends on resolving this first.

---

## Rollout Phases

### Phase 0: Canonicalize the Operating Model

**Why first:** Every document flags this. You can't improve a pipeline when two root docs describe different pipelines.

| # | Change | Target File(s) | Effort |
|---|--------|----------------|--------|
| 0.1 | Declare v1.9.1 (CLAUDE.md) as canonical operating model | README.md | Small |
| 0.2 | Rewrite OPERATOR_PROTOCOL.md to describe the skills-and-evals architecture, or explicitly label it as legacy reference | OPERATOR_PROTOCOL.md | Large |
| 0.3 | Update INIT.md to route new users into the actual v1.9.1 pipeline | INIT.md | Medium |
| 0.4 | Update IMPLEMENTATION_PROMPT.md to scaffold the current system (.agent/, skills, trigger table) instead of the older preamble-heavy model | IMPLEMENTATION_PROMPT.md | Medium |
| 0.5 | Restore single PROTOCOL_IMPROVEMENTS.md path — either at root or in .agent/, and update all references to point to one location | PROTOCOL_IMPROVEMENTS.md | Small |
| 0.6 | Fix housekeeping: missing constitution.md reference, YAML frontmatter inconsistencies in templates, spec.md blockquote metadata | templates/, OPERATOR_PROTOCOL.md | Small |

**Gate:** Phase 0 complete when a fresh agent reading root docs gets a consistent picture of one operating model.

---

### Phase 1: Intent Capture & Dispatch Quality

**Why next:** The cheapest, highest-leverage improvements. Front-loads spec quality without new artifacts or roles.

| # | Change | Target File(s) | Effort |
|---|--------|----------------|--------|
| 1.1 | **Frozen/mutable spec split** — update spec.md template with frozen section (operator-authored, agent-read-only) and mutable section (agent-appended, timestamped, traceable) | templates/spec.md | Medium |
| 1.2 | **Project Definition Record** — new template for durable project intent: problem, users, outcomes, non-goals, constraints, quality priorities, UX intent, decision rights (Always/Ask First/Never), tagged assumptions, known unknowns | templates/project-definition-record.md | Medium |
| 1.3 | **Enhanced dispatch readiness gate** — add intent-completeness checks: explicit user/problem/outcome, non-goals, hard constraints, testable acceptance criteria, explicit assumptions if dispatching with uncertainty | Flow skills, OPERATOR_PROTOCOL.md §4.1 | Small |
| 1.4 | **Structured questioning protocol** — define minimum required question categories (product reality, UX intent, decision boundaries, quality attributes, evidence plan, success criteria) as a repeatable elicitation step | New: skills/discovery-governance/ or feature-flow Phase 0 | Medium |
| 1.5 | **Negative constraints in flow skills** — add explicit "do NOT do" guardrails mirroring the constitution pattern (e.g., debug-flow: "Do NOT refactor surrounding code while fixing a bug") | .claude/skills/debug-flow/, feature-flow/, refactor-flow/ | Small |

**Gate:** Phase 1 complete when dispatch cannot proceed without explicit user/problem/outcome/non-goals/constraints.

---

### Phase 2: Observability & Structured Evidence

**Why next:** You can't improve what you can't measure. These artifacts feed the review cadence in Phase 3.

| # | Change | Target File(s) | Effort |
|---|--------|----------------|--------|
| 2.1 | **Run records** — add runs.jsonl per project (append-only). Fields: run_id, date, project_id, task_id, task_type, agents/skills invoked, prompt/skill versions, result, rework_required, validator_result, qa_result, attempt_count, input/output tokens, tool_calls, latency_ms, estimated_cost | .agent/runs.jsonl, .agent/schemas/ | Medium |
| 2.2 | **Incident log** — add incidents.jsonl for false passes, escaped defects, regressions. Fields: incident_id, date, project, task_id, severity, failure_type, detected_by, escaped_stage, root_cause_classification, protocol_change_candidate | .agent/incidents.jsonl, .agent/schemas/ | Medium |
| 2.3 | **Evidence Review Packet** — new template capturing learning delta between execution waves. Fields: what changed, evidence observed, assumptions invalidated/strengthened, new questions, proposed changes, deferred items, next-slice recommendation, dispatch status (READY / READY WITH EXPLICIT ASSUMPTIONS / NOT READY) | templates/evidence-review-packet.md | Medium |
| 2.4 | **Checkpoint fields in task JSONL** — add plan_checkpoints field so flow skill phase transitions persist. If session dies, next session replans from last checkpoint, not from scratch | .agent/schemas/, flow skill definitions, scripts/tasks.sh | Small |
| 2.5 | **Replan triggers in handoffs** — add "Replan Triggers" section to handoff template (stop and return if: missing file/interface, acceptance criteria conflict, >1 out-of-scope file, unrelated test failures, hidden dependencies) | templates/handoff-packet.md | Small |
| 2.6 | **Verification procedure in handoffs** — add required checks, evidence requirements for session summary, evidence required for Validator PASS | templates/handoff-packet.md, OPERATOR_PROTOCOL.md §2.7 | Small |

**Gate:** Phase 2 complete when every completed task writes a run record, and incidents have a structured capture path.

---

### Phase 3: Review Cadence & Failure Routing

**Why next:** Now that data exists, use it to drive protocol improvement.

| # | Change | Target File(s) | Effort |
|---|--------|----------------|--------|
| 3.1 | **Signal-driven review cadence** — replace "every 5-10 features" with: per-task run data, weekly ops review (rates/incidents/costs), monthly protocol review (durable changes backed by evidence), quarterly structural review (role additions/removals) | OPERATOR_PROTOCOL.md §10.1 | Small |
| 3.2 | **Event-driven evidence reviews** — trigger Evidence Review Packet after: first prototype, first end-to-end slice, operator discomfort, architectural surprise, repeated validator/QA failure patterns, 2-5 uncertain tasks, before large batch commitment | Flow skills (feature-flow especially) | Small |
| 3.3 | **Three review layers made explicit** — (A) Task validation: Validator, contract checks. (B) Experiential review: QA/operator scorecard (clarity, confidence, surprise, friction, taste alignment, 1-5 with evidence for outliers). (C) Pipeline review: weekly/monthly cadence using run records + incident logs | OPERATOR_PROTOCOL.md | Medium |
| 3.4 | **Root-cause classification before protocol changes** — mandatory step in protocol review: classify failure as SPECIFICATION_OR_SYSTEM_DESIGN, HANDOFF_OR_ALIGNMENT, or VERIFICATION_OR_TERMINATION. Then: What failed? What evidence? Why did current gate miss it? Smallest fix in correct layer? What eval should improve? | PROTOCOL_REVIEW_PROMPT.md | Small |
| 3.5 | **Scaffold-first bias in protocol review** — before proposing model-selection changes, first evaluate whether the issue is better fixed by schema change, hook, checklist, eval, or dispatch-quality improvement | PROTOCOL_REVIEW_PROMPT.md | Small |
| 3.6 | **Verification subagent in flow skills** — each flow skill includes an explicit verification step that runs in a separate context (not self-review). Even a subagent dispatch within the same session counts | .claude/skills/debug-flow/, feature-flow/, refactor-flow/ | Medium |

**Gate:** Phase 3 complete when protocol review requires evidence inputs (not just backlog items) and classifies failures before proposing fixes.

---

### Phase 4: Metrics Expansion & Hardening

**Why last:** Refinement layer. Only worth pursuing after Phases 0-3 are stable.

| # | Change | Target File(s) | Effort |
|---|--------|----------------|--------|
| 4.1 | **Expand metrics beyond token profiling** — track four families: outcome (first-pass success, escaped defects, rework rate, operator override rate), efficiency (cycle time, handoff count, blocked rate), cost (tokens, tool calls, cost per successful task), qualitative (clarity, confidence, friction, surprise) | .agent/metrics/ | Medium |
| 4.2 | **Intent-quality metrics** — track late [ASK OPERATOR] incidents, mid-build reversals, validator failures from missing intent, operator UX dissatisfaction, assumption invalidation frequency | .agent/metrics/ | Small |
| 4.3 | **Iteration caps** — doer/verifier loop: cap at 3. Reviewer refinement: cap at 2. When cap hit, log incident and escalate instead of silently retrying | Flow skills, OPERATOR_PROTOCOL.md | Small |
| 4.4 | **Validator false-pass/false-fail tracking** — add validator_false_pass_rate, validator_false_fail_rate, revision_loop_rate, tokens_per_rework to metrics | .agent/metrics/, incidents.jsonl schema | Small |
| 4.5 | **Variant testing** — version prompts/skills/flows explicitly, record version lineage in run ledger, run representative eval set against old vs new before promoting changes | .agent/evals/, runs.jsonl | Medium |

**Gate:** Phase 4 complete when you can answer "what is our first-pass success rate?" and "which task classes cost the most?" from structured data.

---

## Deferred (Revisit After Phase 4)

These have research support but depend on earlier phases being stable:

| Change | Prerequisite | Trigger to Revisit |
|--------|-------------|---------------------|
| Multi-model routing (Claude orchestrate, GPT execute, Gemini research) | API-driven pipeline (e.g., CRUCIBLE) | When programmatic model routing becomes possible |
| Conformance checks against frozen spec | Phase 1 frozen/mutable split in place | After 10+ tasks use the new spec format |
| LLM-as-Judge for subjective evaluation | Enough run/incident data to know where subjective failures cluster | After incident data shows subjective-quality failure patterns |
| Specialist agent triggers as opt-in paths (pre-implementation interviewer, experiential QA) | Phase 3 review cadence running | When evals show measurable gain from specialist passes |

---

## What NOT To Do

Every document agrees on these anti-patterns:

1. **No new standing roles.** Meta-layer = flow skill, not new org chart.
2. **No spec-as-source.** Stay spec-anchored. The spec informs and constrains but isn't the sole generative artifact.
3. **No over-engineered outer loop.** If reviewing takes longer than executing, the process is too heavy.
4. **No unstructured questioning.** "Ask lots of questions" must be a repeatable protocol with defined categories.
5. **No unbounded retry loops.** Cap iterations. Log incidents. Escalate.
6. **No artifacts with no dispatch effect.** Every artifact must change routing, scope, or acceptance criteria — or it is analysis theater.
7. **No forked source of truth.** One canonical operating model in root docs.
8. **No model-churn-driven protocol edits.** Scaffold improvements first, model swaps second.

---

## Success Metrics

After full rollout, these should improve:

| Metric | Measures | Baseline |
|--------|----------|----------|
| Late [ASK OPERATOR] incidents | Intent capture quality | Establish from first 20 tasks |
| Mid-build requirement reversals | Dispatch readiness | Establish from first 20 tasks |
| First-pass success rate | Overall pipeline quality | Establish from runs.jsonl |
| Escaped defect rate | Validator effectiveness | Establish from incidents.jsonl |
| Cost per successful task | Efficiency | Establish from runs.jsonl |
| Rework rate | Spec + dispatch quality | Establish from runs.jsonl |
| Spec revision frequency | Frozen/mutable split value | Compare before/after Phase 1 |

If these do not improve after a phase, simplify the additions from that phase before proceeding.

---

## Minimum Viable Experiment

If testing with smallest possible commitment, implement only:

1. **Phase 0.1-0.2** — Canonicalize the source of truth
2. **Phase 1.2** — Project Definition Record
3. **Phase 1.3** — Enhanced dispatch readiness gate
4. **Phase 2.3** — Evidence Review Packet

Pilot on one new feature or project bootstrap. Measure late clarifications, mid-build reversals, and operator satisfaction. Keep only what earns its cost.

---

## Document Sources

All six input documents, in order of breadth:

1. `THE_FACTORY-pipeline-improvement-synthesis.md` — Broadest synthesis. Identified Priority 0 (canonicalize operating model), four-tier priority system, file-level change targets.
2. `META_LAYER_PIPELINE_RECOMMENDATIONS.md` — Meta-layer executive decision. Project Definition Record, Evidence Review Packet, expanded questioning, dispatch readiness, event-driven review, assumption tracking.
3. `META-LAYER IMPLEMENTATION - claude.md` — Detailed meta-layer implementation. Frozen/mutable spec, questioning protocol with 10-question minimum, three-tier boundary model, gap analysis vs. existing infrastructure.
4. `REVIEW PROTOCOL IMPLEMENTATION - claude.md` — Review protocol implementation. Frozen/mutable spec split, signal-driven cadence, three review layers, run records, incident logs, discovery-governance flow skill.
5. `RESPECTIVE AGENT STRENGTHS suggestions-claude.md` — Agent scaffold improvements. Checkpoint-based re-planning, verification subagent, negative constraints in flow skills. Core finding: scaffold = 12-22 point swing, model swap = ~1 point.
6. `RESPECTIVE AGENT STRENGTHS suggestions-gpt.md` — Handoff scaffold improvements. Replan triggers, verification procedure + evidence requirements, scaffold-first bias in protocol review.
