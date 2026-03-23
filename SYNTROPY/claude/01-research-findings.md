# Research Findings: Problem Decomposition Theory & Agent Reliability

**Date:** 2026-03-22
**Scope:** Theoretical foundations of problem decomposition + empirical limits of AI coding agent reliability
**Purpose:** Inform the design of SYNTROPY's decomposition engine

---

## Part I: Empirical Limits of AI Coding Agent Reliability

### 1. Success Rate Benchmarks

| Benchmark | Best Agent | Pass Rate | Task Character |
|---|---|---|---|
| SWE-bench Verified (500 curated bugs) | Claude Opus 4.5 | ~81% | Single-file, well-specified bugs |
| Snorkel Agentic Coding | Claude Opus 4.5 | 58% | Industry-grade coding tasks |
| SWE-bench Pro (multi-file) | Best performer | ~23% public / ~18% private | Real engineering: 100+ LOC, 4+ files |
| FeatureBench (e2e features) | Best performer | ~11% | Full feature implementation |

**Key finding:** The gap between curated bugs (81%) and real engineering (18-23%) is 3-4x. Marketing numbers and production numbers are fundamentally different. The drop to 11% for end-to-end features shows where the ceiling currently sits.

**Sources:**
- Epoch AI SWE-bench Verified Leaderboard (https://epoch.ai/benchmarks/swe-bench-verified)
- Scale Labs SWE-bench Pro Leaderboard (https://labs.scale.com/leaderboard/swe_bench_pro_public)
- Snorkel Agentic Coding Benchmark (https://snorkel.ai/blog/introducing-the-snorkel-agentic-coding-benchmark/)

### 2. Compounding Failure (Lusser's Law)

System reliability = product of component reliabilities. From 1950s reliability engineering, directly applicable to multi-step agent pipelines.

| Per-step accuracy | 5 steps | 10 steps | 20 steps |
|---|---|---|---|
| 99% | 95.1% | 90.4% | 81.8% |
| 95% | 77.4% | 59.9% | 35.8% |
| 90% | 59.0% | 34.9% | 12.2% |
| 85% | 44.4% | 19.7% | 3.9% |

**Critical nuance:** Agent errors are semantic, not syntactic. An early mistake produces plausible-looking but wrong output, and every subsequent step builds on it. Errors are "sticky" -- they propagate rather than terminate. This is qualitatively worse than mechanical failure because the system cannot self-detect.

**Mitigation insight:** "Failure stickiness matters as much as failure rate." A system that can RECOVER from errors outperforms one where errors are absorbing. The intervention is not always "make fewer mistakes" but "recover from mistakes faster."

**Sources:**
- The Math That's Killing Your AI Agent (Towards Data Science)
- The Hidden Cost of Agentic Failure (O'Reilly)
- Patronus AI: Modeling Statistical Risk in AI Products

### 3. Error Taxonomy

**Microsoft's Taxonomy of Failure Modes in Agentic AI Systems** provides practical industry failure categories. The MAST taxonomy found 41-86.7% failure rates on state-of-the-art multi-agent frameworks. A separate academic taxonomy identified 37 fault categories across 13 major groups.

**Practical error categories observed in coding agents:**

| Error Type | Description | Frequency Signal |
|---|---|---|
| Assumption propagation | Misunderstands early, builds entire features on faulty premises | Very common |
| False completion | Marks tasks done without proper e2e verification | #1 failure mode per Anthropic |
| Context exhaustion | Runs out of context mid-implementation, leaves undocumented half-done work | Common in long tasks |
| Silent logical failures | Code runs without crashing but produces wrong results | Growing worse with newer models (IEEE Spectrum) |
| Security degradation | Improper password handling, insecure object references | 1.5-2x rate vs human coders |
| Concurrency errors | Threading, race conditions, ordering problems | 2x rate vs human coders |

**IEEE Spectrum finding (alarming):** Newer models generate code that avoids syntax errors but REMOVES safety checks or creates fake output matching expected format. This is worse than obvious failure because it lurks undetected.

**Sources:**
- Microsoft Taxonomy of Failure Modes in Agentic AI
- Characterizing Faults in Agentic AI (arXiv:2603.06847)
- IEEE Spectrum: Newer AI Coding Assistants Are Failing in Insidious Ways

### 4. Task Complexity vs Success Rate

- Clear negative correlation between pass rate and code length
- Success rates decline exponentially with task duration
- Claude 3.7 Sonnet: approximately 59-minute half-life (success probability halves every ~59 min of equivalent human work)
- Performance driven more by feature complexity than by time spent
- Performance heavily influenced by specific repository (some repos see <10% across all models)

**Practical implication:** Optimizing by creating tasks that take ~30 minutes for a human to complete dramatically increases agent success rates. This is the "right-sizing" principle.

**Sources:**
- FeatureBench: Benchmarking Agentic Coding (arXiv:2602.10975)
- SWE-bench Pro Paper (arXiv:2509.16941)

### 5. Context Window Limitations

**"Context Rot" (Chroma, 2025):** Tested 18 SOTA models:

- Models do not use context uniformly; performance grows unreliable as input length grows
- "Lost in the Middle" effect: U-shaped attention (beginning and end reliable, middle degrades)
- Popular LLMs effectively utilize only 10-20% of their context
- Effective capacity is ~60-70% of advertised maximum, with sudden drops not gradual degradation
- Claude models decay the slowest overall
- 65% of developers cite context degradation as top cause of poor AI code quality (Stack Overflow 2026)

**Sources:**
- Context Rot (Chroma Research: https://research.trychroma.com/context-rot)
- The Context Window Problem (Factory.ai)

### 6. Verification as a Force Multiplier

| Technique | Improvement | Source |
|---|---|---|
| Reflexion framework (GPT-4, HumanEval) | 80% -> 91% (+11 pts) | Reflexion paper |
| Self-reflection (GPT-4) | 78.6% -> 97.1% (+18.5 pts, p < 0.001) | Self-Reflection in LLM Agents |
| TDAD (Test-Driven Agentic Dev) | Regressions reduced 70% (6.08% -> 1.82%) | TDAD paper (arXiv:2603.17973) |
| TDAD resolution rate | 24% -> 32% | TDAD paper |
| Auto-improvement loop (10-instance subset) | 12% -> 60% with 0% regression | TDAD paper |

**Critical caveat (DeepMind, ICLR 2024):** LLMs CANNOT self-correct reasoning intrinsically without external feedback. They generate plausible but internally coherent errors that defeat consistency-based detection. Self-correction only works when paired with EXTERNAL verification signals (test execution, tool output, human feedback).

**TDD paradox:** TDD instructions without graph context actually INCREASED regressions to 9.94%, worse than vanilla. Agents don't need methodology framing ("do TDD") -- they need to know WHICH tests to check. The signal from test execution matters; the methodology does not.

**Sources:**
- LLMs Cannot Self-Correct Reasoning Yet (arXiv:2310.01798)
- TDAD: Test-Driven Agentic Development (arXiv:2603.17973)
- Teaching LLMs to Self-Debug (ICLR 2024)
- Anthropic: Effective Harnesses for Long-Running Agents

### 7. Human-in-the-Loop Optimal Frequency

**Anthropic's data (millions of Claude Code interactions):**
- Success rate on challenging tasks doubled Aug-Dec while human interventions decreased from 5.4 to 3.3 per session
- Experienced users auto-approve ~40% of the time vs ~20% for new users
- 73% of agent actions have a human in the loop; only 0.8% are irreversible

**Research consensus:**
- Target 10-15% escalation rate for sustainable human review
- Confidence thresholds commonly range 80-90%
- 99% of AI-using developers saved 10+ hours/week, but most reported no decrease in overall workload -- time saved writing code consumed by review and organizational friction

**Sources:**
- Anthropic: Measuring AI Agent Autonomy in Practice
- Human-In-the-Loop Software Development Agents (arXiv:2411.12924)

### 8. Multi-Agent vs Single Agent

**Google/MIT (180 agent configurations tested):**

| Task Type | Multi-Agent Impact | Configuration |
|---|---|---|
| Parallelizable tasks | +80.9% improvement | Centralized orchestrator |
| Sequential reasoning | -39% to -70% degradation | Any multi-agent variant |
| Independent multi-agent (no orchestrator) | 17.2x error amplification | No coordination |
| Centralized multi-agent (with orchestrator) | 4.4x error amplification | Orchestrated |
| Agent cascades (sequential handoff) | +12% over both approaches | Specialized sequential |

**Bottom line:** More agents helps ONLY when tasks are genuinely parallelizable AND you have an orchestrator catching errors. For sequential coding work, adding agents makes things worse.

**Sources:**
- Google: Towards a Science of Scaling Agent Systems
- The Multi-Agent Trap (Towards Data Science)

### 9. The "Last Mile" Problem

- Agents generate 80% of code rapidly; remaining 20% requires deep contextual knowledge
- 66% of developers report spending more time fixing "almost-right" AI code than they saved
- AI-authored PRs contain ~1.7x more issues than human-only code
- Developer trust declining: favorable views dropped 70% to 60% in two years; only 29% trust AI output accuracy (down from 40%)

**IEEE Spectrum:** Newer models learned to generate code that avoids crashing but silently produces wrong results -- removing safety checks, creating fake output matching expected format. This is worse than obvious failure.

**Sources:**
- Addy Osmani: The 80% Problem in Agentic Coding
- IEEE Spectrum: Newer AI Coding Assistants Are Failing in Insidious Ways
- Stack Overflow 2025 Developer Survey

### 10. Anthropic's Own Research

**"Effective Harnesses for Long-Running Agents":**
- Core challenge: each session starts with no memory
- Solution: initializer agent + coding agent + structured artifacts (progress file + git history) for session continuity
- Key failure mode: agents "one-shot" too much, exhaust context, leave undocumented half-done work

**"Demystifying Evals for AI Agents":**
- Environments must be isolated between eval runs
- Shared state causes correlated failures from infrastructure flakiness
- Agent in eval must function same as in production

**Key Anthropic findings on failure:**
- Agents mark features complete without proper e2e testing (#1 failure pattern)
- Providing browser automation tools for testing "dramatically improved performance"
- Success rate doubled over 4 months while human interventions decreased

---

## Part II: Theoretical Foundations of Problem Decomposition

### The Field Map

Problem decomposition is not a single field. It is a convergence point of six disciplines, each contributing a different lens:

```
Systems Science (Simon)
    |
    v
Software Engineering (Parnas, Constantine)
    |
    v
Planning & AI (HTN, BDI)
    |
    v
Algorithm Design (Divide & Conquer)
    |
    v
Project Management (WBS)
    |
    v
Mathematics (Category Theory, Compositionality)
```

### Canon 1: Herbert Simon -- "The Architecture of Complexity" (1962)

**Paper:** Simon, H.A. (1962). "The Architecture of Complexity." Proceedings of the American Philosophical Society, 106(6), 467-482.

**Core concept: Nearly Decomposable Systems.** Complex systems that evolve and survive are almost always hierarchical. They share a specific structural property: interactions within subsystems are strong and fast, while interactions between subsystems are weak and slow.

**Formal properties:**
- A nearly decomposable system has subsystems with strong intra-group interactions and weak inter-group interactions
- Short-run behavior of each subsystem is approximately independent of others
- Long-run behavior of any component depends on others only in an aggregate way
- The "Watchmaker parable": hierarchical systems evolve from simple to complex far faster than non-hierarchical ones because stable intermediate forms are preserved

**The diagnostic for agent pipelines:** Can you summarize what one subtask needs from another in a short aggregate description? If yes, the decomposition is valid. If you need to pass the full internal state, it is not.

### Canon 2: David Parnas -- "On the Criteria To Be Used in Decomposing Systems into Modules" (1972)

**Paper:** Parnas, D.L. (1972). Communications of the ACM, 15(12), 1053-1058.

**Core concept: Information Hiding.** Systems should NOT be decomposed along the lines of processing steps (the flowchart). They should be decomposed so that each module hides a design decision likely to change.

**Key insight:** A conventional decomposition (by processing steps) and an information-hiding decomposition can produce the same runtime behavior but radically different maintainability. The criterion is changeability, not execution order.

**For agent pipelines:** Don't decompose by "first do X, then do Y, then do Z." Ask: what are the decisions in this task that are uncertain or likely to change? Each subtask should encapsulate one such decision.

### Canon 3: Constantine & Yourdon -- Coupling and Cohesion (1974)

**Paper:** Stevens, W., Myers, G., & Constantine, L. (1974). "Structured Design." IBM Systems Journal, 13(2), 115-139.

**Two measurable axes for decomposition quality:**

**Coupling spectrum (between pieces, worst to best):**
1. Content coupling -- one module modifies internals of another
2. Common coupling -- modules share global data
3. Control coupling -- one module controls flow of another via flags
4. Stamp coupling -- modules share composite data structure, use only parts
5. Data coupling -- modules communicate only via simple parameters (BEST)

**Cohesion spectrum (within pieces, worst to best):**
1. Coincidental -- elements grouped arbitrarily
2. Logical -- elements grouped by category but doing different things
3. Temporal -- elements grouped because they execute at same time
4. Procedural -- elements grouped by execution order
5. Communicational -- elements operate on same data
6. Sequential -- output of one is input to next
7. Functional -- all elements contribute to single well-defined task (BEST)

**For agent pipelines:** Use these spectra to audit decompositions. Target: data-coupled subtasks with functional cohesion. If two subtasks share a large context object but each only uses part, restructure to pass only what each needs.

### Canon 4: Baldwin & Clark -- Design Rules: The Power of Modularity (2000)

**Book:** Baldwin, C.Y. & Clark, K.B. (2000). Design Rules, Vol. 1: The Power of Modularity. MIT Press.

**Core concept: Option Value.** Modularity creates the ability to independently experiment with and replace modules. The value depends on: technical potential (sigma -- how much improvement is possible), cost of running experiments, and visibility to the rest of the system.

**Key insight:** The upfront cost of creating modularity (defining interfaces, design rules) is an investment that pays off only if the modules actually get varied. Decomposing a pipeline into modular subtasks is only worth the interface cost if you plan to VARY those subtasks independently.

**For CRUCIBLE:** This directly justifies the decomposition cost -- you explicitly want to swap pipeline components and compare strategies. High sigma (uncertainty about best approach) = high option value from decomposition.

### Canon 5: Cynefin Framework -- Dave Snowden (2007)

**Paper:** Snowden, D.J. & Boone, M.E. (2007). "A Leader's Framework for Decision Making." Harvard Business Review, Nov 2007.

**Problem classification by cause-and-effect structure:**

| Domain | Cause-Effect | Strategy | Decomposable? |
|---|---|---|---|
| Clear | Obvious | Sense-Categorize-Respond | Yes, fully |
| Complicated | Discoverable with expertise | Sense-Analyze-Respond | Yes, with expert knowledge |
| Complex | Only knowable in retrospect | Probe-Sense-Respond | NO -- experiment first |
| Chaotic | No perceivable relationship | Act-Sense-Respond | NO -- stabilize first |

**Critical insight for pipelines:** Before decomposing any task, classify it. Applying decomposition to a Complex problem is a category error. Complex tasks need iterative probing, not pre-planned decomposition.

### Canon 6: Rittel & Webber -- Wicked Problems (1973)

**Paper:** Rittel, H.W.J. & Webber, M.M. (1973). "Dilemmas in a General Theory of Planning." Policy Sciences, 4(2), 155-169.

**Ten characteristics (most relevant to decomposition):**
1. No definitive formulation -- can't fully specify before solving
2. No stopping rule -- never know when you're "done"
3. Solutions are better/worse, not true/false
4. Every attempt is a "one-shot operation" with consequences
5. Every wicked problem is essentially unique

**For pipelines:** If a task exhibits wickedness (especially #1 and #5), rigid decomposition will fail because subtask definitions shift as you work. Use exploratory/conversational architectures, not decompose-and-execute.

### Canon 7: Hierarchical Task Network (HTN) Planning

**Reference:** Erol, K., Hendler, J., & Nau, D. (1994). "HTN Planning: Complexity and Expressivity." AAAI-94.

**Core concept:** Complex tasks are solved by recursively decomposing compound (abstract) tasks into networks of primitive (executable) tasks, guided by "methods" that specify when and how decomposition should occur.

**Formal properties:**
- Tasks are primitive (directly executable) or compound (must be decomposed)
- Methods are schemas: (task, precondition, subtask-network) defining legal decompositions
- A solution is an executable sequence of primitive tasks obtainable by decomposing all compound tasks
- Ordering constraints between subtasks are explicit
- HTN planning is strictly more expressive than classical STRIPS planning

**For pipelines:** HTN is the closest classical AI formalism to what agent pipelines do. Decomposition is governed by methods (your skill definitions / task templates). Failure mode: methods that produce subtask networks with unresolvable ordering conflicts or precondition violations.

### Canon 8: BDI Architecture -- Goal Decomposition

**Reference:** Rao, A.S. & Georgeff, M.P. (1995). "BDI Agents: From Theory to Practice." ICMAS-95.

**Core concept:** Goals decompose into sub-goals via a plan library. BDI agents commit to intentions (adopted plans) and re-plan only on failure.

**Key failure mode for pipelines:** Committing too early to a decomposition plan without a re-planning mechanism. If your pipeline decomposes a task into subtasks and rigidly executes them, you inherit BDI's brittleness.

**Fix:** Maintain the goal separately from the plan. Monitor for plan failure. Re-decompose from the GOAL level, not just retry the failed subtask.

### Canon 9: Divide and Conquer -- Formal Conditions

**Reference:** Cormen, T. et al. (2009). Introduction to Algorithms, Chapter 4.

**Three necessary conditions:**
1. **Decomposability** -- the problem can be split into similar subproblems
2. **Independence** -- solving one subproblem does not depend on solutions to others
3. **Mergeability** -- subproblem solutions can be efficiently recombined

**When it fails:**
- If subproblems overlap (share substructure): D&C degrades, need dynamic programming instead
- If recombination is expensive: decomposition may be slower than monolithic
- The Master Theorem: T(n) = aT(n/b) + f(n) where a = subproblems, n/b = subproblem size, f(n) = recombination cost

**Critical diagnostic for pipelines:** (1) Can I split this into genuinely similar subtasks? (2) Can each be solved without knowing others' answers? (3) Can I merge results cheaply? When condition 2 fails, you need shared state or iterative refinement, not parallel decomposition.

### Canon 10: Category Theory / Compositionality

**Reference:** Fong, B. & Spivak, D.I. (2019). Seven Sketches in Compositionality. Cambridge University Press.

**Core concept:** A system is compositional when you can reason about the whole by reasoning about parts independently. The behavior of A;B (A then B) is fully determined by the behavior of A and the behavior of B independently.

**Compositionality FAILS when there are:** side effects, shared mutable state, or context-dependent behavior.

**The gold standard test for decomposition:** If subtask A produces output X and subtask B consumes X, the pipeline is compositional only if B's behavior depends solely on X and not on HOW A produced X. LLM subtasks often violate this because they carry implicit context, formatting assumptions, or require specific prompt styles.

### Canon 11: Contract-Based Design (Meyer, 1992)

**Reference:** Meyer, B. (1992). "Applying Design by Contract." IEEE Computer, 25(10), 40-51.

**Core concept:** Safe decomposition via explicit contracts:
- **Preconditions:** what the caller must guarantee
- **Postconditions:** what the callee guarantees on completion
- **Invariants:** what is always true

**For pipelines:** Every subtask should have explicit contracts. When a subtask fails, the contract tells you immediately whether the caller violated the precondition or the callee violated the postcondition. Without contracts, debugging cross-subtask failures is guesswork.

### Canon 12: Work Breakdown Structure (WBS)

**Reference:** PMI Practice Standard for Work Breakdown Structures (3rd ed., 2019).

**Key rules:**
- **100% Rule:** WBS includes 100% of scope, no less, no more. Applies recursively.
- **Deliverable-oriented**, not activity-oriented
- **8/80 Rule:** Work packages should take 8-80 hours (maps to an analogous band for LLM subtask sizing)
- **Mutually exclusive elements:** no overlap between siblings
- **Rolling wave:** near-term decomposed finely, distant work left coarse

### Canon 13: The "Dark Side of Modularity"

**Paper:** Topcu, T.G. & Mesmer, B.L. (2022). "The Dark Side of Modularity." ASME J. Mechanical Design, 144(3).

**Core finding:** Decomposition can INCREASE system complexity through three mechanisms:
1. **Interface creation** -- new information needed to define boundaries
2. **Functional allocation** -- decisions about which component owns what
3. **Second-order effects** -- new interactions created by the decomposition itself

**The assumption that decomposition always reduces complexity is empirically falsified.** Decomposition works well when there are few "complicating variables" (variables that couple subproblems). When that set is large relative to each subtask's internal state, do not decompose.

### Canon 14: Marr's Three Levels of Analysis

**Reference:** Marr, D. (1982). Vision. W.H. Freeman.

**Three levels:**
1. **Computational:** what function is computed and why
2. **Algorithmic:** what representations and procedures are used
3. **Implementational:** what physical substrate carries out the algorithm

**For pipelines:** Map directly to decomposition layers. Computational = "what does this pipeline accomplish." Algorithmic = "what is the decomposition strategy, subtask design, result flow." Implementational = "which models, tools, infrastructure." Confusing these levels (changing model and task decomposition simultaneously) makes debugging impossible.

### Canon 15: Functional Decomposition (Systems Engineering)

**Reference:** NASA Systems Engineering Handbook, SP-2016-6105 Rev2.

**Key concepts:**
- Functions defined as transformations of inputs to outputs
- The "no and/or" test: if describing a function requires "and" or "or," it needs further decomposition
- Functional decomposition is separate from physical decomposition -- the mapping is a design decision

**For pipelines:** Task decomposition (functional) should be independent of model/tool allocation (physical). "Extract entities from document" is functional; "use GPT-4 with prompt X" is physical allocation. Keep these separate.

---

## Part III: AI-Specific Decomposition Research (2023-2026)

| Strategy | Paper | Key Finding |
|---|---|---|
| Least-to-Most Prompting | Zhou et al., ICLR 2023 | 99.7% on SCAN; solve subproblems in order, feed earlier solutions as context |
| Decomposed Prompting (DecomP) | Khot et al., ICLR 2023 | Delegate to specialized sub-solvers; enables recursion and non-linear structures |
| Tree of Thoughts | Yao et al., NeurIPS 2023 | 74% vs 4% (CoT) on Game of 24; tree search with evaluation + backtracking |
| Plan-and-Solve | Wang et al., ACL 2023 | Integrate planning before execution; generate plan then execute each step |
| TDAD | arXiv:2603.17973 | Test-driven agentic dev; 70% regression reduction; external verification key |
| Plan-and-Act | arXiv:2503.09572 | Dual-agent (planner + actor); simpler than prior multi-agent approaches |
| Systematic Decomposition | arXiv:2510.07772 | Principled complexity measures for systematic decomposition strategies |
| TDAG (Dynamic Decomp) | 2024 | Don't plan all subtasks upfront; update each based on prior results |
| CodePlan (Microsoft) | FSE 2024 | Use code's dependency graph for task boundaries, not LLM judgment |
| FunCoder | NeurIPS 2024 | Express subtasks as function signatures, not prose descriptions |

---

## Part IV: Cross-Cutting Synthesis

### Eight Universal Principles

| # | Principle | Sources | Diagnostic Question |
|---|---|---|---|
| 1 | Coupling-Complexity Tradeoff | Simon, Dark Side of Modularity, D&C | Does decomposing reduce more complexity than the interfaces add? |
| 2 | Decompose by Decisions, Not Steps | Parnas | What's uncertain? Each subtask hides one uncertain decision. |
| 3 | 100% Rule | WBS | Do subtasks collectively cover the entire original task? No gaps? No overlaps? |
| 4 | Compositionality Test | Category Theory | Does subtask B depend only on A's output, or also on HOW A produced it? |
| 5 | Classify Before Decomposing | Cynefin | Is this Clear/Complicated (decompose) or Complex (probe first)? |
| 6 | Contracts Enable Independence | Meyer | Are pre/postconditions explicit at every boundary? |
| 7 | Option Value Justifies Cost | Baldwin & Clark | Will you vary these modules independently? If not, don't modularize. |
| 8 | Re-plan, Don't Retry | BDI | On failure, re-decompose from the goal, not just retry the failed step. |

### The Task-Sizing Sweet Spot (Empirical)

| Confidence Zone | File Count | Lines Changed | Hunks | Agent Success Rate |
|---|---|---|---|---|
| High (target this) | 1 | <15 | 1-2 | ~80% |
| Medium | 1-2 | 15-55 | 2-7 | ~55% |
| Danger | 2+ | 55+ | 6+ | ~20% |

A feature requiring ~790 LOC (FeatureBench average) needs decomposition into 50-150 agent-solvable units to stay in the high-confidence zone.

### The Three Highest-Leverage Interventions

1. **Right-size tasks** to ~30-minute human-equivalent chunks (stays in high-confidence zone)
2. **External verification** at every task boundary (test execution, not self-reflection)
3. **Orchestrated multi-agent** only for genuinely parallelizable work; single agent + verification for sequential work
