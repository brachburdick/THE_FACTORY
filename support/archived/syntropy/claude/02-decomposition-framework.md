# SYNTROPY Decomposition Framework

**Date:** 2026-03-22
**Version:** 0.1.0 (draft)
**Grounded in:** 01-research-findings.md

---

## Overview

This framework formalizes a problem decomposition process for automated multi-agent pipelines.
It draws from six disciplines (systems science, software engineering, AI planning, algorithm design,
project management, and mathematics) to create a principled, measurable decomposition engine.

The framework operates at three levels (after Marr):
1. **Computational:** What problem are we solving and why is decomposition the right approach?
2. **Algorithmic:** How do we decompose, what are the rules, what are the interfaces?
3. **Implementational:** Which models, tools, and infrastructure execute each piece?

These levels are kept separate. Changing the implementation (swap a model) should not require
re-decomposing. Changing the decomposition should not require re-stating the problem.

---

## Phase 0: Classify (Before Decomposing)

**Source:** Cynefin Framework, Wicked Problems

Before any decomposition, classify the task. Decomposition is a strategy for Clear and
Complicated domains. Applying it to Complex or Chaotic domains is a category error.

### Classification Protocol

```
INPUT:  Task description, acceptance criteria, domain context
OUTPUT: Domain classification + recommended posture
```

| Signal | Domain | Posture | Decomposition Strategy |
|---|---|---|---|
| Known solution pattern exists | Clear | Apply best practice | Template-based decomposition |
| Solution discoverable with expertise | Complicated | Analyze then execute | Expert-informed decomposition |
| Cause-effect only knowable in retrospect | Complex | Probe-sense-respond | Iterative probing, NOT pre-planning |
| No perceivable cause-effect | Chaotic | Stabilize first | No decomposition -- act to stabilize |

### Wickedness Check

If the task exhibits any of these, flag it as partially wicked and adjust:
- [ ] Cannot fully specify the problem before attempting a solution
- [ ] No clear stopping rule (when is "done"?)
- [ ] The problem is essentially unique (no prior pattern)
- [ ] Attempting a solution changes the problem itself

**Wicked tasks:** Use exploratory/conversational architecture. Do not pre-plan full decomposition.
Instead, decompose only the next 1-2 steps, execute, observe, then decompose the next steps.

### Output of Phase 0

```json
{
  "domain": "clear | complicated | complex | chaotic",
  "wickedness_flags": [],
  "decomposition_strategy": "template | expert-informed | iterative-probing | stabilize-first",
  "confidence": "HIGH | MEDIUM | LOW",
  "rationale": "..."
}
```

---

## Phase 1: Identify Decisions (What to Decompose Around)

**Source:** Parnas (Information Hiding), Baldwin & Clark (Option Value)

Do NOT decompose by processing steps. Decompose by DECISIONS.

### Decision Identification Protocol

```
INPUT:  Classified task + acceptance criteria
OUTPUT: Decision inventory
```

1. List every design decision the task requires.
2. For each decision, assess:
   - **Uncertainty (sigma):** How confident are we in the right choice? (HIGH/MEDIUM/LOW)
   - **Changeability:** How likely is this to change? (HIGH/MEDIUM/LOW)
   - **Visibility:** How much does this decision affect other parts? (HIGH/MEDIUM/LOW)
3. Each subtask should HIDE one decision (or a cluster of tightly-coupled decisions).

### Decision Clustering Rules

Decisions should be clustered into the same subtask when:
- They are tightly coupled (changing one requires changing the other)
- They share the same uncertainty level
- They operate on the same data

Decisions should be in SEPARATE subtasks when:
- They are independent (can be resolved without knowing each other's answer)
- They have different uncertainty levels (high-uncertainty decisions need more exploration)
- They will be varied independently in experiments (Baldwin & Clark option value)

### Output of Phase 1

```json
{
  "decisions": [
    {
      "id": "D-001",
      "description": "How to validate track metadata",
      "uncertainty": "MEDIUM",
      "changeability": "HIGH",
      "visibility": "LOW",
      "cluster": "validation"
    }
  ],
  "clusters": [
    {
      "id": "C-001",
      "name": "validation",
      "decisions": ["D-001", "D-003"],
      "rationale": "These decisions share data and coupling"
    }
  ]
}
```

---

## Phase 2: Define Interfaces (The Boundaries)

**Source:** Simon (Nearly Decomposable Systems), Category Theory (Compositionality),
Meyer (Contract-Based Design), Constantine (Coupling/Cohesion)

Interfaces are where decomposition succeeds or fails. Every interface must pass four tests.

### Interface Quality Tests

| Test | Question | Source | Failure Mode |
|---|---|---|---|
| Narrowness | Does only essential information cross this boundary? | Simon | Over-coupling, context bloat |
| Stability | Will this interface remain valid if internals of either side change? | Parnas | Brittle handoffs |
| Explicitness | Is everything that crosses documented (no hidden dependencies)? | Meyer | Silent failures |
| Sufficiency | Can the receiving side work with ONLY what's provided? | Category Theory | Implicit context leaks |

### The Compositionality Gate

For each interface between subtask A and subtask B:

```
Q: Does B's behavior depend ONLY on A's output,
   or also on HOW A produced that output?

If ONLY on output → Interface is compositional (PASS)
If also on HOW    → Interface leaks (FAIL -- redesign)
```

**Common LLM interface leaks:**
- B assumes A's output follows a specific formatting convention not in the schema
- B requires prompt-style context that A's output doesn't carry
- B needs to know which model A used to interpret results correctly
- B assumes A validated something that A's contract doesn't guarantee

### Contract Specification

Every interface gets a contract:

```json
{
  "interface_id": "I-001",
  "from_subtask": "ST-001",
  "to_subtask": "ST-002",
  "preconditions": [
    "Input must be valid JSON matching schema X",
    "All file paths must be absolute and exist on disk"
  ],
  "postconditions": [
    "Output contains exactly one result per input item",
    "No hallucinated entity names (verified against input set)"
  ],
  "invariants": [
    "Total item count is preserved across transformation"
  ],
  "data_schema": "{ ... JSON Schema ... }",
  "coupling_type": "data"
}
```

### Coupling Audit

After defining interfaces, audit coupling type for each:

| Coupling Type | Description | Action |
|---|---|---|
| Data coupling | Simple parameters only | GOOD -- keep |
| Stamp coupling | Shared composite structure, partial use | WARN -- trim to only needed fields |
| Control coupling | Flags controlling behavior | BAD -- make each subtask self-determining |
| Common coupling | Shared global state | BAD -- eliminate shared state |
| Content coupling | Direct internal modification | CRITICAL -- redesign immediately |

---

## Phase 3: Decompose (Create the Task Tree)

**Source:** HTN Planning, WBS (100% Rule), Functional Decomposition (No And/Or Test),
Divide & Conquer (Three Conditions)

### Decomposition Rules

**Rule 1: 100% Coverage (WBS)**
The subtasks must collectively cover 100% of the original task scope. No gaps. No overlaps.
Verify by mapping each acceptance criterion to at least one subtask.

**Rule 2: No And/Or (Functional Decomposition)**
If describing a subtask requires "and" or "or," it needs further decomposition.
- BAD: "Parse the config and validate the schema"
- GOOD: "Parse the config" + "Validate the parsed config against schema"

**Rule 3: Three Conditions Check (Divide & Conquer)**
For each decomposition, verify:
1. **Decomposability:** Can I split this into similar subproblems? (If not: don't decompose)
2. **Independence:** Can each be solved without knowing others' answers? (If not: sequential, not parallel)
3. **Mergeability:** Can I combine results cheaply? (If not: reconsider whether decomposition saves work)

**Rule 4: Right-Sizing (Empirical)**
Target the high-confidence zone:

| Metric | Target | Danger Zone |
|---|---|---|
| Files touched | 1 | 3+ |
| Lines changed | <15 | 55+ |
| Hunks | 1-2 | 6+ |
| Human-equivalent time | ~30 min | >2 hours |

If a subtask exceeds these bounds, decompose further.

**Rule 5: Subtasks as Interfaces, Not Prose (FunCoder)**
Express subtasks as function signatures, not natural language descriptions.
- BAD: "Validate the track metadata"
- GOOD: `validate_track_metadata(track: Track) -> ValidationResult`

### Task Tree Structure

```
Goal (acceptance criteria)
├── Milestone 1 (independently verifiable feature slice)
│   ├── Task 1.1 (single-file, <15 LOC, 1-2 hunks)
│   │   ├── Contract: pre/postconditions
│   │   └── Verification: test assertion
│   ├── Task 1.2
│   └── Task 1.3
├── Milestone 2 (can be parallelized with M1 if independent)
│   ├── Task 2.1
│   └── Task 2.2
└── Integration (merge milestone results)
    ├── Contract verification across milestone boundaries
    └── End-to-end acceptance test
```

### Ordering Constraints

Mark each pair of sibling subtasks:
- **Independent:** Can execute in parallel (different agents)
- **Sequential:** Must execute in order (output of A feeds B)
- **Conditional:** B only executes if A produces certain result

**Google/MIT finding:** Only use multiple agents for Independent subtasks. Sequential subtasks
degrade with multi-agent (-39% to -70%). Use single agent + verification for sequential work.

---

## Phase 4: Verify Each Subtask (External Signals)

**Source:** TDAD, DeepMind (LLMs Cannot Self-Correct), Anthropic research

### Verification Rules

**Rule 1: External, Not Internal**
LLMs cannot self-correct reasoning without external feedback (DeepMind, ICLR 2024).
Every subtask must have an external verification signal:
- Test execution (preferred)
- Type checking
- Schema validation
- Human review
- Tool output comparison

Self-reflection ("does this look right?") is NOT verification.

**Rule 2: Verify at Every Boundary**
Do not batch verification at the end. Verify after EACH subtask completes.
This prevents compounding errors (Lusser's Law).

```
Subtask 1 → Verify → Subtask 2 → Verify → ... → Integration → Verify
```

**Rule 3: Verify Against Contract, Not Intent**
Check whether postconditions are met, not whether the result "seems right."
Contract violations are bugs. Ambiguous results indicate insufficient contracts (fix the contract).

**Rule 4: Separate Context Verification**
The context that produced the work must NOT be the only context that verifies it.
Use a separate agent, subagent, or fresh context for verification.

### Verification Specification Per Subtask

```json
{
  "subtask_id": "ST-001",
  "verification_type": "test_execution | type_check | schema_validation | human_review",
  "assertions": [
    "Output matches schema X",
    "No new test failures in affected module",
    "Acceptance criterion AC-003 is satisfied"
  ],
  "external_signal": "npm test -- --filter=validation",
  "separate_context": true,
  "max_retries": 3,
  "on_failure": "replan_from_goal | escalate | retry_with_feedback"
}
```

---

## Phase 5: Re-plan on Failure (Adaptive Decomposition)

**Source:** BDI Architecture, TDAG (Dynamic Decomposition), Cynefin (probe-sense-respond)

### Re-planning Rules

**Rule 1: Maintain Goal Separately from Plan**
The goal (acceptance criteria) is immutable. The plan (decomposition) is mutable.
On failure, question the plan, not the goal.

**Rule 2: Re-decompose, Don't Just Retry**
If a subtask fails after max_retries:
1. Do NOT retry again
2. Ask: was the subtask correctly specified? (preconditions met?)
3. Ask: was the decomposition correct? (should this be split differently?)
4. Re-decompose from the nearest milestone level, incorporating failure evidence

**Rule 3: Dynamic Task Updates (TDAG)**
Each subtask's definition should incorporate results from prior subtasks:
```
t_i' = Update(t_i, results_1, results_2, ..., results_{i-1})
```
Plans are living documents, not specifications.

**Rule 4: Escalation Threshold**
After 3 failed re-plans at the same level, escalate to:
- Next level up (milestone → goal)
- Human operator
- Incident log

### Re-planning Decision Tree

```
Subtask fails
├── Postcondition violated?
│   ├── Yes: Was precondition met?
│   │   ├── Yes: Subtask implementation is wrong → retry with failure feedback
│   │   └── No: Upstream subtask produced bad output → re-verify upstream
│   └── No contract exists: → STOP, define contract first
├── Max retries exceeded?
│   ├── Yes: Re-decompose from milestone level
│   └── No: Retry with feedback from verification
└── Milestone-level re-plan failed 3x?
    └── Escalate to operator + log incident
```

---

## Phase 6: Measure and Iterate (The Eval Loop)

**Source:** Baldwin & Clark (option value requires experimentation), Anthropic (evals over docs)

### What to Measure

| Metric | Formula | Target |
|---|---|---|
| Per-subtask success rate | successes / attempts | >80% (high-confidence zone) |
| End-to-end success rate | product of subtask rates | >50% for full features |
| Rework rate | re-decompositions / total plans | <15% |
| Interface violation rate | contract failures / total handoffs | <5% |
| Decomposition overhead | (tokens for decomposition) / (tokens for execution) | <20% |
| Recombination cost | (integration time) / (total time) | <15% |

### The Experiment

The core experiment CRUCIBLE should run:

```
GIVEN:   A feature specification with defined acceptance criteria
VARY:    Decomposition granularity × Verification frequency × Agent configuration
MEASURE: Success rate × Token cost × Wall-clock time × Rework rate
FIND:    The configuration that maximizes success rate per token dollar
```

Specific variables to test:
1. **Granularity:** How small should subtasks be? (5 LOC? 15 LOC? 50 LOC?)
2. **Verification frequency:** Every subtask? Every milestone? Only at end?
3. **Contract strictness:** Full JSON Schema? Loose descriptions? No contracts?
4. **Re-planning aggressiveness:** Retry 1x? 3x? Re-decompose immediately?
5. **Agent configuration:** Single agent? Multi-agent for parallel milestones? Cascade?

---

## Appendix A: Quick Reference Checklist

### Before Decomposing
- [ ] Classified domain (Clear/Complicated/Complex/Chaotic)
- [ ] Checked for wickedness flags
- [ ] Confirmed decomposition is the right strategy (not probing or stabilizing)

### During Decomposition
- [ ] Decomposed by decisions, not processing steps
- [ ] Each subtask hides one uncertain decision
- [ ] 100% coverage verified (every AC maps to a subtask)
- [ ] No subtask description requires "and" or "or"
- [ ] All subtasks in the high-confidence size zone
- [ ] Three conditions checked (decomposable, independent, mergeable)
- [ ] Subtasks expressed as interfaces, not prose

### At Every Boundary
- [ ] Contract defined (preconditions, postconditions, invariants)
- [ ] Compositionality test passed (B depends only on A's output)
- [ ] Coupling audit passed (data coupling, no content/common coupling)
- [ ] External verification signal specified
- [ ] Separate-context verification assigned

### On Failure
- [ ] Goal maintained separately from plan
- [ ] Re-decomposition considered before retry
- [ ] Failure evidence incorporated into next attempt
- [ ] Escalation threshold enforced (3 retries → escalate)

---

## Appendix B: Theoretical Lineage

```
Simon 1962 (Nearly Decomposable Systems)
    └─> "Strong intra-group, weak inter-group interactions"
Parnas 1972 (Information Hiding)
    └─> "Decompose by decisions, not steps"
Constantine 1974 (Coupling & Cohesion)
    └─> Measurable decomposition quality axes
Marr 1982 (Three Levels)
    └─> Separate computational, algorithmic, implementational
Meyer 1992 (Design by Contract)
    └─> Pre/postconditions enable independence
Rao & Georgeff 1995 (BDI)
    └─> Goal ≠ Plan; re-plan on failure
Baldwin & Clark 2000 (Modularity)
    └─> Option value justifies decomposition cost
Snowden 2007 (Cynefin)
    └─> Classify before decomposing
Fong & Spivak 2019 (Compositionality)
    └─> B depends only on A's output, not on HOW

Empirical AI Research 2023-2026:
    Least-to-Most, DecomP, Tree of Thoughts, TDAD,
    CodePlan, FunCoder, TDAG, Plan-and-Act
    └─> Right-size tasks, external verification,
        dynamic re-planning, function signatures > prose
```
