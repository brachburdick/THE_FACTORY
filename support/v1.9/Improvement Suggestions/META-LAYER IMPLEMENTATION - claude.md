# Meta-Layer Implementation Recommendations for THE_FACTORY

**Date:** 2026-03-20
**Source:** Synthesis of META-LAYER research (Claude + GPT) against current THE_FACTORY documentation (v1.9.1)
**Purpose:** Actionable recommendations for adding a discovery-and-governance control plane to the agentic pipeline.

---

## Core Thesis

Both research documents converge on the same finding from independent angles:

> THE_FACTORY needs a lightweight discovery-and-governance control plane that sits above execution, preventing assumption drift through structured artifacts and review gates — not through more agent roles.

This aligns with v1.9's direction (roles → skills, structured state, progressive disclosure). The meta-layer is the next logical step.

---

## 1. Add a Formal Spec-Anchored Specification Artifact

**Both documents recommend this as the highest-impact change.**

Claude's research calls it a "Living Specification" with frozen/mutable sections. GPT calls it a "Project Definition Record." The mechanism is the same:

- **Frozen section** (human-authored, agent-readable only): original requirements, user stories, acceptance criteria, success metrics, non-goals, hard constraints
- **Mutable section** (agents can append, human reviews): discovered requirements, clarifications, architectural decisions, open questions — each entry timestamped, attributed, and traceable back to a frozen requirement

**What THE_FACTORY currently has:** `spec.md` and `plan.md` templates exist in the Protocol Enforcer's deliverables, but there is no frozen/mutable split, no traceability enforcement, and no formal rule about who can modify what section. `AGENT_BOOTSTRAP.md` carries some of this intent but is bootstrap-scoped, not lifecycle-scoped.

**Recommendation:** Create a `PROJECT_DEFINITION.md` template with explicit frozen/mutable sections. Add it to the Protocol Enforcer deliverables. The frozen section replaces scattered intent capture; the mutable section replaces ad-hoc `[DECISION NEEDED]` resolution notes that currently live in various artifacts.

**Recommended fields (frozen):**
- Problem statement
- Target users / stakeholders
- Jobs-to-be-done / key scenarios
- Desired outcomes
- Success metrics
- Non-goals
- Hard constraints
- Quality attributes (usability, performance, reliability, privacy/security, maintainability, cost/time)
- UX intent (emotional tone, visual intent, friction tolerance, trust requirements)
- Decision rights (Always / Ask First / Never boundaries)

**Recommended fields (mutable):**
- Discovered requirements (with traceability link to frozen requirement)
- Clarifications and interpretations
- Architectural decisions and rationale
- Open questions awaiting human resolution
- Known assumptions (each tagged: high / medium / low confidence)
- Known unknowns (each tagged with discovery path)

---

## 2. Add an Evidence Review Packet

**GPT's strongest unique contribution.** Claude's research describes this as part of the "Review Gate" but doesn't give it a standalone artifact shape.

This artifact captures what reality taught the project since the last review:

- What changed since last review
- Evidence observed (prototype feedback, build friction, user reaction, architecture surprises, testing/QA results)
- Assumptions invalidated
- Assumptions strengthened
- New questions surfaced
- Requirement / UX / architecture changes proposed
- Items intentionally deferred
- Next-slice recommendation
- **Dispatch readiness status**: `READY` / `READY WITH EXPLICIT ASSUMPTIONS` / `NOT READY`

**What THE_FACTORY currently has:** The Orchestrator State Snapshot (`orchestrator-state.md`) tracks execution state, but nothing captures *learning delta* between execution cycles. Insights evaporate between context windows.

**Recommendation:** Create an `EVIDENCE_REVIEW.md` template. Produced at defined checkpoints (not every task). Feeds back into the Project Definition's mutable section. This is the "outer loop" made concrete.

---

## 3. Formalize a Questioning Protocol

**Both documents validate the empirical observation that architect/designer questioning dramatically improves outcomes.**

Claude's research provides a 10-question minimum viable set. GPT organizes questions into 5 categories. Both agree: this is not "ask lots of questions informally" — it's a structured elicitation protocol that searches for missing concepts, competing priorities, and unstated constraints.

**What THE_FACTORY currently has:** `INIT.md` has a 6-question "What To Ask First" section, and Architect/Designer preambles mention asking questions. But there's no structured protocol, no minimum question set, and no gate that prevents execution dispatch until key questions are answered.

**Recommendation:** Add a `discovery-elicitation` flow skill (or fold into `feature-flow` Phase 0). Define minimum required answers before dispatch.

**Minimum viable question set:**

### Product Reality
- What exact user pain are we reducing?
- Who feels it most sharply?
- What would make this obviously valuable to them?
- What would make it disappointing even if technically "complete"?

### Scope & Boundaries
- What is explicitly out of scope?
- What adjacent features should be deferred?
- What may agents infer vs. what must agents escalate?

### Quality Attributes
- What matters more: speed, clarity, robustness, flexibility, polish, explainability, reversibility, or cost?
- Which failures are tolerable? Which are unacceptable?

### Data & Integration
- What are the core entities and their relationships?
- What external systems does this touch?
- What state must persist across sessions vs. ephemeral?

### Evidence Plan
- What can only be learned after a prototype exists?
- What is the cheapest artifact that will teach us that?
- What result would change the plan?

### Success Criteria
- How do we know this is working correctly?
- What does "done" look like?

**Questions to defer to later review gates:**
- Performance optimization targets (need baseline measurements)
- Edge case handling for discovered requirements
- Integration contract details for systems not yet explored
- UX refinements based on working prototype feedback

---

## 4. Add a Dispatch Readiness Gate (Intent-Completeness)

**GPT's "smallest version worth trying" centers on this.**

Execution cannot start unless these are all explicit:
- Target user
- Problem statement
- Desired outcome
- Non-goals
- Hard constraints
- Next-slice acceptance criteria

**What THE_FACTORY currently has:** The Orchestrator preamble has a "dispatch readiness checklist" focused on artifact completeness (handoff packet fields present), not intent completeness (does the operator's intent actually make it into the artifacts).

**Recommendation:** Extend the existing Orchestrator dispatch readiness checklist with intent-completeness checks. Small change — no new role or phase needed.

---

## 5. Define Event-Driven Review Cadence

**GPT is clearer here.** Trigger an Evidence Review when:

- After the first runnable prototype
- After the first end-to-end thin slice
- After operator discomfort with UX direction
- After an architectural surprise
- After a validator/QA failure pattern repeats
- After 2–5 execution tasks when work is moving fast but still uncertain
- Before committing to a large batch of implementation work

**What THE_FACTORY currently has:** Protocol Review is batch-processed from `PROTOCOL_IMPROVEMENTS.md`. There's no equivalent for project-level learning review.

**Recommendation:** Add review triggers to the `feature-flow` skill. These are lightweight checkpoints, not full re-planning sessions. If drift is detected, escalate to a full review.

---

## 6. Enhance Progress Ledger for Session Bridging

**Claude's research emphasizes this** (from Anthropic's long-running agent harness pattern). A standardized artifact that all agents read at cycle start and update at cycle end, preventing "where were we?" confusion across context windows.

**What THE_FACTORY currently has:** `orchestrator-state.md` + `.agent/tasks.jsonl` together cover most of this. The gap is that individual agents don't have a shared "what happened across all recent sessions" view — the Orchestrator reconstructs this, but other agents start cold.

**Recommendation:** Ensure the Orchestrator State Snapshot includes a "recent session digest" section that any agent can read for cross-session continuity. Small extension, not a new artifact.

---

## 7. Three-Tier Boundary Model (Always / Ask First / Never)

**From Addy Osmani's framework, cited by Claude's research.** A taxonomy for agent decision rights:

- **Always:** Non-negotiable constraints the agent follows without asking
- **Ask First:** Decision points requiring human judgment before proceeding
- **Never:** Hard prohibitions

**What THE_FACTORY currently has:** `COMMON_RULES.md` has some of this implicitly (ask-don't-assume rule, scope discipline). But it's not structured as a three-tier model, and project-specific boundaries aren't formalized this way.

**Recommendation:** Adopt this taxonomy in the Project Definition Record's frozen section. Each project includes explicit Always/Ask First/Never boundaries. Directly reduces late-discovered `[ASK OPERATOR]` incidents.

---

## What NOT To Take From the Research

Both documents warn against these:

1. **Don't go Spec-as-Source.** Stay at Spec-Anchored level. The spec informs and constrains but isn't the sole generative artifact. v1.9 already operates at this level.

2. **Don't add new standing roles.** Both documents explicitly say the meta-layer should be a flow skill / control-plane routine, not new personas. This is already v1.9's philosophy.

3. **Don't over-engineer the outer loop.** If reviewing takes longer than executing, the process is too heavy. Keep review gates as fast checkpoints.

4. **Don't create massive spec documents.** Context window pressure is real. The Project Definition Record should be concise and use progressive disclosure.

5. **Don't wait for perfect certainty.** Some questions are only answerable after building. The evidence review loop exists precisely for this — dispatch with explicit assumptions, then validate them.

---

## Anti-Patterns To Avoid

- Treating "ask lots of questions" as unstructured conversation rather than a repeatable elicitation protocol
- Adding new roles when a flow skill or artifact schema would do
- Waiting for perfect certainty before dispatching any execution work
- Rewriting the whole project brief after every learning event instead of tracking deltas
- Letting unknowns stay implicit instead of converting them into tagged assumptions or questions
- Running reviews that do not change routing, scope, or acceptance criteria

---

## Suggested Implementation Order

| Priority | Change | Effort | Impact |
|----------|--------|--------|--------|
| 1 | Project Definition Record template (frozen/mutable spec) | New template | Highest — directly prevents assumption drift |
| 2 | Dispatch readiness gate (intent-completeness check) | Extend existing Orchestrator checklist | High — blocks premature execution |
| 3 | Structured questioning protocol | New flow skill or feature-flow Phase 0 | High — front-loads spec quality |
| 4 | Evidence Review Packet template | New template | Medium — captures learning between cycles |
| 5 | Three-tier boundary model in Project Definition | Template structure | Medium — clarifies decision rights |
| 6 | Event-driven review triggers in feature-flow | Extend existing flow skill | Medium — makes the outer loop concrete |
| 7 | Progress ledger enhancement to Orchestrator State | Extend existing artifact | Low — mostly already solved |

---

## Minimum Viable Experiment

If testing the value of this layer with the smallest possible commitment, add only:

1. **Project Definition Record** — one durable file with frozen/mutable sections
2. **Evidence Review Packet** — one recurring review artifact
3. **Dispatch Readiness Gate** — execution cannot start unless user, problem, desired outcome, non-goals, hard constraints, and next-slice acceptance criteria are all explicit

That is enough to test the value of the layer without rebuilding the protocol around it.

**Measure:**
- Number of `[ASK OPERATOR]` incidents discovered late
- Number of mid-build requirement reversals
- Validator failures caused by missing intent
- Operator-reported UX dissatisfaction
- Spec revision frequency before vs. after the layer

---

## How This Maps to Existing Infrastructure

| Research Concept | THE_FACTORY Equivalent | Gap |
|---|---|---|
| Constitution | `CLAUDE.md` + `AGENT_BOOTSTRAP.md` | Mostly covered |
| Frozen/Mutable Spec | `spec.md` template | No frozen/mutable split, no traceability |
| Progress Ledger | `orchestrator-state.md` + `tasks.jsonl` | Mostly covered; needs recent-session digest |
| Review Gate | Protocol Review process | Exists for protocol; missing for project-level learning |
| Questioning Protocol | `INIT.md` questions + Architect preamble | Informal, no minimum gate |
| Three-Tier Boundaries | `COMMON_RULES.md` ask-don't-assume | Implicit, not structured per-project |
| Conformance Checks | Validator + QA Tester | Covers execution; doesn't cover intent-vs-spec conformance |
| Dispatch Readiness | Orchestrator checklist | Checks artifact completeness, not intent completeness |

---

## Sources

Full citations available in the source research documents:
- `support/v1.9/Improvement Research/META-LAYER research - claude`
- `support/v1.9/Improvement Research/META-LAYER research - gpt.md`

Key references: GitHub Spec Kit, Amazon Kiro, MetaGPT (ICLR 2024), MassGen, Anthropic "Building Effective Agents," Anthropic long-running agent harness, Addy Osmani spec framework, Google design review studies, MAST multi-agent failure analysis (2025).
