# Meta-Project Layer Research

Date: 2026-03-20
Scope: Research synthesis for whether THE_FACTORY should formalize a meta-project layer for intent capture, iterative re-elicitation, and build-governance.

## 1. Core Question

Is a separate, formalized layer above project execution useful for:

- preventing agent assumption and drift,
- improving UX quality by forcing better user clarification,
- revising plans as the real product takes shape,
- and doing so without re-introducing unnecessary standing agent-role complexity?

## 2. Bottom Line

Short answer: **yes, but only if it is designed as a lightweight process-and-artifact layer, not as a large new cast of standing roles.**

The research points in the same direction from multiple angles:

- Requirements engineering literature treats elicitation as **iterative**, **context-dependent**, and dependent on **communication, validation, and iterative refinement** rather than a one-shot brief.
- Empirical work suggests **structured elicitation methods** and **prototypes/workshops** outperform loose interviewing when the goal is completeness, quality, and reduced misunderstanding.
- Industrial evidence from Google shows that **lightweight but structured design review** improves throughput and decision quality.
- LLM multi-agent research shows that **SOPs, explicit intermediate artifacts, and critique/refinement loops** can help, but recent failure analysis warns that over-complex multi-agent systems often fail due to poor decomposition, role overlap, and weak verification.

So the right move is not "more roles again." It is:

1. a formal **meta-project review loop**,
2. a small number of **durable artifacts**,
3. explicit **question-asking and ambiguity surfacing** before execution,
4. and scheduled **re-elicitation checkpoints** as evidence arrives from real implementation.

That means your instinct is directionally correct, but the safest implementation is closer to a **flow skill / control-plane routine** than a new organizational chart.

## 3. What The Research Actually Says

### 3.1 Requirements elicitation is not a one-time phase

Recent literature still describes requirements elicitation as a difficult, iterative activity with no single universally correct method.

- A 2025 systematic literature review argues there is still "a lack of a unified and systematic framework" for practitioners and identifies **communication, validation, and iterative refinement** as crosscutting activities across elicitation work. It also notes that interviews, workshops, and prototyping are the most common techniques, and that method choice depends on context rather than doctrine. [2]
- ISO/IEC/IEEE 29148:2018 remains the current requirements-engineering standard and explicitly defines required requirements-engineering processes and information items **throughout the life cycle**. [1]

Implication for THE_FACTORY:

- Your problem is not unusual.
- A generalized template is sensible.
- The template must assume that some requirements are only discoverable later and must therefore support revision, not only intake.

### 3.2 "Ask more questions" is not a vague preference; it is a real elicitation method

Your observation that Architect/Designer sessions improved outcomes by asking many questions is strongly consistent with established elicitation findings.

- The Design Thinking literature applied to software requirements argues that, at project start, the important task is to **understand and question what people’s needs are**, with prototyping used to surface the right problem before locking the solution. [3]
- In a family of experiments comparing **Unstructured Interviews**, **Joint Application Design (JAD)**, and **Paper Prototyping**, paper prototyping produced the strongest overall functional-requirement results and unstructured interviews were fastest but lower quality. JAD was best for some non-functional requirements and overlap reduction. [4]
- A 2022 paper on software developers’ search behavior found that targeted **clarification questions** can elicit missing concepts that were absent from the original request, improving downstream retrieval quality. That is not requirements engineering directly, but it supports the deeper mechanism: a bad initial prompt often lacks essential latent concepts, and well-aimed questions surface them. [5]

Implication for THE_FACTORY:

- The user-facing meta layer should not merely "collect a brief."
- It should run a **structured clarification interview** that deliberately searches for missing concepts, competing priorities, unstated constraints, and UX intent.
- Prototypes and examples should be treated as first-class elicitation tools, not post-spec decoration.

### 3.3 Iterative review during development is not over-engineering

Your idea that some truths only become visible once the app exists is also supported.

- The 2025 SLR explicitly describes elicitation as an **iterative process that evolves as understanding improves**. [2]
- Google’s architecture redesign case study reports that starting from a few **critical user scenarios** and **quality-attribute scenarios**, then using lightweight models to discuss trade-offs, was effective and accepted by teams. The paper specifically concludes that these techniques can be integrated into development to communicate and assess design decisions **continuously and iteratively**. [7]
- Google’s design-review work shows that a **structured, lightweight review process** can improve speed rather than slow it down: their approach reduced median time-to-approval by **25%** across a large internal dataset. [6]

Implication for THE_FACTORY:

- A meta layer should not run only before bootstrap.
- It should run at defined checkpoints where the team updates understanding from prototypes, integration friction, UX feedback, and implementation discoveries.
- If lightweight, it should reduce waste rather than add ceremony.

### 3.4 Multi-agent systems benefit from structure, but complexity is a tax

The multi-agent evidence is mixed in exactly the way your intuition suggests.

Positive findings:

- MetaGPT argues that encoding **Standardized Operating Procedures (SOPs)** into prompt sequences and using explicit intermediate verification improves coherence in multi-agent collaboration. [10]
- ChatDev argues that software work benefits from specialized agent collaboration when communication protocols are explicit. [11]
- AgentCoder shows a concrete gain from role specialization plus iterative test feedback in code generation benchmarks. [9]
- Self-Refine shows that critique-and-revise loops can improve outputs by about **20% absolute on average** across tasks. [8]

Negative finding:

- The 2025 MAST paper, "Why Do Multi-Agent LLM Systems Fail?", finds that gains are often minimal and classifies failures into **system design issues**, **inter-agent misalignment**, and **task verification** failures. [12]

Implication for THE_FACTORY:

- You are **not wrong** that a separate meta layer can be valuable.
- But the criticism about role richness still partly applies if you implement the meta layer as lots of new standing personas.
- The safer pattern is: **one meta-process, few artifacts, strong gates, explicit review cadence**.

## 4. Recommended Model For THE_FACTORY

## 4.1 Design Principle

Implement the meta-project layer as a **control-plane flow**, not a new execution org chart.

In v1.9.1 terms, this wants to be something like:

- a `discovery-governance` flow skill, or
- a pair of flows: `intent-discovery` and `evidence-review`,

instead of adding several persistent new roles.

This keeps you aligned with the v1.9 simplification direction:

- fewer standing personas,
- stronger explicit process,
- better artifacts,
- easier evals,
- lower coordination overhead.

## 4.2 What this layer should own

This layer should own four things:

1. **Intent capture**
   - What problem matters, for whom, and why now.
2. **Ambiguity exposure**
   - What is unknown, disputed, assumed, or confidence-limited.
3. **Learning integration**
   - What changed after prototyping/building/testing.
4. **Dispatch readiness**
   - Whether execution agents have enough signal to proceed safely.

It should explicitly *not* own coding, implementation detail, or long freeform design wandering.

## 4.3 The most useful abstraction: stable core + iterative review

The cleanest generalized format is a two-artifact model:

### Artifact A: Project Definition Record (stable core)

This is the durable "what we currently believe" object.

Recommended fields:

- `Problem statement`
- `Target users / stakeholders`
- `Jobs-to-be-done / key scenarios`
- `Desired outcomes`
- `Success metrics`
- `Non-goals`
- `Hard constraints`
- `Quality attributes`
  - usability
  - performance
  - reliability
  - privacy/security
  - maintainability
  - cost/time sensitivity
- `UX intent`
  - emotional tone
  - visual intent
  - friction tolerance
  - trust requirements
- `Known assumptions`
  - each tagged with confidence: high / medium / low
- `Known unknowns`
  - each tagged with discovery path
- `Decision rights`
  - what the operator must approve vs. what agents may decide

### Artifact B: Evidence Review Packet (iterative)

This is the "what reality just taught us" object.

Recommended fields:

- `What changed since last review`
- `Evidence observed`
  - prototype feedback
  - build friction
  - user reaction
  - architecture surprises
  - testing/QA results
- `Assumptions invalidated`
- `Assumptions strengthened`
- `New questions surfaced`
- `Requirement changes proposed`
- `UX changes proposed`
- `Architecture/plan changes proposed`
- `Do not change yet`
  - items intentionally deferred
- `Next-slice recommendation`
- `Dispatch status`
  - `READY`
  - `READY WITH EXPLICIT ASSUMPTIONS`
  - `NOT READY`

This split matters:

- The first artifact stabilizes identity and direction.
- The second artifact absorbs learning without constantly rewriting the whole project narrative.

## 5. Recommended Operating Loop

Use a repeating five-step loop:

1. **Elicit**
   - Ask structured questions before planning/building.
2. **Synthesize**
   - Update the Project Definition Record.
3. **Execute a thin slice**
   - Build or prototype enough to learn.
4. **Review evidence**
   - Produce an Evidence Review Packet.
5. **Re-dispatch**
   - Update priorities, assumptions, and boundaries before the next execution wave.

This is essentially a controlled version of:

`intent -> artifact -> execution -> evidence -> revised artifact -> next execution`

That directly fits THE_FACTORY’s artifact-first philosophy.

## 6. What Questions The Meta Layer Should Force

If the goal is to prevent assumption drift, the generalized template should force answers to the following categories before execution begins.

### 6.1 Product reality

- What exact user pain are we reducing?
- Who feels it most sharply?
- What would make this obviously valuable to them?
- What would make it disappointing even if technically "complete"?

### 6.2 UX intent

- What should the experience feel like?
- Where should the product feel fast, calm, powerful, safe, playful, or precise?
- What kinds of friction are acceptable?
- What kinds of friction would feel like betrayal?

### 6.3 Decision boundaries

- What may agents infer?
- What must agents escalate?
- What trade-offs can be made locally?
- What trade-offs require human taste or product judgment?

### 6.4 Quality attributes

- What matters more here: speed, clarity, robustness, flexibility, polish, explainability, reversibility, or cost?
- Which failures are tolerable?
- Which failures are unacceptable?

### 6.5 Evidence plan

- What can only be learned after a prototype exists?
- What is the cheapest artifact that will teach us that?
- What result would change the plan?

These categories matter more than any single prompt wording.

## 7. Suggested Review Cadence

The review loop should be **event-driven**, not purely time-driven.

Run an Evidence Review Packet when one of these happens:

- after the first clickable or runnable prototype,
- after the first end-to-end thin slice,
- after any notable user/operator discomfort with the UX,
- after any architectural surprise,
- after any validator or QA pattern repeats,
- after 2-5 execution tasks when work is moving fast but still uncertain,
- before committing to a large batch of implementation work.

This keeps the system adaptive without turning every task into a ceremony.

## 8. How This Fits The Existing Critique About Too Many Roles

Your instinct that this is somewhat outside the earlier criticism is **partly right**.

Why it is different:

- This layer addresses **project-definition quality**, not execution specialization.
- It exists to improve the quality of downstream work by reducing ambiguity and capturing learning.
- It maps to real software engineering disciplines: requirements elicitation, design review, and iterative architecture/UX validation.

Why the criticism still partly applies:

- If you implement this as many new standing personas, you reintroduce coordination overhead.
- If it creates large documents with no dispatch effect, it becomes analysis theater.
- If it is not tied to gates and artifacts, it becomes another conversational cloud layer.

So the best interpretation is:

- **yes** to a formal meta-project layer,
- **no** to a large new caste of permanent agents,
- **yes** to a control-plane flow with durable artifacts and evals.

## 9. Minimal Version Worth Trying

If you want the smallest version likely to produce real signal, add only these three things:

1. `Project Definition Record`
   - one durable file
2. `Evidence Review Packet`
   - one recurring review file
3. `Dispatch Readiness Gate`
   - execution cannot start unless:
     - user,
     - problem,
     - desired outcome,
     - non-goals,
     - hard constraints,
     - and next-slice acceptance signal
     are all explicit

That is enough to test the value of the layer without rebuilding the protocol around it.

## 10. Anti-Patterns To Avoid

- Treating "ask lots of questions" as unstructured conversation rather than a repeatable elicitation protocol.
- Adding new roles when a flow skill or artifact schema would do.
- Waiting for perfect certainty before dispatching any execution work.
- Rewriting the whole project brief after every learning event instead of tracking deltas.
- Letting unknowns stay implicit instead of converting them into tagged assumptions or questions.
- Running reviews that do not change routing, scope, or acceptance criteria.

## 11. Best Current Thesis

The strongest current thesis is:

> The missing layer is not another builder role. It is a lightweight, formalized discovery-and-review control plane that converts unknown unknowns into explicit assumptions, explicit questions, and evidence-driven revisions.

That is how you reduce second-degree ignorance without freezing in analysis paralysis.

## 12. Suggested Next Protocol Experiment

For the next protocol iteration, test:

1. Add a single new support artifact pair:
   - `PROJECT_DEFINITION_RECORD.md`
   - `EVIDENCE_REVIEW_PACKET.md`
2. Add one flow:
   - `discovery-governance-flow`
3. Add one gate:
   - `dispatch_readiness`
4. Measure:
   - number of `[ASK OPERATOR]` incidents discovered late,
   - number of mid-build requirement reversals,
   - validator failures caused by missing intent,
   - operator-reported UX dissatisfaction,
   - spec revision frequency before vs. after the layer

If those metrics improve, the layer is earning its keep.

## 13. Sources

1. ISO. *ISO/IEC/IEEE 29148:2018 Systems and software engineering — Life cycle processes — Requirements engineering*. [https://www.iso.org/standard/72089.html](https://www.iso.org/standard/72089.html)
2. Hidalgo et al. *What Is the Process? A Metamodel of the Requirements Elicitation Process Derived from a Systematic Literature Review* (2025). [https://www.mdpi.com/2227-9717/13/1/20](https://www.mdpi.com/2227-9717/13/1/20)
3. Araujo et al. *Design Thinking: Challenges for Software Requirements Elicitation* (2019). [https://www.mdpi.com/2078-2489/10/12/371](https://www.mdpi.com/2078-2489/10/12/371)
4. Rueda et al. *Requirements Elicitation Methods based on Interviews in Comparison: A Family of Experiments* (2020). [https://www.uv.es/joigpana/Files/Journals/IST_2020Requirements_elicitation.pdf](https://www.uv.es/joigpana/Files/Journals/IST_2020Requirements_elicitation.pdf)
5. Imran and Damevski. *Using clarification questions to improve software developers' Web search* (2022). [https://arxiv.org/abs/2207.12768](https://arxiv.org/abs/2207.12768)
6. Ziftci and Greenberg. *Improving Design Reviews at Google* (ASE 2023). [https://research.google/pubs/improving-design-reviews-at-google/](https://research.google/pubs/improving-design-reviews-at-google/)
7. Jia et al. *A Model-based, Quality Attribute-guided Architecture Re-Design Process at Google* (ICSE-SEIP 2023). [https://research.google/pubs/a-model-based-quality-attribute-guided-architecture-re-design-process-at-google/](https://research.google/pubs/a-model-based-quality-attribute-guided-architecture-re-design-process-at-google/)
8. Madaan et al. *Self-Refine: Iterative Refinement with Self-Feedback* (2023). [https://arxiv.org/abs/2303.17651](https://arxiv.org/abs/2303.17651)
9. Huang et al. *AgentCoder: Multi-Agent-based Code Generation with Iterative Testing and Optimisation* (2024). [https://arxiv.org/abs/2312.13010](https://arxiv.org/abs/2312.13010)
10. Hong et al. *MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework* (2024 version). [https://arxiv.org/abs/2308.00352](https://arxiv.org/abs/2308.00352)
11. Qian et al. *ChatDev: Communicative Agents for Software Development* (2024 version). [https://arxiv.org/abs/2307.07924](https://arxiv.org/abs/2307.07924)
12. Cemri et al. *Why Do Multi-Agent LLM Systems Fail?* (2025). [https://arxiv.org/abs/2503.13657](https://arxiv.org/abs/2503.13657)
