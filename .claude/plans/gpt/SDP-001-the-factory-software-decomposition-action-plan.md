# SDP-001: Software Decomposition Action Plan for THE_FACTORY

**Date:** 2026-03-26  
**Source:** `/Users/brach/Downloads/deep-research-report Software Decomposition.md`  
**Status:** Proposal - awaiting operator review

## Executive Summary

The research largely validates THE_FACTORY's current architecture:

- artifact-first coordination is the right base model
- section contracts are the right decomposition primitive
- deterministic hooks + evals are the right reliability mechanism
- a modular monolith/process repo is the right default before any heavier orchestration

The main gap is not "become a multi-agent platform." The gap is to make THE_FACTORY's existing operating model more explicit, more machine-checkable, and more observable.

The recommendation is:

1. Keep the single-agent + skills core as the default operating model.
2. Formalize architecture and artifact contracts so reasoning does not live only in chat context.
3. Make boundaries, gates, and evidence more machine-checkable.
4. Add a tighter control loop around metrics, risk, and integrity.
5. Run exactly one narrow manager-worker experiment where the repo already has the right shape: section review.

## What The Report Validates

### 1. THE_FACTORY already behaves like an artifact-centric state machine

The report's strongest recommendation is artifact-centric orchestration with deterministic gates. THE_FACTORY already has the pieces:

- `CLAUDE.md` as the hot runtime constitution
- `.agent/tasks.jsonl`, `.agent/runs.jsonl`, `.agent/incidents.jsonl` as the workflow state
- hooks as gatekeepers
- evals as machine-checkable validators
- specs, section contracts, and handoff artifacts as durable coordination objects

This means the right move is to strengthen the artifact model, not replace it.

### 2. Section contracts are THE_FACTORY's bounded-context mechanism

The report recommends DDD boundaries plus ports/adapters inside a modular monolith. THE_FACTORY's section model is already the closest repo-level equivalent:

- sections isolate review units
- contracts define owned paths, invariants, and verification
- boundary enforcement evals keep decomposition honest

The opportunity is to upgrade section contracts from "review guidance" into "published interface contracts."

### 3. Deterministic validation beats role-play

The research is clear that multi-agent role separation only works when handoffs are explicit and validators are deterministic. That matches THE_FACTORY's existing preference for hooks, evals, and evidence over prompt discipline.

### 4. Full multi-agent orchestration is not justified yet

The report surveys manager-worker, blackboard, contract-net, and reflection loops. For THE_FACTORY, the practical lesson is not "adopt all of these." It is:

- keep the default system simple
- use protocol-based coordination only where the artifact boundaries are already clean
- avoid swarm dynamics and open-ended chat topologies

## Gap Analysis

| Area | Current Strength | Gap To Close |
|---|---|---|
| Architecture description | Good local docs and conventions | No first-class ADR layer explaining core bets and boundary decisions |
| Artifact model | Strong artifact habit | Required artifacts and transitions are not defined in one canonical taxonomy |
| Flow gates | Good prose in flow skills | Gates are mostly narrative, not structured contracts |
| Boundary contracts | Strong section-review model | Cross-section inputs/outputs are not yet published as explicit compatibility contracts |
| State validation | Handoff schema exists | `tasks.jsonl`, `runs.jsonl`, `incidents.jsonl` are not fully schema-backed |
| Observability | Run records, assess.py, token dashboard | No unified DORA-lite / error-budget view for pipeline quality |
| Security/integrity | Git guard, dependency checks in flow | No proportional provenance / dependency-change guardrail layer |
| Orchestration experiments | Section review is promising | No controlled benchmark comparing siloed review against baseline review |

## Workstreams

## Workstream 1: Formalize The Architecture Description Layer

**Goal:** Move core design rationale out of implicit session memory and into durable artifacts.

**Deliverables**

- `templates/adr.md`
- `support/adrs/ADR-001-single-agent-with-skills.md`
- `support/adrs/ADR-002-file-based-artifact-blackboard.md`
- `support/adrs/ADR-003-sections-as-bounded-contexts.md`
- `support/architecture/artifact-model.md`

**Why this matters**

The report emphasizes that architecture descriptions, not just architecture, are what let multiple actors coordinate reliably. In THE_FACTORY, this reduces re-litigation of the same design bets and makes future protocol changes easier to reason about.

**Success signal**

- a new operator can explain the system without relying on prior chat history
- major pipeline changes reference an ADR rather than ad hoc rationale
- each flow can point to a canonical artifact model

## Workstream 2: Turn Flow Gates Into Structured Phase Contracts

**Goal:** Make flow progression machine-checkable instead of mostly prose-enforced.

**Deliverables**

- `templates/phase-contract.yaml`
- `templates/artifact-requirements.md`
- one structured contract per flow phase: intent, spec, plan, implement, test, verify
- an eval that checks every flow declares:
  - required inputs
  - required outputs
  - success criteria
  - failure policy
  - escalation trigger

**Why this matters**

The research repeatedly shows that agent pipelines get brittle when completion is narrative instead of machine-verifiable. THE_FACTORY already has hooks and evals; this makes them consume structured phase definitions rather than freeform prose.

**Tie-in to existing work**

This workstream should absorb or align with:

- `tf-027` pre-flight readiness
- `tf-026` compound error budget
- `tf-024` risk-aware autonomy controls

**Success signal**

- flow transitions can be validated automatically
- fewer sessions start implementation with underspecified intent
- fewer closures rely on "looks done" reasoning

## Workstream 3: Upgrade Section Contracts Into Published Interface Contracts

**Goal:** Make sections the canonical bounded contexts for both review and change isolation.

**Deliverables**

- section contract v2 fields:
  - owned paths
  - published inputs
  - published outputs
  - invariants
  - allowed dependencies
  - verification command
  - split/merge triggers
- `sections/BOUNDARIES.md` or equivalent registry for cross-section contracts
- evals that verify every cross-section dependency is declared and every shared type is owned somewhere explicit

**Why this matters**

Right now sections are strong review units. The report suggests going one step further: stable boundaries need explicit interface contracts, not just ownership and test commands. This is the most direct way to turn sectioning into a real decomposition system.

**Tie-in to existing work**

This workstream should align with:

- `skills/section-review/SKILL.md`
- current section boundary evals
- `tf-025` blast radius scope checks

**Success signal**

- cross-section changes become auditable
- out-of-scope edits are easier to detect before they spread
- section reviews catch more seam bugs and fewer duplicate internal findings

## Workstream 4: Expand The Control Loop With Metrics And Error Budgets

**Goal:** Close the outer loop the report recommends: release -> observe -> learn.

**Deliverables**

- JSON schemas for `tasks.jsonl`, `runs.jsonl`, and `incidents.jsonl`
- run record extensions for:
  - risk
  - section_changes
  - operator_interventions
  - agent_escalations
  - phase_step_count
  - rework_count
- DORA-lite reporting in `scripts/assess.py` or a sibling tool:
  - lead time
  - rework rate
  - fail/redo rate
  - intervention rate
  - task completion latency by risk level

**Why this matters**

The report is explicit that pipeline quality must be measured, not inferred. THE_FACTORY already captures useful raw state, but it still lacks one clear operator view of throughput, stability, and trust calibration.

**Tie-in to existing work**

This workstream should absorb or align with:

- `tf-028` interrupt budget tracking
- `tf-029` PR size guardrail
- `tf-030` trust calibration metrics

**Success signal**

- the operator can see whether autonomy is improving or just getting faster
- gate strictness can be tuned with evidence instead of anecdotes
- recurring failure patterns show up as measurable trends

## Workstream 5: Add Proportional Integrity And Supply-Chain Controls

**Goal:** Add the report's security/integrity recommendations without overbuilding.

**Deliverables**

- a dependency/build-script change detector for high-risk edits
- a policy check for risky file classes such as hooks, packaging, CI, and release scripts
- optional SBOM/provenance generation for release-like artifacts, benchmarks, or published templates

**Why this matters**

The report recommends SLSA-style provenance and policy-as-code gates. For THE_FACTORY, the right translation is proportional enforcement:

- strict on dependency and workflow mutations
- light on ordinary documentation or local feature edits
- no heavy platform migration unless a real need emerges

**Success signal**

- dependency or build-system changes are always visible and reviewable
- risky changes carry stronger evidence than normal code changes
- integrity controls do not slow normal sessions unnecessarily

## Workstream 6: Run One Controlled Manager-Worker Experiment

**Goal:** Learn from the report's multi-agent research without destabilizing the core operating model.

**Experiment scope**

Use the existing section-review workflow as the only sanctioned manager-worker topology:

1. parallel section review agents for Pass 1 where boundaries are already independent
2. one boundary-review agent for Pass 2
3. one integration-review agent for Pass 3

**Do not expand beyond this until measured**

- no general-purpose swarm mode
- no peer-to-peer chat topology
- no portfolio-wide multi-agent default

**Success metrics**

- bugs found per token
- unique boundary findings vs baseline review
- rework caused by false positives
- wall-clock speedup vs single-context review

## Suggested Rollout

### Phase 1: Tighten The Current System

Promote already-pending work that directly matches the report:

- `tf-027` pre-flight readiness
- `tf-024` risk classifier
- `tf-025` blast radius scope checks
- `tf-026` compound error budget
- `tf-030` trust calibration metrics

These are the fastest way to make the current pipeline more state-machine-like.

### Phase 2: Formalize The Artifact And Boundary Model

Add the missing decomposition primitives:

- ADR template + first three ADRs
- canonical artifact taxonomy
- schema-backed `.agent/` state
- section contract v2
- boundary registry + compatibility evals

This is the phase that turns the report's abstract findings into durable repo structure.

### Phase 3: Add Measurement And One Narrow Experiment

Once the artifacts are formalized:

- extend run records and assess tooling
- add DORA-lite reporting
- run the section-review manager-worker pilot
- compare it against baseline review sessions

### Phase 4: Add Integrity Controls Where The Data Justifies It

Only after the above is stable:

- dependency/build-script guardrails
- policy checks for high-risk changes
- optional SBOM/provenance generation for release-like outputs

## Suggested New Task Seeds

These are not yet in `.agent/tasks.jsonl`, but they are the cleanest new work items to create if this proposal is approved.

| Proposed ID | Task | Depends On |
|---|---|---|
| `tf-031` | ADR package + canonical artifact model | none |
| `tf-032` | Structured phase contract template + flow evals | `tf-031` |
| `tf-033` | Section contract v2 + boundary registry | `tf-031` |
| `tf-034` | Schemas + validation evals for `.agent/` state files | `tf-031` |
| `tf-035` | Dependency/build-script integrity guardrails | `tf-034` |
| `tf-036` | Section-review manager-worker pilot with benchmark metrics | `tf-033`, `tf-034` |

## Explicit Non-Goals

- Do not rewrite THE_FACTORY around microservices.
- Do not adopt a general multi-agent swarm architecture.
- Do not add CQRS/event sourcing to the pipeline repo itself.
- Do not replace file-based coordination with a workflow engine unless scale pain is measured first.
- Do not add security theater; add proportional controls tied to actual risk classes.

## Bottom Line

This report should push THE_FACTORY toward a more explicit and measurable version of what it already is, not toward a different architecture.

If approved, the best next move is:

1. execute the already-pending risk and control-loop tasks
2. formalize ADRs, artifact contracts, and section boundaries
3. measure one narrow manager-worker pattern before considering any broader orchestration shift
