# SYNTROPY Research Agenda

**Date:** 2026-03-22
**Status:** Draft
**Purpose:** Define the research program for building a principled decomposition process that helps automated multi-agent SWE pipelines satisfy acceptance criteria.

---

## Research Objective

Design and validate a decomposition process that converts underspecified software engineering requests into agent-ready, acceptance-criteria-preserving work graphs with measurable quality.

The key phrase is **with measurable quality**.

SYNTROPY should not become another elaborate planning doctrine that cannot be falsified.

---

## Primary Research Questions

### RQ1. What makes a decomposition good?

This is the first question because everything else depends on it.

Working answer:

- it preserves user intent,
- covers the acceptance criteria,
- produces low-coupling leaves,
- makes verification local,
- and improves end-to-end execution outcomes.

**Justification:** Requirements engineering, modularity theory, and systems engineering all imply that decomposition quality must be defined independently of execution quality, even though the two are related.

### RQ2. What makes a leaf task agent-solvable?

You need an operational definition of a leaf, not a visual one.

Candidate properties:

- bounded context
- bounded tool policy
- explicit artifact
- explicit verifier
- manageable dependency surface
- local failure containment

**Justification:** HTN gives the abstract/primitive distinction, but SYNTROPY needs a model-era version of "primitive" that reflects actual agent limits.

### RQ3. Which boundary heuristics produce the best decompositions?

Likely candidates:

- goal-based
- decision-based
- dependency-based
- interface-first
- milestone-first
- hybrids

**Justification:** Parnas suggests decision hiding, DSM suggests dependency-aware cuts, and practical SWE work often needs both.

### RQ4. How much verification is worth paying for?

You need to know whether per-leaf verification, per-milestone verification, or end-only verification gives the best tradeoff.

**Justification:** Recent agent literature strongly supports external verification, but the optimal frequency and strictness are still empirical questions.

### RQ5. When should a decomposition process clarify, probe, or replan instead of continuing?

This is the main guard against false precision.

**Justification:** Requirements ambiguity, wickedness, and evolving discovery are all recurrent sources of failure in real SWE tasks.

### RQ6. When does multi-agent execution help, and when does it hurt?

SYNTROPY should not assume that decomposition implies parallel multi-agent execution.

**Justification:** Current evidence suggests that architecture and task structure interact strongly; sequential work often does not benefit from naive multi-agent splitting.

---

## The Program I Would Run

## Stream A: Formalization

### A1. Define the SYNTROPY artifact set

Create a minimal, formal decomposition artifact family:

- `ProblemFrame`
- `GoalModel`
- `DecisionMap`
- `DependencyGraph`
- `LeafContract`
- `CoverageMap`
- `ReplanRecord`

**Why first:** Without shared artifacts, the project cannot accumulate evidence or compare variants cleanly.

### A2. Define a leaf-task contract

A leaf should carry:

- objective
- inputs
- outputs
- dependencies
- verifier
- cost/time budget
- escalation condition

**Why first:** This is the core unit of decomposition and the smallest meaningful object to benchmark.

### A3. Separate decomposition quality from execution quality

Define metrics that score the decomposition itself before execution:

- acceptance-criteria coverage
- overlap / redundancy
- coupling level
- dependency fan-in / fan-out
- ambiguity left unresolved
- verifier completeness

**Why first:** If you only measure final success, you cannot tell whether failures came from decomposition, execution, or evaluation.

---

## Stream B: Benchmark Design

### B1. Build a task family taxonomy

At minimum:

- bugfix
- vertical feature slice
- refactor
- integration task
- greenfield mini-app
- ambiguous / underspecified request

**Why this matters:** Different decomposition methods may work for different task families. A single benchmark family will mislead you.

### B2. Build hidden-verifier benchmark cases

Each case should include:

- visible brief
- visible acceptance criteria
- hidden checks
- seed repo or seed artifacts
- budget and runtime caps

**Why this matters:** Hidden checks are the cleanest protection against decomposition or execution overfitting.

### B3. Add ambiguity-sensitive cases

Some tasks should be impossible to do well without clarification or deliberate constraint handling.

**Why this matters:** Real SWE problems are often underspecified. A decomposition method that only works on clean inputs is not enough.

---

## Stream C: Comparative Experiments

### C1. Compare boundary strategies

Start with a manageable challenger set:

- step-based
- goal-based
- decision-based
- dependency-based
- hybrid goal + dependency

**Why this matters:** This directly tests the question at the heart of SYNTROPY.

### C2. Compare verification policies

Candidate settings:

- self-check only
- independent verifier at leaf level
- milestone verifier only
- leaf verifier plus hidden end-to-end evaluator

**Why this matters:** Verification cost is real, so it needs to be justified empirically.

### C3. Compare replanning policies

Candidate settings:

- fixed plan
- retry-on-failure
- local replan
- parent-level replan
- clarification-first replan

**Why this matters:** Real pipelines fail in the middle. Recovery quality may matter more than first-plan quality.

### C4. Compare execution topologies

Candidate settings:

- single agent
- planner + executor
- planner + executor + verifier
- graph scheduler over independent leaves

**Why this matters:** Decomposition and execution topology are related but not identical. They need to be tested separately.

---

## Stream D: Automation

### D1. Build a decomposition agent

Only after the artifact schema and benchmark are stable.

This agent should produce:

- goal/constraint extraction
- proposed decomposition graph
- leaf contracts
- coverage map
- confidence / ambiguity notes

**Why later:** Automating an unstable theory tends to lock in mistakes.

### D2. Build a decomposition checker

A separate verifier should check:

- AC coverage
- duplicate leaves
- contract completeness
- dependency cycles
- unverifiable leaves

**Why later:** SYNTROPY needs an independent critic, not just a generative planner.

### D3. Only then explore automated workflow search

Search-based optimization of decomposition rules should be a late-stage program.

**Why later:** Search is only useful once the objective function and artifact ontology are trustworthy.

---

## The First Deliverables I Would Want

1. A one-page SYNTROPY definition
2. A decomposition artifact schema set
3. A leaf solvability definition
4. A benchmark case template
5. A decomposition scorecard
6. A small baseline study comparing 3-5 decomposition styles

This is enough to move from philosophy to experiment.

---

## Suggested Initial Hypotheses

### H1. Decision-aware or dependency-aware decomposition will outperform pure step-based decomposition on non-trivial SWE tasks.

**Why this is plausible:** Step-based breakdowns often mirror process order rather than coupling structure.

### H2. Leaf-local external verification will improve end-to-end success even when it raises token cost.

**Why this is plausible:** It should reduce silent propagation of bad intermediates.

### H3. Clarification or ambiguity handling will matter more on underspecified tasks than additional planner complexity.

**Why this is plausible:** Many failures start before implementation begins.

### H4. Strong single-agent baselines will beat many naive multi-agent variants on serial SWE work.

**Why this is plausible:** Coordination overhead and semantic drift are both expensive.

### H5. Fixed granularity heuristics will underperform capability-based leaf gating.

**Why this is plausible:** "One file" is an imperfect proxy for actual solvability.

---

## Recommended Order Of Operations

### Phase 1: Definition

- define the artifact set
- define leaf solvability
- define the decomposition scorecard

### Phase 2: Benchmark

- build 10-20 benchmark cases across multiple families
- add hidden checks
- add ambiguity-sensitive cases

### Phase 3: Baselines

- run strong simple baselines first
- establish single-agent and planner-executor baselines

### Phase 4: Decomposition Experiments

- compare boundary heuristics
- compare verification policies
- compare replanning policies

### Phase 5: Automation

- automate decomposition
- automate decomposition checking
- later, search over strategies

This sequence matters because it reduces the chance that SYNTROPY becomes an automation stack before it becomes a coherent theory.

---

## Explicit Justification For This Agenda

I am suggesting this order because the literature, taken together, keeps pointing at the same failure pattern:

- intent gets lost early,
- boundaries are drawn poorly,
- verification is too weak or too late,
- and teams then compensate with more orchestration complexity.

That means the first objective should not be "build a very smart agentic planner."

It should be:

> define the decomposition object, define what a good decomposition is, and only then optimize generation and execution of decompositions.

That is the deepest reason for this agenda.

---

## References

- Goal-oriented requirements engineering overview — [DIAL / UCLouvain](https://dial.uclouvain.be/pr/boreal/object/boreal%3A87074)
- Parnas modular decomposition — [MIT-hosted copy](https://sunnyday.mit.edu/16.355/parnas-criteria.html)
- HTN planning references — [University of Maryland HTN page](https://www.cs.umd.edu/projects/plus/HTN/)
- Functional architecture — [SEBoK](https://sebokwiki.org/wiki/Functional_Architecture)
- System verification — [SEBoK](https://sebokwiki.org/wiki/System_Verification)
- System validation — [SEBoK](https://sebokwiki.org/wiki/System_Validation)
- Design by Contract — [Eiffel.org](https://www.eiffel.org/doc/eiffel/ET-_Design_by_Contract_%28tm%29%2C_Assertions_and_Exceptions)
- SWE-agent — [NeurIPS proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html)
- Agentless metadata / DOI — [DBLP](https://dblp.org/rec/journals/corr/abs-2407-01489)
- CodePlan — [Microsoft Research](https://www.microsoft.com/en-us/research/publication/codeplan-repository-level-coding-using-llms-and-planning/)
- FunCoder — [Hugging Face paper page](https://huggingface.co/papers/2405.20092)
- Why Do Multi-Agent LLM Systems Fail? — [ScienceStack summary of arXiv 2503.13657](https://www.sciencestack.ai/paper/2503.13657v3)
