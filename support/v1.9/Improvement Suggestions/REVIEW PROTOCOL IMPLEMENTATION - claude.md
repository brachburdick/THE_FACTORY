# Improvement Recommendations for THE_FACTORY's Agentic Pipeline

**Date:** 2026-03-20
**Source material:** REVIEW-PROTOCOL research (Claude + GPT), META-LAYER research (Claude + GPT)
**Cross-referenced against:** CLAUDE.md constitution v1.9.1, OPERATOR_PROTOCOL v1.8, INIT.md, IMPLEMENTATION_PROMPT.md, PROTOCOL_REVIEW_PROMPT.md

---

## 1. What The Research Converges On

All four documents independently arrive at the same core thesis:

> The missing capability is not more roles. It is a formalized discovery/governance control plane and a structured observability layer — both implemented as lightweight flows and artifacts, not standing personas.

This aligns with the v1.9 direction (skills over roles, evals over docs). The research validates the trajectory and identifies specific gaps.

---

## 2. High-Impact Changes (Adopt Now)

### 2.1 Add a Frozen/Mutable Spec Pattern

**Gap:** The current `spec.md` template (§2.5) has no formal distinction between original operator intent and agent-discovered requirements. Spec drift is invisible — agents can silently rewrite original intent during revision passes.

**Recommendation:** Split `spec.md` into two sections:
- **Frozen section** — original requirements as stated by the operator. Agents can reference but not modify.
- **Mutable section** — discovered requirements, clarifications, architectural decisions surfaced during implementation. Timestamped, attributed to originating agent/cycle. Each entry must reference the frozen requirement it relates to.

This is the single highest-leverage structural change. It makes drift machine-detectable.

**Source:** META-LAYER research (Claude) §6.1.2, META-LAYER research (GPT) §4.3

### 2.2 Add a Progress Ledger Artifact

**Gap:** The Orchestrator State Snapshot (§2.8) tracks task status but not what reality taught us since the last cycle. There is no session-bridging artifact that captures learning, invalidated assumptions, or proposed requirement changes.

**Recommendation:** Add an Evidence Review Packet artifact:
- What changed since last review
- Assumptions invalidated / strengthened
- New questions surfaced
- Requirement/UX/architecture changes proposed
- Dispatch status: READY / READY WITH EXPLICIT ASSUMPTIONS / NOT READY

**Trigger:** After first prototype, after first end-to-end slice, after any notable operator discomfort, after any architectural surprise, before committing to a large batch.

**Source:** META-LAYER research (GPT) §4.3 Artifact B, META-LAYER research (Claude) §6.1.3

### 2.3 Formalize the Dispatch Readiness Gate with Intent Checks

**Gap:** The current Dispatch Readiness Gate (§4.1) checks mechanical completeness (paths exist, markers resolved, atomization test passed) but does not check whether enough intent signal exists to proceed safely.

**Recommendation:** Add to the existing gate:
- User/problem/desired outcome are explicit (not just inferred from task title)
- Non-goals are stated
- Hard constraints are listed
- Acceptance criteria are testable, not vague

This is the cheapest way to front-load spec quality without adding a new agent.

**Source:** META-LAYER research (GPT) §9 (Minimal Version), REVIEW-PROTOCOL research (GPT) §4.2

### 2.4 Shift Review Cadence from Feature-Count to Signal-Driven

**Gap:** §10.1 recommends protocol review "every 5-10 features." This is workable but does not respond to actual quality signals.

**Recommendation:** Replace with:
- **Weekly ops review** (30-45 min): scan pass rates, rework rates, block reasons, false-pass examples, cost hotspots. Produce quick mitigations and deferred investigations.
- **Monthly protocol review**: only promote changes backed by repeated failure, measured friction, or eval gains.
- **Quarterly structural review**: whether roles should be added/removed, whether specialist paths should be promoted, whether handoff overhead has accumulated.

The weekly cadence catches problems before they harden. The monthly cadence prevents impulsive protocol edits.

**Source:** REVIEW-PROTOCOL research (GPT) §5, REVIEW-PROTOCOL research (Claude) — both converge on this exact cadence.

---

## 3. Medium-Impact Changes (Adopt in Next Iteration)

### 3.1 Add Structured Run Records

**Gap:** There is no per-task telemetry beyond session summaries. You cannot answer "what is our first-pass success rate?" or "which task classes cost the most?" without manually reviewing artifacts.

**Recommendation:** Add a `runs.jsonl` append-only file per project. Minimum fields per run:
- `run_id`, `project`, `task_id`, `task_class`
- `agents_invoked`, `start_time`, `end_time`
- `result`, `rework_required`
- `validator_result`, `qa_result`, `operator_score`
- `input_tokens`, `output_tokens`, `estimated_cost`

This feeds the weekly ops review and makes quality/cost trends visible over time.

**Source:** REVIEW-PROTOCOL research (GPT) §5.1, §7.1

### 3.2 Add an Incident Log

**Gap:** `PROTOCOL_IMPROVEMENTS.md` captures friction and ideas, but does not systematically capture false passes, escaped defects, or regressions with enough structure for trend analysis.

**Recommendation:** Add `incidents.jsonl` alongside the improvements log. Fields:
- `incident_id`, `date`, `project`, `task_id`, `severity`
- `failure_type`, `detected_by`, `escaped_stage`
- `root_cause_guess`, `protocol_change_candidate`

This is what turns anecdote ("that one time the validator missed it") into trend ("validators miss contract violations 40% of the time").

**Source:** REVIEW-PROTOCOL research (GPT) §7.2

### 3.3 Separate Review into Three Explicit Layers

**Gap:** The current system conflates task validation (did it satisfy the contract?), experiential review (does it feel right?), and pipeline review (is the system itself working well?). These are currently spread across Validator, QA, and the informal protocol review.

**Recommendation:** Make explicit:
- **Layer A — Task validation:** Validator. Already exists. No change needed.
- **Layer B — Experiential review:** QA Tester or operator review. Already partially exists. Formalize with a scorecard (clarity, confidence, surprise, friction, taste alignment) on a 1-5 scale with one-sentence evidence for outlier scores.
- **Layer C — Pipeline review:** The weekly/monthly review cadence from §2.4 above, using run records and incident logs.

These layers should never be collapsed into one generic "reviewer."

**Source:** REVIEW-PROTOCOL research (GPT) §4.3

### 3.4 Add a Structured Questioning Protocol (Discovery-Governance Flow)

**Gap:** INIT.md recommends Researcher/Designer/Architect prep sessions, and Phase 3.5 Feature Rationale Check exists, but there is no generalized question set that forces intent surface-area coverage before any execution.

**Recommendation:** Create a `discovery-governance` flow skill. It owns:
1. **Intent capture** — problem, for whom, why now
2. **Ambiguity exposure** — what is unknown, disputed, assumed
3. **Learning integration** — what changed after building/testing
4. **Dispatch readiness** — whether agents have enough signal

Minimum question categories before any feature execution:
- Product reality (what pain, for whom, what makes it valuable vs. disappointing)
- UX intent (what should it feel like, what friction is acceptable vs. unacceptable)
- Decision boundaries (what agents may infer vs. escalate)
- Quality attributes (speed vs. clarity vs. robustness — which matters most here)
- Evidence plan (what can only be learned after building, what is the cheapest artifact that teaches it)

**Source:** META-LAYER research (GPT) §6, META-LAYER research (Claude) §6.3

---

## 4. Low-Impact / Deferred (Validate With Evals First)

### 4.1 Specialist Agent Triggers as Opt-In Paths

The research recommends treating specialist agents (spec interviewer, code-aware planner, experiential QA) as trigger-based, not standing. The v1.9 constitution already moves in this direction with the skill trigger table. Specific triggers to consider adding:

- **Pre-implementation interviewer**: when user intent is ambiguous, goals under-specified, or UX quality is central
- **Experiential QA / user-advocate**: when behavior matters beyond static correctness

These should earn their place through eval improvement before becoming permanent paths.

### 4.2 Conformance Checks Against Frozen Spec

Automated or semi-automated validation that implementation matches frozen spec acceptance criteria. Can start as "agent compares output against spec checklist" and graduate to contract testing. Defer until the frozen/mutable spec split (§2.1) is in place.

### 4.3 LLM-as-Judge for Subjective Evaluation

Use a second agent to review output against spec quality guidelines for criteria that cannot be automated (code style, UX coherence, architectural pattern adherence). This is the evaluator-optimizer pattern applied at the meta-project level. Defer until there are enough run records to know where subjective failures cluster.

---

## 5. What NOT To Do

The research is equally clear about what to avoid:

1. **Do not add standing roles.** The meta-project layer is a control-plane flow, not a new org chart. Implement as a flow skill, not as new preambles.
2. **Do not over-engineer the outer loop.** If reviewing the spec takes longer than the execution cycle it governs, the process is too heavy.
3. **Do not treat "ask lots of questions" as unstructured conversation.** It must be a repeatable protocol with defined categories.
4. **Do not adopt spec-as-source (heavyweight SDD).** Spec-anchored is the right level — the spec informs and constrains but is not the sole generative artifact.
5. **Do not let unknowns stay implicit.** Convert them into tagged assumptions or explicit questions.
6. **Do not create large documents with no dispatch effect.** Every artifact must change routing, scope, or acceptance criteria — or it is analysis theater.

---

## 6. Suggested Implementation Order

1. **Frozen/mutable spec split** — update `templates/spec.md` and §2.5
2. **Enhanced dispatch readiness gate** — update §4.1 with intent checks
3. **Signal-driven review cadence** — update §10.1
4. **Evidence review packet artifact** — new template and trigger conditions
5. **Run records (`runs.jsonl`)** — new artifact, append-only per project
6. **Incident log (`incidents.jsonl`)** — new artifact alongside improvements log
7. **Discovery-governance flow skill** — new skill in `skills/`
8. **Experiential review scorecard** — extend QA verdict or add standalone template

Items 1-3 are configuration changes to existing artifacts. Items 4-8 are new artifacts or skills that should each be validated by running through the lightweight protocol eval set (§10.5) before becoming permanent.

---

## 7. Relationship to v1.9 Constitution

These recommendations reinforce and extend v1.9 principles:

| v1.9 Principle | Research Reinforcement |
|---|---|
| Skills, not standing roles | Confirmed. Meta-layer = flow skill, not new roles |
| Evals over docs | Confirmed. Run records + incident logs = eval infrastructure |
| Structured state over prose | Confirmed. JSONL run records > markdown session narratives |
| Progressive disclosure | Confirmed. Discovery questions loaded per-feature, not globally |
| Documentation earns its context window | Confirmed. Every new artifact must change dispatch decisions |

The research does not suggest a v2.0. It suggests filling specific gaps in v1.9's observability and intent-capture layers while keeping the same architecture.
