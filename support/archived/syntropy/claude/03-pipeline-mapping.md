# Pipeline Mapping: Decomposition Framework onto THE_FACTORY

**Date:** 2026-03-22
**Purpose:** Map the formalized decomposition framework (02-decomposition-framework.md) onto the
existing THE_FACTORY pipeline infrastructure, identifying what already exists, what needs to change,
and what needs to be built.

---

## Current State Summary

THE_FACTORY v1.9.2 has:
- A constitution (CLAUDE.md) with trigger table, flow routing, session protocol
- Three flow skills (debug, feature, refactor) with phase gates
- A handoff envelope schema (v1.1.0) for domain boundary crossings
- Templates for specs, plans, handoff packets, orchestrator state
- JSONL task tracker, run ledger, incident log
- Eval suite organized by type
- CRUCIBLE as an agent evaluation harness (E2B sandbox, Langfuse, loop detection)

---

## Mapping Table

### Framework Phase 0: Classify → Existing Infrastructure

| Framework Element | Exists? | Current Location | Gap |
|---|---|---|---|
| Domain classification (Cynefin) | Partial | CLAUDE.md flow routing table classifies by task TYPE (debug/feature/refactor) | No classification by DOMAIN COMPLEXITY. Flow routing answers "what kind of work" but not "how knowable is the solution." |
| Wickedness check | No | -- | No mechanism to flag tasks where the problem definition is unstable. |
| Decomposition strategy selection | No | -- | The constitution assumes decomposition is always appropriate. No probe-sense-respond path for Complex tasks. |

**What to build:**
- Add a `complexity_domain` field to the task tracker schema: `clear | complicated | complex | chaotic`
- Add a `wickedness_flags` array field
- Add an `investigation` flow skill (already noted as future in CLAUDE.md) that implements probe-sense-respond for Complex-domain tasks
- Modify Phase 0 of feature-flow to include domain classification BEFORE spec writing

**Mapping onto feature-flow Phase 0 (Intent Check):**
```
CURRENT Phase 0: Confirm intent capture → Gate: dispatch readiness
PROPOSED Phase 0:
  Step 0a: Classify domain complexity (Clear/Complicated/Complex/Chaotic)
  Step 0b: Check wickedness flags
  Step 0c: IF Complex → route to investigation flow (probe first)
  Step 0d: IF Clear/Complicated → proceed with intent capture
  Gate: domain classified + dispatch readiness met
```

---

### Framework Phase 1: Identify Decisions → Existing Infrastructure

| Framework Element | Exists? | Current Location | Gap |
|---|---|---|---|
| Decision inventory | No | -- | Current pipeline decomposes by STEPS ("implementation steps in dependency order" -- feature-flow Phase 2), not by DECISIONS. This is precisely what Parnas warns against. |
| Uncertainty assessment per decision | No | -- | No formal uncertainty tracking. `assumptionsInForce` in handoff envelope has confidence levels but these are for assumptions, not design decisions. |
| Decision clustering | No | -- | No mechanism to group related decisions. |

**What to build:**
- Extend the spec template (`templates/spec.md`) with a "Decision Inventory" section:
  ```markdown
  ### Decision Inventory
  | ID | Decision | Uncertainty | Changeability | Visibility | Cluster |
  |---|---|---|---|---|---|
  | D-001 | How to validate metadata | MEDIUM | HIGH | LOW | validation |
  ```
- Extend the plan template (`templates/plan.md`) to decompose by decision clusters, not by processing steps
- The "Interfaces and Contracts" section of plan.md is the right place for this, but currently it's a fill-in-the-blank. It needs to become a structured contract specification.

**Mapping onto feature-flow Phase 1 (Spec):**
```
CURRENT Phase 1: Write spec with behavior, inputs, outputs, edge cases
PROPOSED Phase 1:
  Step 1a: Write spec (current behavior)
  Step 1b: Identify all design decisions the task requires (NEW)
  Step 1c: Assess uncertainty/changeability/visibility per decision (NEW)
  Step 1d: Cluster tightly-coupled decisions (NEW)
  Gate: spec exists + decision inventory complete + all HIGH-uncertainty
         decisions have explicit handling strategy
```

---

### Framework Phase 2: Define Interfaces → Existing Infrastructure

| Framework Element | Exists? | Current Location | Gap |
|---|---|---|---|
| Interface contracts (pre/postconditions) | Partial | Handoff envelope has `verificationProcedure`, `evidenceRequired`, `assumptionsInForce` | These exist for HANDOFFS (cross-domain boundaries) but not for WITHIN-TASK interfaces between subtasks. The handoff envelope is too heavy for subtask boundaries. |
| Compositionality test | No | -- | No formal check that subtask B depends only on A's output. |
| Coupling audit | No | -- | No measurement of coupling type between subtasks. |
| Data schemas at boundaries | Partial | SCUE has layer boundary contracts ("NEVER cross layer boundaries without defined contracts") | Project-specific, not portfolio-level. |

**What to build:**
- A lightweight subtask contract schema (simpler than handoff-envelope.json):
  ```json
  {
    "subtask_id": "string",
    "preconditions": ["string"],
    "postconditions": ["string"],
    "input_schema": { "JSON Schema" },
    "output_schema": { "JSON Schema" },
    "verification_command": "string",
    "coupling_type": "data | stamp | control"
  }
  ```
  Store at `.agent/schemas/subtask-contract.json`
- Add compositionality check to the plan template as a required section
- The existing `templates/plan.md` "Interfaces and Contracts" section should reference this schema

**Mapping onto feature-flow Phase 2 (Plan):**
```
CURRENT Phase 2: Identify files, list steps in dependency order, estimate scope
PROPOSED Phase 2:
  Step 2a: For each decision cluster, define the subtask boundary
  Step 2b: For each boundary, specify contract (pre/post/invariant)
  Step 2c: Run compositionality test on each interface
  Step 2d: Audit coupling type (flag anything above data coupling)
  Step 2e: Right-size check: is each subtask in the high-confidence zone?
           (1 file, <15 LOC, 1-2 hunks)
  Step 2f: Mark ordering constraints (independent/sequential/conditional)
  Gate: all interfaces pass compositionality test + all subtasks right-sized
```

---

### Framework Phase 3: Decompose → Existing Infrastructure

| Framework Element | Exists? | Current Location | Gap |
|---|---|---|---|
| Task tree (goal → milestone → task) | Partial | `.agent/tasks.jsonl` tracks tasks flat. No formal milestone grouping. PDR → spec → plan → tasks is the conceptual hierarchy but it's not structurally enforced. | No milestone layer between goal and task. Tasks are flat in the tracker. |
| 100% coverage verification | No | -- | No check that subtasks cover all acceptance criteria. |
| Right-sizing rules | No | -- | No enforceable size limits on tasks. |
| Subtasks as function signatures | No | -- | Subtasks are described in prose (plan template), not as interfaces. |

**What to build:**
- Add `milestone_id` field to task tracker schema (optional, groups tasks under milestones)
- Add `parent_task` field for hierarchical decomposition
- Add `acceptance_criteria_refs` array field (which ACs does this subtask satisfy?)
- Add a coverage verification step: every AC must map to at least one subtask
- Add size-limit checks to the plan phase (measurable: file count, estimated LOC)
- The plan template should express subtasks as interface definitions, not prose:
  ```markdown
  ### Subtask: ST-001
  **Interface:** `validate_config(raw: RawConfig) -> ValidatedConfig | ValidationError`
  **Hides decision:** D-002 (validation strategy)
  **Size estimate:** 1 file, ~12 LOC
  **Covers AC:** AC-003, AC-004
  **Depends on:** ST-000 (sequential)
  **Contract:** see subtask-contract ST-001
  ```

**Mapping onto feature-flow Phase 3 (Implement):**
```
CURRENT Phase 3: Follow plan step by step, run tests after each step,
                 stop if plan is wrong
PROPOSED Phase 3:
  Step 3a: FOR EACH subtask in dependency order:
    3a.i:   Verify preconditions are met (upstream contracts satisfied)
    3a.ii:  Execute subtask (single file, <15 LOC target)
    3a.iii: Run external verification (test, typecheck, schema validation)
    3a.iv:  Verify postconditions are met
    3a.v:   IF postcondition violated AND retries < 3 → retry with feedback
    3a.vi:  IF retries exhausted → trigger re-plan (Phase 5)
  Step 3b: After all subtasks in a milestone complete:
    3b.i:   Run milestone-level integration test
    3b.ii:  Verify cross-subtask contracts
  Gate: all subtasks verified + milestone integration passes
```

---

### Framework Phase 4: Verify → Existing Infrastructure

| Framework Element | Exists? | Current Location | Gap |
|---|---|---|---|
| External verification | Yes | All three flow skills require separate-context verification in Phase 5 | Exists but only at the END (Phase 5). Framework calls for verification at EVERY subtask boundary. |
| Test execution | Yes | Feature-flow Phase 4 (Test), Debug-flow Phase 1 (Reproduce) | Good coverage for feature-level and bug-level. Missing at subtask granularity. |
| Separate-context verification | Yes | All flows mandate this in Phase 5 | Well-designed. Keep as-is and extend to milestone boundaries. |
| Schema validation | Partial | Handoff envelope is validated. No subtask contract validation. | Need subtask contract validation at each boundary. |
| Max retries + escalation | Yes | "Do NOT silently retry more than 3 times" in all flows | Good. Maps directly to framework's escalation threshold. |

**What to change:**
- Move verification from end-only (Phase 5) to every-boundary
- Keep the existing Phase 5 separate-context verification as the FINAL gate
- Add subtask-level verification as a new concern within Phase 3 (Implement)
- The existing "run relevant existing tests after each significant step" in feature-flow Phase 3 is the seed of this -- formalize it with contract verification

**Verification hierarchy:**
```
Subtask boundary   → Contract check (pre/postconditions) + test execution
Milestone boundary → Integration test + cross-contract verification
Feature boundary   → Separate-context verification (existing Phase 5)
```

---

### Framework Phase 5: Re-plan on Failure → Existing Infrastructure

| Framework Element | Exists? | Current Location | Gap |
|---|---|---|---|
| Re-planning mechanism | Partial | Feature-flow Phase 3: "If you discover the plan is wrong, STOP. Update the plan first." | The instruction exists but there's no structured re-planning protocol. It's "update the plan" without guidance on HOW. |
| Goal vs plan separation | Yes | Frozen Intent (immutable) vs Mutable Specification in spec template | Excellent. This IS the goal/plan separation. Frozen Intent = goal, Mutable Spec = plan. |
| Failure evidence incorporation | Partial | Incident log captures failures. Debug-flow searches evals for known patterns. | Incidents are logged but not fed back into decomposition decisions. |
| Dynamic task updates (TDAG) | No | -- | Plans are written once and followed. No formal mechanism to update subtask definitions based on prior results. |

**What to build:**
- A re-planning protocol that specifies:
  1. Which level to re-plan from (subtask → milestone → goal)
  2. How to incorporate failure evidence into the new decomposition
  3. When to escalate vs when to re-decompose
- Add `replan_count` and `replan_reason` fields to task tracker
- The existing `replanTriggers` field in handoff-envelope.json is the right concept -- extend it to subtask contracts

**Mapping onto existing flows:**
```
CURRENT: "STOP. Update the plan first, then resume." (feature-flow Phase 3)
PROPOSED re-plan protocol:
  1. Subtask fails after 3 retries
  2. Log failure evidence (what failed, why, what was tried)
  3. Check: was this a precondition violation? (upstream problem)
     → Re-verify upstream subtask
  4. Check: was this a decomposition error? (subtask too large/wrong boundary)
     → Re-decompose from milestone level with failure evidence
  5. Check: was this a specification error? (wrong acceptance criteria)
     → Escalate to operator (Frozen Intent is immutable without approval)
  6. After re-decomposition: update tasks.jsonl with new subtasks
  7. Resume execution from the re-planned point
```

---

### Framework Phase 6: Measure and Iterate → Existing Infrastructure

| Framework Element | Exists? | Current Location | Gap |
|---|---|---|---|
| Run metrics | Yes | `.agent/runs.jsonl` tracks result, tokens, tool calls, latency, cost | Good coverage. Missing decomposition-specific metrics. |
| Incident tracking | Yes | `.agent/incidents.jsonl` with root-cause classification | Good. Already has SPECIFICATION, HANDOFF, VERIFICATION categories. |
| Eval suite | Yes | `.agent/evals/` with conventions, flows, handoffs, skills families | Well-structured. Needs decomposition-specific evals. |
| CRUCIBLE as eval harness | Yes | E2B sandbox, Langfuse tracing, loop detection, configurable kill switches | Ready for decomposition experiments. Needs task definitions. |

**What to add:**
- Decomposition-specific metrics to runs.jsonl:
  ```json
  {
    "decomposition_depth": 3,
    "subtask_count": 12,
    "subtask_success_rate": 0.83,
    "contract_violations": 1,
    "replan_count": 1,
    "interface_overhead_tokens": 4500,
    "verification_overhead_tokens": 2200
  }
  ```
- Decomposition-specific evals:
  - `evals/decomposition/coverage-100-percent.md` — verify 100% rule
  - `evals/decomposition/right-sizing.md` — verify subtask size limits
  - `evals/decomposition/compositionality.md` — verify no interface leaks
  - `evals/decomposition/contract-completeness.md` — verify all interfaces have contracts
- CRUCIBLE experiment definitions for the core experiment:
  ```
  VARY: granularity × verification_frequency × contract_strictness × replan_aggressiveness
  MEASURE: success_rate × token_cost × wall_clock × rework_rate
  ```

---

## Summary: What Exists, What Changes, What's New

### Keep As-Is (Already Aligned)

| Component | Why It's Good |
|---|---|
| Frozen Intent / Mutable Spec separation | IS the goal/plan separation (BDI principle) |
| Separate-context verification (Phase 5) | Matches external verification requirement |
| 3-retry escalation limit | Matches framework escalation threshold |
| Incident log with root-cause classification | Matches failure evidence requirement |
| Handoff envelope with replanTriggers | Correct concept for cross-boundary failure handling |
| CRUCIBLE sandbox + Langfuse | Ready infrastructure for decomposition experiments |
| "Evals over docs" principle | Matches framework's measurement emphasis |
| Flow skill phase gates | Natural verification boundaries |

### Extend (Good Foundation, Needs More)

| Component | Current | Extension |
|---|---|---|
| Feature-flow Phase 0 | Intent check | Add domain classification (Cynefin) |
| Feature-flow Phase 2 | Steps in dependency order | Decision-based decomposition with contracts |
| Feature-flow Phase 3 | "Run tests after each step" | Formalized contract verification at each subtask |
| Task tracker schema | Flat task list | Add milestone_id, parent_task, acceptance_criteria_refs |
| Spec template | Behavior/inputs/outputs/edges | Add Decision Inventory section |
| Plan template | Steps + interfaces (prose) | Subtasks as function signatures with contracts |
| Runs.jsonl | Outcome + efficiency metrics | Add decomposition-specific metrics |
| Eval suite | Conventions, flows, handoffs | Add decomposition family |

### Build New

| Component | Purpose | Priority |
|---|---|---|
| Subtask contract schema | Lightweight pre/post/invariant at subtask boundaries | HIGH |
| Domain classification protocol | Cynefin classification before decomposition | HIGH |
| Re-planning protocol | Structured re-decomposition on failure | HIGH |
| Investigation flow skill | Probe-sense-respond for Complex-domain tasks | MEDIUM |
| Coverage verification step | Ensures 100% AC coverage | MEDIUM |
| Compositionality checker | Validates interface independence | MEDIUM |
| Decomposition eval family | Automated checks for decomposition quality | MEDIUM |
| CRUCIBLE experiment definitions | The core decomposition experiment | MEDIUM |
| Right-sizing enforcer | Checks subtask size limits | LOW (can be manual initially) |
| Coupling auditor | Measures coupling type at boundaries | LOW (can be manual initially) |

---

## Implementation Sequence

Phase 1 (Foundation):
1. Add domain classification to feature-flow Phase 0
2. Create subtask contract schema
3. Add Decision Inventory to spec template
4. Extend plan template with function-signature subtasks

Phase 2 (Verification):
5. Add contract verification to feature-flow Phase 3
6. Create re-planning protocol
7. Add decomposition metrics to runs.jsonl
8. Create decomposition eval family

Phase 3 (Experimentation):
9. Build investigation flow skill
10. Define CRUCIBLE decomposition experiments
11. Run experiments, measure, iterate

Phase 4 (Automation):
12. Automate coverage verification
13. Automate compositionality checking
14. Automate right-sizing enforcement
15. Automate coupling auditing
