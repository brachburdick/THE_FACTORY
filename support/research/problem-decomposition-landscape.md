---
status: COMPLETE
project_root: /Users/brach/Documents/THE_FACTORY
revision_of: none
supersedes: none
superseded_by: none
---

# Research Findings: Problem Decomposition Landscape

## Questions Addressed
1. Is there a "theory of problem decomposition" relevant to agentic software building?
2. What field or fields should an operator study to improve downstream framing, decomposition quality, and resilience?
3. How does this map onto THE_FACTORY and CRUCIBLE?

## Findings

### Question 1: Is there a single theory of problem decomposition?

**Answer:** No single field owns the whole problem. The closest answer is a
cluster of literatures spanning AI planning, requirements engineering, systems
engineering, dependency analysis, and newer LLM-agent workflow research.

**Detail:**
The heart of the problem is not merely "how to split work into smaller pieces."
It is:

- how to refine goals without losing intent
- how to cut tasks at low-coupling boundaries
- how to know when a subproblem is small enough to solve reliably
- how to verify partial results before integration

The most useful formal homes for that are:

- **Hierarchical planning** for recursive task refinement
- **Goal-oriented requirements engineering** for intent refinement
- **Systems engineering decomposition + V&V** for architecture layers and
  verification at each level
- **Design Structure Matrix / dependency structure** for deciding where to cut
  the system

**Sources:**
- [KAOS / Goal-Driven Requirements Engineering](https://webperso.info.ucl.ac.be/~avl/gore.php)
- [Goal-Oriented Requirements Engineering: A Guided Tour](https://www.bibsonomy.org/bibtex/2555b559dcd219f980d3dd3da9cd710ff/neilernst?lang=en)
- [UMCP / HTN Planning](https://auld.aaai.org/Library/AIPS/1994/aips94-042.php)
- [HTN with Task Insertion and State Constraints](https://www.ijcai.org/Proceedings/2017/623)
- [SEBoK: Functional Architecture](https://sebokwiki.org/wiki/Functional_Architecture)
- [SEBoK: System Verification](https://sebokwiki.org/wiki/System_Verification)
- [SEBoK: System Validation](https://sebokwiki.org/wiki/System_Validation)
- [Design Structure Matrix review](https://www.researchgate.net/publication/3076682_Applying_The_Design_Structure_Matrix_To_System_Decomposition_And_Integration_Problems_A_Review_And_New_Directions)

**Confidence:** HIGH

### Question 2: What are the most relevant fields to study?

**Answer:** If the goal is "bulletproof building of apps by agents," the best
study order is:

1. Goal-oriented requirements engineering
2. Hierarchical task planning
3. Systems engineering decomposition and V-model verification
4. Dependency structure methods such as DSM
5. LLM-specific decomposition/search methods
6. Multi-agent failure analysis and workflow benchmarking

**Detail:**

#### 1. Goal-Oriented Requirements Engineering (GORE / KAOS)

This field studies how to refine high-level stakeholder intent into operational
subgoals, constraints, non-goals, agents, and obstacle analyses.

Why it matters:

- stops decomposition from drifting away from user value
- gives a formal place for non-goals and constraints
- makes "research in the middle" principled via obstacle analysis

This is the closest field to the meta-project -> project -> milestone structure
in THE_FACTORY.

#### 2. Hierarchical Task Network Planning (HTN)

This field studies recursive task decomposition from abstract tasks into
primitive executable actions with preconditions and state constraints.

Why it matters:

- gives a formal answer to "when is a task decomposed enough?"
- supports dynamic decomposition and replanning
- maps naturally onto milestone -> task -> leaf-task execution

This is the closest formal answer to "problem decomposition for agents."

#### 3. Systems Engineering Decomposition and V-Model Verification

This field studies functional, logical, and physical decomposition plus
verification and validation at every level.

Why it matters:

- architecture is decomposed in parallel with verification
- integration does not wait until the end to discover defects
- makes architecture -> development -> validation -> QA structurally sound

This is highly aligned with the architecture/development/validation/QA ladder
already present in the workspace.

#### 4. Design Structure Matrix (DSM)

DSM studies dependency structure so work can be clustered into low-coupling
modules and risky iteration loops can be surfaced explicitly.

Why it matters:

- gives a principled way to choose task boundaries
- explains why some decompositions cause rework and others do not
- helps define "leaf tasks" that do not collide at integration time

This is especially valuable for full-stack or cross-layer app work.

#### 5. LLM Decomposition and Search Methods

Recent LLM research includes:

- least-to-most prompting
- decomposed prompting
- ReAct
- Tree of Thoughts
- LLMCompiler

Why it matters:

- shows smaller intermediate steps improve reliability
- adds search and backtracking where linear plans fail
- helps with micro-level task solving inside a larger decomposition framework

These methods are not a full app-building theory by themselves, but they are
strong local techniques.

#### 6. Multi-Agent Failure Analysis and Workflow Benchmarking

Recent research such as MAST, MultiAgentBench, ChatDev, MetaGPT, and AFlow is
useful because it makes the failure modes visible:

- specification failures
- inter-agent misalignment
- weak verification
- brittle workflow topologies

Why it matters:

- prevents over-romanticizing multi-agent role structures
- pushes the benchmark target toward decomposition quality and verification
- turns pipeline design into an empirical science rather than intuition

**Sources:**
- [Least-to-Most Prompting](https://openreview.net/forum?id=WZH7099tgfM)
- [Decomposed Prompting](https://openreview.net/forum?id=_nGgzQjzaRy)
- [ReAct](https://openreview.net/forum?id=WE_vluYUL-X)
- [Tree of Thoughts](https://openreview.net/forum?id=5Xc1ecxO1h)
- [LLMCompiler](https://huggingface.co/papers/2312.04511)
- [ChatDev](https://aclanthology.org/2024.acl-long.810/)
- [MetaGPT](https://openreview.net/forum?id=VtmBAGCN7o)
- [Why Do Multi-Agent LLM Systems Fail?](https://openreview.net/forum?id=MqBzKkb8eK)
- [MultiAgentBench](https://aclanthology.org/2025.acl-long.421/)
- [AFlow](https://openreview.net/forum?id=z5uVAKwmjf)

**Confidence:** HIGH

### Question 3: How does this map onto THE_FACTORY and CRUCIBLE?

**Answer:** THE_FACTORY is already converging on a serious decomposition model.
The next step is to make that model explicit and benchmarkable.

**Detail:**
The current workspace implicitly mixes:

- GORE for intent and goal framing
- HTN-like refinement for milestones and tasks
- systems engineering for architecture layers and review gates
- experimental agent workflow research for orchestration and evaluation

That means the right next abstraction is not "more prompts" or "more roles."
It is a formalized decomposition program with explicit leaf-task gates,
dependency-aware cuts, and independent verification.

For CRUCIBLE specifically, the most promising target is:

- benchmark decomposition formulas directly
- compare verification regimes directly
- measure whether leaves are independently solvable

The benchmark design in
`projects/CRUCIBLE/docs/benchmark-program.md` is intended as the operational
bridge from theory to experiment.

**Confidence:** HIGH

## Working Synthesis

If a single phrase is needed, the closest useful label is:

**Hierarchical, verification-driven problem decomposition**

If a cluster of field names is acceptable, the best shorthand is:

**Goal-oriented requirements engineering + hierarchical task planning +
systems decomposition + dependency analysis**

## Practical Definition For This Workspace

For THE_FACTORY, problem decomposition can be defined as:

> Refining a high-level goal into a hierarchy or graph of subproblems such that
> each leaf has bounded context, explicit interfaces, independent verifiability,
> manageable dependencies, and compositional correctness under integration.

This definition is not a citation. It is a synthesis of the literature above.

## Suggested Study Order

1. Learn GORE / KAOS to improve goal refinement, non-goals, and obstacle
   analysis.
2. Learn HTN planning to formalize recursive task decomposition and stop
   conditions.
3. Learn systems engineering V&V to pair each architecture layer with
   verification and validation.
4. Learn DSM to make task boundaries and integration risks more principled.
5. Learn LLM decomposition/search methods as local execution tactics, not the
   master theory.
6. Use CRUCIBLE to empirically test which decomposition formulas survive real
   benchmarks.

## Recommended Next Steps

1. Use `projects/CRUCIBLE/docs/benchmark-program.md` as the executable research
   program for comparing decomposition formulas.
2. Introduce a formal leaf-task gate into future task decomposition artifacts.
3. When evolving THE_FACTORY, treat decomposition formula as a first-class
   variant dimension alongside model and prompt choice.
4. Distill the most stable insights into a future decomposition skill or
   operator reference file.

## Skill File Candidates

- Potential future skill: `skills/problem-decomposition/SKILL.md`
  - When it applies: before milestone/task breakdown
  - Core content: goal refinement, dependency-aware cuts, leaf solvability
    gate, verifier pairing, replan triggers
