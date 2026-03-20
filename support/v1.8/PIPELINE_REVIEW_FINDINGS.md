# Pipeline Review Findings — External Review (2026-03-19)

> **Source:** Independent pipeline review conducted by an external agent with no prior SCUE context.
> **Scope:** All 10 documents listed in `docs/agents/PIPELINE_REVIEW_PROMPT.md`.
> **Operator context:** Brach provided follow-up answers about intended workflow, pain points, and design philosophy. Those answers significantly informed the recommendations below.
>
> **How to use this document:**
> Load this file into a Protocol Review session alongside `PROTOCOL_REVIEW_PROMPT.md`,
> `OPERATOR_PROTOCOL.md`, and `PROTOCOL_IMPROVEMENTS.md`. The reviewer should treat
> Section 1 entries as pre-triaged improvement proposals (apply now) and Section 2 as
> ongoing vigilance guidance (inform future reviews).

---

## Section 1: Immediate Improvement Proposals

These are structured as `PROTOCOL_IMPROVEMENTS.md` entries, pre-triaged by priority.
The reviewer should validate, refine, and apply them through the standard review process.

---

### 1.1 Orchestrator Role Overload — Restore Thin Routing Intent

**Type:** FRICTION (bordering on GAP)
**Date:** 2026-03-19
**Priority:** P1

**Context:** The Orchestrator was designed as a thin routing/interface layer — "here's what's next, what do you want to do?" Over successive protocol revisions, technical judgment responsibilities have accumulated on it: FE state behavior checks, Designer invocation thresholds, QA dispatch decisions, interface contract discipline, misstep pattern detection. Each was individually justified, but the compound effect is that the Orchestrator now requires significant technical context (~60K tokens at initialization) and makes judgments about the *nature* of work, not just its *status*.

**Observation:** The operator spends more time managing agent infrastructure than building features. The Orchestrator's initialization cost is a major contributor — it reads preambles, state snapshots, session summaries, milestone trackers, bug logs, and task files before it can produce a handoff. Much of this context is needed only because the Orchestrator is making technical assessments that belong on the Architect.

**Improvement:** Redistribute technical judgment from Orchestrator to Architect. The Orchestrator keeps routing, status tracking, and operator interface duties. The Architect gains pre-dispatch quality checks.

**Specific changes:**

**Move FROM Orchestrator TO Architect:**

| Responsibility | Current owner | Proposed owner | Rationale |
|---|---|---|---|
| FE State Behavior Check (does a UI State Behavior artifact exist for this task?) | Orchestrator | Architect | The Architect produces plans and task breakdowns — it already knows which tasks involve state-dependent display. Flag during planning, not during dispatch. |
| Designer invocation decision (≥3 components / ≥4 states threshold) | Orchestrator | Architect | The Architect evaluates UI complexity when producing the plan. It should flag `[REQUIRES DESIGNER]` with reasoning, not leave the threshold check to the Orchestrator. |
| Interface contract discipline (should this handoff include an interface AC?) | Orchestrator | Architect | The Architect defines interfaces in specs. It knows which tasks touch contracts. Include the AC in the task breakdown, not as an Orchestrator afterthought. |
| QA dispatch recommendation | Orchestrator | Architect | The Architect knows which tasks involve bug fixes, FE-BE integration, or hardware interaction. Tag tasks as `[QA-REQUIRED]` in the task breakdown. The Orchestrator still dispatches, but the decision is pre-made. |

**Keep ON Orchestrator:**

- State snapshot read/write
- Priority recommendations (based on milestone status, not technical assessment)
- Handoff packet generation (assembling from Architect's task breakdowns + adding preamble refs and context file paths)
- Archival housekeeping flagging
- Surfacing `[DECISION NEEDED]` items from any source
- Unresolved operator concerns promotion
- Misstep pattern review (this is a *process* observation, not a technical judgment — keep it)

**Effect on Orchestrator context budget:** The Orchestrator no longer needs to read specs, architecture docs, or contracts to make dispatch decisions. Its initialization shrinks to: preamble + COMMON_RULES + state snapshot + active `tasks.md` files + most recent session summaries for active tasks. This should reduce context from ~60K to ~25-35K.

**Effect on Architect output:** The Architect's task breakdown (`templates/tasks.md`) gains two optional fields per task:
- `QA Required:` YES / NO (with reason)
- `State Behavior:` link to artifact, `[INLINE — simple]`, or `[REQUIRES DESIGNER]`

The Orchestrator trusts these tags when assembling handoff packets. It does not re-evaluate them.

---

### 1.2 Product Rationale Phase — Upstream Feature Challenge

**Type:** GAP
**Date:** 2026-03-19
**Priority:** P1

**Context:** The operator identified a missing step: nobody challenges *whether* a feature makes sense, *what* its purpose is, or *how* it fits with existing features before the Architect specs it. The current flow goes: operator describes feature → Architect specs it → Developer builds it. If the feature description is vague, over-scoped, or internally contradictory, the Architect faithfully specs the contradictions. The Designer defines how it looks, but not whether it should exist in its current shape.

The operator described needing an agent that asks:
- "What is the purpose of this page? How are these components used in the grand scheme?"
- "This is a bad idea for XYZ reason" / "It's not clear how this contributes to the end goal"
- "These are good ideas, but they should be organized differently across views"

**Observation:** This is a Product Advisor function. It sits between the operator (vision holder) and the Architect (technical planner). It does not require a new role — it is a mode of the Architect that is invoked before detailed spec work begins.

**Improvement:** Add a **Phase 3.5: Feature Rationale Check** to the workflow. This is an Architect session with a specific prompt mode: challenge scope, check coherence, refine the brief.

**Specific changes:**

**(A) Add to OPERATOR_PROTOCOL.md §3 (Workflow Protocol), after Phase 3 and before Phase 4:**

```markdown
### Phase 3.5: Feature Rationale Check (When Starting a New Feature or Major Revision)

Before detailed spec work (Phase 4), run the Architect in product-challenge mode:

1. Start a fresh conversation.
2. Load: `AGENT_BOOTSTRAP.md` → Architect preamble → relevant existing specs for adjacent features.
3. Provide: the operator's raw feature description.
4. Architect outputs a **Feature Rationale Brief**:
   - **Purpose statement** — one sentence: what does this feature enable the user to do?
   - **Coherence check** — how does this fit with existing features? Overlap or conflict?
   - **Scope challenge** — are all proposed components necessary for the stated purpose? What could be deferred without losing the core value?
   - **UX concerns** — information architecture problems (too much on one page, unclear navigation, conflicting patterns)
   - **Open questions** — things the operator should clarify before spec work begins
   - **Refined brief** — the cleaned-up feature description the Architect will spec against in Phase 4
5. **You review.** This is the step where scope gets narrowed and purpose gets sharpened. The Architect is expected to push back — not just execute.
6. If the feature rationale is approved, proceed to Phase 4 with the refined brief as input.

**When to skip:** Simple backend additions, bug fixes, or tasks where the scope is already well-defined and narrow. Use when the feature involves new pages, new navigation, significant user-facing changes, or when the operator's description is exploratory.
```

**(B) Add to Architect preamble — Feature Rationale Mode section:**

```markdown
## Feature Rationale Mode

When invoked for a Feature Rationale Check (Phase 3.5), your job changes. You are not speccing — you are challenging.

- **Be opinionated.** "I recommend cutting component X because it doesn't serve the stated purpose" is a valid output. The operator expects pushback.
- **Check coherence with existing features.** Read adjacent specs and existing UI. Flag overlap, redundancy, or conflicting interaction patterns.
- **Challenge scope.** For each proposed component, ask: is this necessary for the core purpose, or is it a nice-to-have that adds complexity? Propose a minimal viable version.
- **Flag ill-defined areas.** If the feature description is vague on any dimension, name it explicitly. "The description says 'show track info' but doesn't define which track info, in what layout, or what happens when no track is loaded."
- **Output: Feature Rationale Brief** using the structure defined in the workflow (Purpose, Coherence, Scope Challenge, UX Concerns, Open Questions, Refined Brief).

This mode produces a brief, not a spec. Keep it under 2 pages. The spec comes in Phase 4 after the brief is approved.
```

---

### 1.3 Orchestrator Context Budget

**Type:** FRICTION
**Date:** 2026-03-19
**Priority:** P2

**Context:** As the project grows, the Orchestrator will hit context limits. There is no triage strategy for what to read when the total exceeds budget.

**Observation:** Without a context budget, the Orchestrator either overloads (reads everything, hits token limits, gets confused) or under-loads (skips context, misses critical state).

**Improvement:** Add a context budget rule to the Orchestrator preamble.

**Specific change — add to ORCHESTRATOR.md:**

```markdown
## Context Budget

Target initialization: ≤30K tokens (leaving room for handoff generation and operator interaction).

If reading all recent session summaries would exceed this budget:
1. Always read: state snapshot, active `tasks.md` files.
2. Then: most recent session summary per active task.
3. Then: any session with BLOCKED or PARTIAL status.
4. Skip: COMPLETE sessions older than the most recent per task, archived sessions, non-active feature specs.

If you cannot determine project state from this subset, tell Brach what's missing rather than reading everything.
```

---

### 1.4 Compound State Behavior Guidance in UI State Behavior Template

**Type:** GAP
**Date:** 2026-03-19
**Priority:** P2

**Context:** The UI State Behavior template maps individual states to display but gives no guidance on state *combinations*. For a real-time system like SCUE, compound states (bridge reconnecting AND hardware absent) may require different display than either individual state suggests. Without guidance, Designers either ignore combinations (gaps) or enumerate all permutations (explosion).

**Improvement:** Add one paragraph of guidance to `templates/ui-state-behavior.md`.

**Specific change — add after the States Reference table:**

```markdown
## Compound States

Not all state combinations produce unique display behavior. Include a compound-state row ONLY when the combination requires display that differs from what the individual states would each produce independently. Do not enumerate all permutations — focus on combinations where the compound behavior is surprising or non-obvious.

Example: if "bridge disconnected" always shows a full-screen error regardless of hardware state, no compound rows are needed for bridge disconnected + hardware variations. But if "bridge reconnecting + hardware absent" should show a different message than "bridge reconnecting + hardware present," add those as explicit rows.
```

---

### 1.5 LEARNINGS.md Pruning Rule

**Type:** FRICTION
**Date:** 2026-03-19
**Priority:** P3

**Context:** LEARNINGS.md is append-only with no pruning mechanism. After 50+ sessions it will be too long for agents to read meaningfully.

**Improvement:** Add a pruning step to the protocol review cycle.

**Specific change — add to OPERATOR_PROTOCOL.md §10.3 (Protocol Review Session), after Step 5:**

```markdown
### Step 5a: LEARNINGS.md Maintenance

During each protocol review, also review the project's `LEARNINGS.md`:
1. Entries marked `(fixed)` and older than 3 months: archive or remove.
2. Entries superseded by skill file content: replace with a one-line pointer to the skill file.
3. Duplicate or near-duplicate entries: consolidate.

Target: LEARNINGS.md should stay under 200 lines. If it exceeds this, aggressive consolidation is needed.
```

---

### 1.6 Reviewer Role Preamble

**Type:** GAP
**Date:** 2026-03-19
**Priority:** P3

**Context:** Phase 7 (Feature Review) references a "Reviewer" role but says it "can be the Architect role with a review-focused prompt." This is the only workflow phase without a formal role definition. If the Architect is acting as Reviewer, its preamble doesn't cover review-specific behaviors.

**Improvement:** Create a minimal Reviewer preamble (can be a mode of the Architect, like the Feature Rationale mode).

**Specific change — add to Architect preamble:**

```markdown
## Feature Review Mode (Phase 7)

When invoked for a Feature Review, evaluate the completed implementation against the spec:

1. **Spec conformance** — Does every spec requirement have a corresponding implementation? Are there implemented behaviors not covered by the spec?
2. **Cross-layer contract integrity** — Do all layer boundaries match `docs/CONTRACTS.md`? Are there undocumented interface changes?
3. **Unstated assumptions** — What did the Developer assume that wasn't in the spec? Are those assumptions safe?
4. **Test coverage** — Are the acceptance criteria from all task handoffs actually tested? Are there obvious edge cases without tests?
5. **Coherence with adjacent features** — Does this feature interact cleanly with existing features, or are there integration gaps?

Output: Feature Review Report. Flag issues as CRITICAL (must fix before milestone close) or ADVISORY (improve if time permits).
```

---

### 1.7 Orchestrator Handoff Validation Against Session Outputs

**Type:** GAP
**Date:** 2026-03-19
**Priority:** P2

**Context:** The Orchestrator reads session summaries and produces handoff packets, but there is no check that the handoff accurately reflects the preceding session's outputs. A Developer could report `[INTERFACE IMPACT]` or `[BLOCKED]` in their session summary, and if the Orchestrator's next handoff doesn't incorporate it, it's silently dropped.

**Improvement:** Add a cross-reference check to the Orchestrator's handoff generation process.

**Specific change — add to ORCHESTRATOR.md under Handoff Packet Generation:**

```markdown
## Pre-Dispatch Cross-Reference

Before dispatching any handoff packet, verify against the most recent session summary for the relevant task/feature:

1. Every `[INTERFACE IMPACT]` entry is either addressed in this handoff's scope or explicitly deferred with reasoning in the state snapshot.
2. Every `[BLOCKED]` item is either resolved or carried forward as a blocker in this handoff's Dependencies section.
3. Every `[SCOPE VIOLATION]` is either incorporated into the new scope or routed to a separate task.

If any item is unaccounted for, do not dispatch. Surface it to Brach first.
```

---

## Section 2: Ongoing Vigilance — Guidance for Future Reviews

These are not actionable changes yet. They are patterns to watch for and address when they produce real friction. The reviewer should keep these in mind during future protocol review sessions.

---

### 2.1 Watch: Orchestrator State Snapshot History

The state snapshot is overwritten each session. If the Orchestrator mischaracterizes state, the previous snapshot is gone. This hasn't caused a failure yet, but when it does, the fix is: keep the previous snapshot as `orchestrator-state-prev.md` (just one generation of history, not a full log). Don't implement until a real overwrite error occurs.

### 2.2 Watch: Session Summary Learnings Duplication

Session summaries have a `## Learnings` field AND agents must append to `LEARNINGS.md`. This is intentional duplication (session summary is the record, LEARNINGS.md is the knowledge base), but watch for drift where one gets updated and the other doesn't. If drift becomes a pattern, consider making the session summary's Learnings field a pointer ("See LEARNINGS.md entries added this session") rather than duplicating content.

### 2.3 Watch: Parallel Task Contract Conflicts

The operator runs agents in parallel when tasks are independent. This works well now, but as the project grows, two parallel Developer sessions may both need to modify `docs/CONTRACTS.md` or shared type files. When this first causes a conflict, the fix is: the Orchestrator notes in each parallel handoff which interfaces are "frozen" for that task and which may be modified by a concurrent task.

### 2.4 Watch: Cross-Feature Knowledge Surfacing

Session summaries live in `specs/feat-[name]/sessions/`. Patterns learned in one feature aren't automatically surfaced when working on another feature. `LEARNINGS.md` and skill files partially address this, but watch for cases where an agent re-discovers something already known from a different feature's sessions. If this recurs, consider a periodic "knowledge consolidation" step where LEARNINGS.md entries are reviewed for skill file promotion.

### 2.5 Watch: Product Advisor Scope Creep

The Feature Rationale Check (proposed in §1.2 above) gives the Architect permission to push back on scope. Watch for two failure modes:
- **Under-challenge:** The Architect rubber-stamps feature descriptions without meaningful pushback. Fix: add examples of good pushback to the preamble.
- **Over-challenge:** The Architect blocks features with excessive skepticism. Fix: clarify that the Architect recommends, the operator decides. The Architect cannot veto.

### 2.6 Watch: Researcher Proactive Deployment

Currently, research only happens reactively (after an agent hits the 2-attempt rule). As the project takes on more ambitious features, consider whether the Architect should be able to proactively request research during Phase 3.5 or Phase 4 — not just after getting stuck. The mechanism exists (Research Request template), but the workflow doesn't encourage proactive use. Don't change this until a feature is delayed because research was triggered too late.

### 2.7 Future Consideration: Intent Verification for Developers

A lightweight addition to the Developer preamble: "After reading the handoff, state in one sentence what you believe the operator's intent is. If you cannot state this clearly, ask." This surfaces spec gaps early. Defer until a Developer implements something that passes all acceptance criteria but misses the operator's intent.

---

## Section 3: Items Already in PROTOCOL_IMPROVEMENTS.md — Reviewer Cross-Reference

The root `PROTOCOL_IMPROVEMENTS.md` currently has three pending entries. Here is how they relate to this review's findings:

### Pending: [GAP] Domain expert review
**Relation:** Partially addressed by §1.2 (Feature Rationale Check) and §1.6 (Feature Review Mode). The Feature Rationale Check brings domain challenge upstream. The Feature Review Mode adds spec conformance checking downstream. However, neither fully replaces a domain expert who evaluates whether the *spec itself* is technically sound from a DJ/lighting domain perspective. That remains a skill file concern — load domain skill files into the Architect during Phase 3.5 and Phase 7. Consider this entry partially resolved; the remaining gap is narrow enough to defer.

### Pending: [IDEA] User Advocate role
**Relation:** The Feature Rationale Check (§1.2) absorbs some of this by challenging whether features serve user needs. But the User Advocate as described (walking through the feature as the target user) is a distinct evaluation mode not covered by any current or proposed role. Defer per the IDEA deferral rule — no supporting BUG or GAP yet. Revisit when a feature ships that users find unusable despite passing all quality gates.

### Pending: [FRICTION] Guided question scripts
**Relation:** Not addressed by this review. This is a valid friction point but lower priority than the structural changes above. Keep as pending.
