# SYNTROPY: Problem Statement

**Date:** 2026-03-22
**Version:** 0.1.0 (draft)

---

## The Problem

Automated multi-agent pipelines fail at real-world software engineering tasks. Frontier models
solve curated single-file bugs at ~81% but drop to ~18-23% on multi-file engineering and ~11%
on end-to-end feature implementation. The root cause is compounding failure across sequential
steps (Lusser's Law), amplified by semantic error propagation where plausible-looking but
wrong intermediate results cascade through the pipeline undetected.

The dominant mitigation strategy is problem decomposition: break complex tasks into smaller
pieces that individually fall within the agent's reliable operating zone. But decomposition
itself is a design problem with well-studied failure modes. Bad decomposition -- wrong
boundaries, leaky interfaces, insufficient contracts, rigid plans -- can increase total
system complexity rather than reduce it.

**No principled, measurable decomposition process exists for agent pipelines.**

Teams either decompose by intuition (unreliable, untestable) or don't decompose at all
(hitting the complexity ceiling). The field needs a formalized decomposition engine grounded
in the six decades of theory that already exists across systems science, software engineering,
AI planning, algorithm design, project management, and mathematics.

---

## What SYNTROPY Is

SYNTROPY is a research-informed problem decomposition process designed to enable automated
multi-agent pipelines to reliably meet acceptance criteria of SWE problems.

It is:
- A **process**, not a tool. It defines HOW to decompose, not WHAT to decompose.
- **Grounded in theory.** Every rule traces to a canonical source (Simon, Parnas, Constantine,
  Meyer, Baldwin & Clark, Snowden, Fong & Spivak, and the 2023-2026 LLM decomposition literature).
- **Measurable.** Every decomposition property (coverage, coupling, compositionality, sizing)
  has a concrete test. Decomposition quality is a measurable quantity, not a subjective judgment.
- **Testable.** Different decomposition strategies can be compared empirically using the same
  task specification and acceptance criteria. This makes it an eval target, not a doctrine.

---

## The Core Hypothesis

> If we decompose SWE problems using principled rules derived from decomposition theory --
> classifying domain complexity, decomposing by decisions not steps, enforcing contracts at
> every interface, right-sizing subtasks to the agent's reliable zone, verifying externally
> at every boundary, and re-planning from goals on failure -- then automated multi-agent
> pipelines can achieve >50% end-to-end success rate on non-trivial feature implementations,
> up from the current ~11-23%.

### Sub-hypotheses (testable independently):

**H1: Classification prevents category errors.**
Tasks classified as Complex and routed to probe-sense-respond will have higher success rates
than Complex tasks forced through pre-planned decomposition.

**H2: Decision-based decomposition produces better boundaries than step-based.**
Subtasks organized around uncertain decisions (Parnas) will have lower coupling and higher
cohesion than subtasks organized by processing order.

**H3: Contracts reduce compounding failure.**
Explicit pre/postcondition contracts at subtask boundaries will catch errors before they
propagate, reducing the effective per-step failure rate and improving end-to-end outcomes.

**H4: Right-sizing keeps subtasks in the reliable zone.**
Subtasks constrained to 1 file, <15 LOC, 1-2 hunks will individually succeed at >80%,
compared to <55% for medium-sized and <20% for large subtasks.

**H5: External verification at every boundary beats end-only verification.**
Verifying after each subtask (not just at the end) will produce higher end-to-end success
rates despite the token overhead, because it prevents error compounding.

**H6: Re-planning from goals outperforms retry-from-failure.**
When a subtask fails, re-decomposing from the milestone or goal level (incorporating failure
evidence) will produce better outcomes than retrying the same subtask with the same boundaries.

---

## What Success Looks Like

### Near-term (CRUCIBLE experiments)

1. A formalized decomposition process that can be applied by a single operator agent
   to any SWE task specification.
2. Measurable decomposition quality metrics (coverage, coupling, compositionality, sizing)
   with automated checks.
3. A/B experiment results comparing decomposition strategies on the same task set:
   - Step-based vs decision-based decomposition
   - No contracts vs strict contracts
   - End-only verification vs per-boundary verification
   - Fixed plans vs adaptive re-planning
4. Empirical evidence for or against each sub-hypothesis.

### Mid-term (pipeline integration)

5. THE_FACTORY's flow skills (feature-flow, debug-flow, refactor-flow) updated with
   decomposition framework phases.
6. Subtask contract schema integrated into the handoff system.
7. Domain classification integrated into task dispatch.
8. Re-planning protocol integrated into flow skills.
9. Decomposition eval family in `.agent/evals/`.

### Long-term (automation)

10. The decomposition process itself is agent-executable: given a feature spec with
    acceptance criteria, an agent can produce a high-quality decomposition without
    human guidance.
11. The decomposition quality is verified automatically (coverage, compositionality,
    sizing, coupling checks all pass without human review).
12. The pipeline reliably produces working features from specs, with human involvement
    limited to intent capture (Frozen Intent) and final acceptance testing.
13. The process is self-improving: CRUCIBLE experiments continuously test decomposition
    strategy variations and feed results back into the process.

---

## Scope and Boundaries

### In scope
- Problem decomposition process for SWE tasks (feature implementation, bug fixes, refactors)
- Formalized rules for decomposition quality
- Measurable properties at every decomposition boundary
- Integration with existing THE_FACTORY infrastructure
- Experimental framework for comparing decomposition strategies

### Out of scope
- Model training or fine-tuning (we use frontier models as-is)
- New programming languages or frameworks
- General AGI task decomposition (we focus on SWE tasks)
- Replacing human judgment for intent capture (Frozen Intent remains human-authored)
- Decomposition of tasks outside the Clear/Complicated domain (Complex tasks get
  probe-sense-respond, not decomposition)

---

## Theoretical Foundation (Summary)

The process draws from six disciplines:

| Discipline | Key Contributor | Core Insight for SYNTROPY |
|---|---|---|
| Systems Science | Simon (1962) | Decompose where interactions are weak between subsystems |
| Software Engineering | Parnas (1972), Constantine (1974), Meyer (1992) | Decompose by decisions, measure coupling/cohesion, enforce contracts |
| AI Planning | HTN, BDI (Rao & Georgeff, 1995) | Methods govern decomposition; maintain goal separately from plan |
| Algorithm Design | Cormen et al. | Three conditions: decomposable, independent, mergeable |
| Project Management | WBS (PMI) | 100% rule, deliverable-oriented, right-sizing |
| Mathematics | Category Theory (Fong & Spivak, 2019) | Compositionality test: B depends only on A's output |

And from empirical AI research (2023-2026):

| Finding | Source | Implication |
|---|---|---|
| 81% → 18% success drop with complexity | SWE-bench → SWE-bench Pro | Task sizing is critical |
| 70% regression reduction with TDAD | arXiv:2603.17973 | External verification is the top intervention |
| -39% to -70% with multi-agent on sequential tasks | Google/MIT | Don't parallelize sequential work |
| Context effectively used: 10-20% | Chroma Context Rot | Keep subtask context small |
| LLMs cannot self-correct without external feedback | DeepMind, ICLR 2024 | Self-reflection is not verification |
| Function signatures > prose for subtask specification | FunCoder, NeurIPS 2024 | Reduce ambiguity at interfaces |

---

## The Experiment

The core experiment SYNTROPY enables:

```
GIVEN:   A feature specification with defined acceptance criteria
VARY:    decomposition_strategy × verification_frequency ×
         contract_strictness × replan_aggressiveness × agent_config
MEASURE: success_rate × token_cost × wall_clock × rework_rate ×
         contract_violation_rate × replan_count
FIND:    The configuration that maximizes:
           success_rate / (token_cost * wall_clock)
         subject to:
           success_rate > 50%
           rework_rate < 15%
```

This experiment is run in CRUCIBLE. Results feed back into the decomposition process.
The process improves empirically, not doctrinally.

---

## Relationship to Existing Infrastructure

```
SYNTROPY (decomposition process)
    │
    ├── Informs: THE_FACTORY flow skills (how tasks are decomposed and executed)
    ├── Produces: Subtask contracts, decomposition plans, coverage maps
    ├── Measured by: CRUCIBLE (experiments comparing decomposition strategies)
    ├── Tracked by: .agent/ (tasks.jsonl, runs.jsonl, incidents.jsonl)
    ├── Validated by: .agent/evals/decomposition/ (automated quality checks)
    └── Visualized by: Tinyshop (operator dashboard for decomposition state)
```

SYNTROPY is not a new project in the portfolio. It is a cross-cutting process that
improves how ALL projects in the portfolio decompose and execute work. It lives at the
meta-infrastructure level alongside the constitution (CLAUDE.md) and flow skills.

---

## Open Questions

1. **Decomposition agent vs human decomposition:** Should the decomposition itself be
   agent-performed (with human approval) or human-performed? The research suggests
   CodePlan (using dependency graphs) outperforms LLM-generated decompositions. Is there
   a hybrid?

2. **Optimal granularity band:** The research suggests ~30 minutes of human-equivalent
   work per subtask. But the high-confidence zone is 1 file, <15 LOC. These may conflict
   for some task types. What's the actual optimum?

3. **Contract specification cost:** Full JSON Schema contracts at every subtask boundary
   may cost more tokens than they save in error prevention. What's the minimum viable
   contract?

4. **Cynefin classification accuracy:** Can an agent reliably classify tasks into
   Clear/Complicated/Complex/Chaotic? Or does this require human judgment?

5. **Interaction with existing flow skills:** Should SYNTROPY replace the flow skills,
   extend them, or wrap them? The mapping document proposes extension. Is that right?

6. **Eval design for decomposition quality:** What does a good decomposition eval look
   like? Current evals test conventions and flows. Decomposition quality is a higher-order
   property.
