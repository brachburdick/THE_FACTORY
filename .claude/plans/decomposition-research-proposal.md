# Decomposition Research → THE_FACTORY Improvements

Source: `~/Downloads/deep-research-report Software Decomposition.md`
Created: 2026-03-26

---

## What the report says

A deep-research survey of software decomposition for multi-agent pipelines. Covers architecture styles (DDD, hexagonal, EDA, CQRS), multi-agent coordination patterns (contract-net, blackboard, reflection loops), and concrete pipeline design (artifact-centric orchestration, gated verification, three-loop control). Key thesis: treat agent pipelines as distributed systems with explicit contracts, deterministic gates, and end-to-end observability.

## What THE_FACTORY already does well

The report validates several existing choices:

| Report recommendation | THE_FACTORY equivalent | Status |
|---|---|---|
| Artifact-centric orchestration with gated verification | Hooks enforce gates (git-guard, fix-attempt-tracker); evals as deterministic validators | Done |
| Single orchestrator over peer-to-peer swarm | Single-agent with dynamic skills (validated by DeepMind/Anthropic data in v2.2 compass) | Done |
| Bounded contexts with explicit contracts | Section contracts (SYNTROPY.md, section-contract template) | Partial |
| Reflection via structured feedback | Run records + assess.py feedback loop | Done |
| Retry budgets to prevent thrash | Fix-attempt tracker (2 mutations without test = block) | Done |
| Handoff contracts between agents/phases | Handoff skill + JSON Schema envelope | Done |

## Actionable improvements (new or reinforcing existing tasks)

### 1. Formalize the artifact taxonomy

**From report:** Define a minimal artifact taxonomy agents must respect (specs, ADRs, contracts, diffs, tests, provenance, telemetry).

**Gap:** THE_FACTORY has artifacts scattered across formats — tasks.jsonl, runs.jsonl, incidents.jsonl, section contracts, specs, plans — but no single taxonomy doc that names them, defines their schema, and states which pipeline phase produces/consumes each.

**Action:** Create `templates/artifact-taxonomy.md` listing every artifact type, its schema reference, producer phase, consumer phase, and validation method. This becomes the "architecture description" the report emphasizes.

**Maps to existing task:** None. New task. Low effort, high clarity.

---

### 2. Strengthen section contracts as bounded contexts

**From report:** DDD bounded contexts + hexagonal ports/adapters + explicit context relationships. Contracts prevent "distributed monolith" anti-pattern. Strongest differentiator for agent-managed codebases.

**Gap:** Section contracts exist as a template but adoption is inconsistent across projects. The report's emphasis on "stable boundaries that agents can reliably decompose tasks against" reinforces that this is THE_FACTORY's most unique and underdeveloped asset.

**Action:** Already captured as v2.2 Priority 3. Reinforce with:
- Add `inputs` / `outputs` / `invariants` fields to contract template (port-like interface)
- Eval: every cross-section import goes through a declared port (hexagonal enforcement)
- Eval: no file orphans (every file owned by exactly one section)

**Maps to existing task:** tf-025 (blast radius scope check), v2.2 P3 (section contracts).

---

### 3. ADR template for architecture decisions

**From report:** ADR with Context → Decision → Consequences → Validation. "Memory with rationale" rather than implicit chat context.

**Gap:** THE_FACTORY has specs and plans but no ADR format. Decisions get buried in commit messages or plan files. When a future session asks "why did we choose X?", the rationale is lost.

**Action:** Add `templates/adr.md` using the report's template (context, constraints, decision, alternatives, consequences, validation tests/metrics). Reference ADRs from relevant tasks and run records.

**Maps to existing task:** None. New task. Small effort, compounds over time.

---

### 4. Three-loop control model as explicit framework

**From report:** Inner loop (edit→test→fix), middle loop (design→implement→integrate), outer loop (release→observe→learn). Each loop has different speed, scope, and gate strictness.

**Gap:** THE_FACTORY already implements all three loops but doesn't name them or set distinct policies per loop. The fix-attempt-tracker is an inner-loop gate. Section contract checks are middle-loop gates. Assess.py is an outer-loop feedback mechanism. Making this explicit would help tune gate strictness per loop.

**Action:** Add a "Three-Loop Model" section to CLAUDE.md that maps existing mechanisms to loops:
- **Inner:** fix-attempt-tracker, lint, unit tests (fast, automatic)
- **Middle:** section boundary checks, contract tests, plan approval (medium, semi-automatic)
- **Outer:** assess.py trends, DORA-like metrics, run record analysis (slow, operator-driven)

This is documentation, not new machinery — but it gives future sessions a framework for deciding where a new gate belongs.

**Maps to existing task:** tf-026 (compound error budget) fits as inner→middle escalation.

---

### 5. Pipeline SLOs and metrics

**From report:** Define pipeline SLOs — median PR cycle time, failure/rework rate, agent tool error rate. Use error budgets to auto-tighten/loosen gates.

**Gap:** THE_FACTORY tracks run records and assess.py can compute trends, but there are no declared SLOs. The v2.2 plan mentions dropping the token dashboard for Langfuse — this is the right time to define what metrics matter.

**Action:** Define 4-5 pipeline SLOs in a new `templates/pipeline-slos.md`:
- Session completion rate (runs that end with task marked complete)
- Rework rate (runs where the same file is edited in consecutive sessions)
- Escalation rate (AskUserQuestion calls per session)
- Test-gate failure rate (fix-attempt-tracker blocks per session)

These feed into v2.2 P5 (Langfuse) and tf-030 (trust calibration metrics).

**Maps to existing task:** tf-028 (interrupt budget), tf-030 (trust calibration metrics).

---

### 6. Agent contract template

**From report:** Each agent role should have a YAML contract specifying inputs, outputs, success_criteria (machine-checkable), and failure_policy (retry budget + escalation).

**Gap:** THE_FACTORY skills have YAML frontmatter (name, description) but don't declare their inputs/outputs/success_criteria. The report's point is sharp: "success_criteria must be machine-checkable, not narrative."

**Action:** Extend skill frontmatter schema with optional `inputs`, `outputs`, `success_criteria`, `failure_policy` fields. Start with the three flow skills (debug, feature, refactor) since they're the most structured. This aligns with v3 Phase 2 (skill format standardization).

**Maps to existing task:** v3 proposal items 2.1-2.3.

---

### 7. Spec drift prevention

**From report:** "Agents implement plausible but wrong changes because constraints were implicit or underspecified." Mitigate with spec templates, acceptance tests as executable specs, contract checks.

**Gap:** This is exactly the failure mode described in `feedback_memory_to_action_gap.md` — known bugs get dropped because agents don't cross-reference memory against fix lists. The report frames it as "spec drift" and the mitigation is the same: make constraints machine-checkable.

**Action:** Already partially addressed by tf-027 (pre-flight readiness checks). Strengthen by:
- Pre-flight must verify acceptance criteria exist and are testable before starting work
- Feature-flow skill should require at least one acceptance test per objective before implementation begins

**Maps to existing task:** tf-027 (pre-flight readiness).

---

## What to skip

The report covers topics that are either not applicable or already handled:

| Report topic | Why skip |
|---|---|
| Microservices / SOA / CQRS | THE_FACTORY manages single-agent pipelines, not distributed services |
| Multi-agent swarm coordination | Validated as inferior for this use case (v2.2 compass research) |
| SLSA / SBOM / supply-chain signing | Relevant for production deployments, not for an agent process pipeline |
| GitOps reconciliation controllers | Overkill for current scale; Git is already source of truth |
| Contract-net auction allocation | Interesting but requires multiple agents; file for future reference if multi-agent is revisited |
| OpenTelemetry distributed tracing | Deferred to Langfuse integration (v2.2 P5) |

---

## Priority ordering

Ranked by impact/effort ratio and alignment with existing v2.2 roadmap:

| # | Improvement | Effort | New task? | Blocked by |
|---|---|---|---|---|
| 1 | Three-loop model in CLAUDE.md | Small | No (docs) | Nothing |
| 2 | ADR template | Small | New | Nothing |
| 3 | Artifact taxonomy | Small | New | Nothing |
| 4 | Strengthen section contracts | Medium | Reinforces tf-025, v2.2 P3 | Nothing |
| 5 | Pipeline SLOs | Medium | Reinforces tf-028, tf-030 | Langfuse setup |
| 6 | Extend skill frontmatter | Medium | Reinforces v3 P2 | Nothing |
| 7 | Spec drift prevention | Small | Reinforces tf-027 | Nothing |

Items 1-3 are documentation/template work that can ship in one session. Items 4-7 require code or eval changes and align with existing backlog tasks.
