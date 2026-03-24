# SYNTROPY Research Synthesis

**Date:** 2026-03-22
**Status:** Draft
**Purpose:** Establish the intellectual backbone for SYNTROPY outside the local THE_FACTORY/CRUCIBLE implementation context.

---

## Executive View

There is no single canonical "theory of problem decomposition" that directly answers the SYNTROPY problem.

The closest real answer is a stack of adjacent theories:

1. **Requirements engineering** explains how to preserve user intent while refining it.
2. **Software modularity and architecture theory** explains where to draw boundaries.
3. **Hierarchical planning** explains how to recursively refine abstract tasks into executable leaves.
4. **Systems engineering** explains how to verify each level of the decomposition.
5. **Task analysis / human factors** explains how to choose granularity around actual work performance rather than arbitrary structure.
6. **LLM-agent research** explains where current models fail and what extra constraints agentic decomposition must satisfy.

My strongest synthesis is:

> SYNTROPY is trying to solve **acceptance-criteria-preserving hierarchical problem decomposition for software engineering**.

That is the center of gravity I would use going forward.

---

## What Problem Decomposition Means Here

For SYNTROPY, decomposition is not just "splitting a big task into smaller tasks."

It is the process of transforming:

- an underspecified software problem,
- expressed in human language,
- with acceptance criteria,
- into a graph of low-coupling,
- independently verifiable,
- execution-ready subproblems

without losing the user's real intent.

That last clause matters. A lot of decomposition methods optimize tractability while silently destroying fidelity to the original problem.

---

## The Real Field Map

### 1. Goal-Oriented Requirements Engineering

This is the best starting point if the true objective is "meet acceptance criteria reliably."

Why it matters:

- It starts from goals, constraints, assumptions, and obstacles rather than implementation steps.
- It gives SYNTROPY a way to preserve traceability from leaf work back to user intent.
- It treats ambiguity and conflict as first-class design concerns rather than execution noise.

Key contribution to SYNTROPY:

- Every decomposition artifact should trace back to a goal, constraint, or obstacle.
- Acceptance criteria should not be downstream add-ons; they should shape the decomposition itself.

### 2. Software Modularity and Architecture Decomposition

This is where the boundary rules come from.

Why it matters:

- Parnas's information hiding gives a principled answer to "where should I cut?"
- Coupling/cohesion theory gives measurable properties for good and bad cuts.
- Dependency-aware decomposition matters more than pretty task trees.

Key contribution to SYNTROPY:

- A good decomposition hides volatile decisions and minimizes cross-boundary knowledge.
- Not all subproblems are parallelizable just because they are separate on paper.

### 3. Hierarchical Planning

This is the cleanest formal model for recursive refinement.

Why it matters:

- HTN planning models the move from abstract task to executable leaves explicitly.
- It separates compound tasks from primitive actions.
- It gives a rigorous language for methods, preconditions, ordering constraints, and replanning.

Key contribution to SYNTROPY:

- Decomposition should stop only when a leaf is actually executable and verifiable under the chosen agent/tool policy.

### 4. Systems Engineering and V&V

This is the discipline that prevents decomposition from becoming hand-wavy.

Why it matters:

- It pairs decomposition with verification and validation at every level.
- It distinguishes function, interface, allocation, and integration.
- It treats decomposition as something that must be checked, not merely described.

Key contribution to SYNTROPY:

- Every level of the tree or graph needs its own correctness check, not just final QA.

### 5. Task Analysis and Human Factors

This is an underused but useful adjacent field.

Why it matters:

- Hierarchical task analysis asks what the work actually is before deciding how fine-grained it should be.
- It helps avoid arbitrary decomposition depth.
- It reminds us that decomposition quality is purpose-dependent.

Key contribution to SYNTROPY:

- "Small enough" should be judged relative to observability, controllability, and verifiability, not only LOC or file count.

### 6. Modern LLM-Agent Research

This is the newest layer and the most unstable one, but it matters because SYNTROPY is for current-model pipelines.

Why it matters:

- Current agents degrade on underspecification, long horizons, serial handoffs, and weak verification.
- Simpler baselines remain surprisingly strong.
- Good interfaces and external feedback often beat more elaborate agent organizations.

Key contribution to SYNTROPY:

- A decomposition theory for agentic SWE must be model-aware.
- It must explicitly account for ambiguity, context limits, verification needs, and orchestration overhead.

---

## The Core SYNTROPY Thesis

The heart of the problem is not multi-agent coordination by itself.

It is this:

> How do we transform a human SWE request into a set of subproblems that are:
> 1. faithful to the request,
> 2. solvable by current agents,
> 3. safe to compose back together, and
> 4. externally checkable against acceptance criteria?

That is the main research frame I would use.

---

## The Principles I Would Treat As Foundational

### 1. Intent Preservation

Every decomposition unit should trace back to a user goal, constraint, assumption, or acceptance criterion.

If a leaf cannot be traced back, it is likely process noise.

### 2. Boundary Discipline

A decomposition is only useful if the boundaries reduce coupling rather than create new hidden dependencies.

The main question is not "can I split this?" but "where can I split this without leaking too much state across the cut?"

### 3. Leaf Solvability

A leaf is not "small" because it looks short.

A leaf is small only if one agent, with one tool policy and one bounded context, can finish it and verify it reliably.

### 4. Explicit Interface Contracts

Each boundary should have explicit:

- inputs,
- outputs,
- assumptions,
- invariants,
- and verification rules.

Otherwise decomposition just converts hidden complexity into coordination risk.

### 5. Independent Verification

A decomposition without external verification is mostly ceremony.

The literature keeps pointing to the same thing: self-reflection alone is not enough.

### 6. Replanning As a First-Class Operation

A decomposition process that cannot safely re-cut work after failure is brittle.

Plans must be revisable without rewriting the goal.

### 7. Ambiguity Handling Before Precision

Many SWE failures are not implementation failures. They are understanding failures.

A decomposition process needs an explicit ambiguity-handling step before it overcommits to structure.

### 8. Empirical Calibration

SYNTROPY should treat its own rules as hypotheses.

Granularity, contract strictness, verification frequency, and topology should be measured, not defended as doctrine.

---

## What SYNTROPY Should Probably Output

If SYNTROPY becomes a real process, it should produce more than a checklist.

I would expect it to generate at least these artifacts:

1. **Problem frame**
   - what world/problem is being changed
   - what is in scope
   - what is not

2. **Goal and constraint model**
   - goals
   - non-goals
   - hard constraints
   - assumptions
   - open ambiguities

3. **Decision and dependency map**
   - key choices
   - dependency edges
   - coupling hot spots

4. **Decomposition graph**
   - milestone or capability nodes
   - leaf tasks
   - ordering constraints

5. **Leaf-task contracts**
   - inputs
   - outputs
   - verification oracle
   - escalation rule

6. **Coverage map**
   - which leaves satisfy which acceptance criteria

7. **Replanning policy**
   - what evidence triggers redraw
   - when to escalate

---

## What I Would Not Overcommit To Yet

### Fixed Numeric Granularity Rules

Rules like "`<= 15 LOC`" or "`1 file`" are useful prompts for caution, but they are too brittle to treat as theory.

Different task types have different natural grains.

### Heavy Multi-Agent Structure

The literature does not currently justify assuming "more agents = more reliable."

For sequential SWE work, that often appears false.

### Category Theory As Core Scaffolding

Compositionality is a helpful concept. Category theory is not yet necessary as a central organizing language for the project.

It may be better as an occasional precision tool than as the public face of SYNTROPY.

### Full Upfront Planning For Ambiguous Problems

If the problem is materially underspecified, the right next step may be clarification or probing, not decomposition.

### Self-Assessment As Validation

This one is simple: agent judgment is not enough.

---

## My Current Naming Suggestion

If you want a more precise phrase than "problem decomposition theory," I would use one of these:

- **acceptance-criteria-preserving decomposition**
- **verification-driven hierarchical decomposition**
- **agent-ready software problem decomposition**

Of the three, the first is my favorite because it keeps the user promise in view.

---

## Recommended Reading Order

If you want the fastest path to becoming dangerous in this area, I would go in this order:

1. Goal-oriented requirements engineering
2. Parnas and modularity / coupling / cohesion
3. HTN planning
4. Systems engineering verification and validation
5. Recent SWE-agent and multi-agent failure literature

This order starts with "what are we actually trying to preserve?" before moving into "how do we split it?" and only then "how do current agents distort it?"

---

## References

- Axel van Lamsweerde, "Goal-Oriented Requirements Engineering: A Guided Tour" — [DIAL / UCLouvain](https://dial.uclouvain.be/pr/boreal/object/boreal%3A87074)
- David L. Parnas, "On the Criteria To Be Used in Decomposing Systems into Modules" — [digitized copy](https://sunnyday.mit.edu/16.355/parnas-criteria.html)
- HTN planning project references and classic papers — [University of Maryland HTN page](https://www.cs.umd.edu/projects/plus/HTN/)
- SEBoK Functional Architecture — [SEBoK](https://sebokwiki.org/wiki/Functional_Architecture)
- SEBoK System Verification — [SEBoK](https://sebokwiki.org/wiki/System_Verification)
- SEBoK System Validation — [SEBoK](https://sebokwiki.org/wiki/System_Validation)
- Bertrand Meyer / Eiffel, Design by Contract basics — [Eiffel.org](https://www.eiffel.org/doc/eiffel/ET-_Design_by_Contract_%28tm%29%2C_Assertions_and_Exceptions)
- Herbert A. Simon, "The Architecture of Complexity" citation context — [SFI Press note](https://www.sfipress.org/21-simon-1962)
- SWE-agent — [NeurIPS proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html)
- Agentless metadata / DOI — [DBLP](https://dblp.org/rec/journals/corr/abs-2407-01489)
- CodePlan — [Microsoft Research](https://www.microsoft.com/en-us/research/publication/codeplan-repository-level-coding-using-llms-and-planning/)
- FunCoder / "Divide-and-Conquer Meets Consensus" — [Hugging Face paper page](https://huggingface.co/papers/2405.20092)
- Why Do Multi-Agent LLM Systems Fail? — [ScienceStack summary of arXiv 2503.13657](https://www.sciencestack.ai/paper/2503.13657v3)
