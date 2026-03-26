# Review Prompt Linguistic Analysis

**Date:** 2026-03-26
**Purpose:** Assess how THE_FACTORY asks agents to perform reviews, with a
focus on sentiment, instruction structure, and wording patterns that likely
help or hinder review quality.
**Use:** Research brief for comparing THE_FACTORY's prompt style against
academic work on human-AI communication, prompt design, critique quality,
uncertainty elicitation, and instruction-following.

---

## Corpus Reviewed

Primary artifacts analyzed:

- `support/v1.10/conversation-analysis-prompts.md`
- `support/v2-archive/governance/PROTOCOL_REVIEW_PROMPT.md`
- `support/v1.8/pipeline-review-2026-03-19.md`
- `skills/section-review/SKILL.md`

These documents are enough to characterize the dominant review-request style:
they define role framing, sequencing, constraints, evidence thresholds, and
expected outputs for both code review and meta-pipeline review.

---

## Executive Summary

THE_FACTORY's review prompts are strong where many prompt systems are weak:
they define roles clearly, constrain scope, require evidence, and specify
output formats. This likely improves compliance, reduces drift, and produces
more actionable findings.

The main tradeoff is prompt compression. Several review prompts stack too many
objectives into a single request, often mixing diagnosis, implementation,
packaging, and downstream delegation. That raises cognitive load and may cause
agents to optimize for procedural compliance over independent critical thought.

In short:

- **Strength profile:** high clarity, high rigor, high containment
- **Risk profile:** high directive density, moderate goal stacking, limited
  uncertainty scaffolding
- **Likely effect:** strong execution on bounded reviews; weaker performance on
  cases where the agent should challenge framing, surface ambiguity, or slow
  down before applying changes

---

## Current Linguistic Profile

### 1. Dominant tone: directive, surgical, evidence-first

The prompts are mostly emotionally neutral, but highly controlling in structure.
They read like operating procedures rather than collaborative requests.

Common patterns:

- "Start a fresh conversation"
- "Load these files in order"
- "Apply each change precisely"
- "Do not redesign unrelated sections"
- "Present an evidence summary before proposing changes"

**Assessment:** This is not hostile language. It is disciplined, high-control
language optimized for drift prevention.

**Likely upside:** Better scope adherence and cleaner output.

**Likely downside:** The agent may infer that reframing the task is risky unless
the prompt explicitly invites challenge or uncertainty.

### 2. Role framing is a major strength

Your prompts consistently assign a role early:

- "You are performing a protocol review"
- "You are an Architect agent performing a targeted protocol review"

This gives the model a stable frame for judgment, output style, and boundaries.

**Why it helps:** Role framing reduces ambiguity about what kind of reasoning is
wanted. It also makes multi-agent specialization easier to preserve.

**Research angle:** Compare this against literature on role prompting,
specialization, and evaluator framing effects.

### 3. Evidence requirements are unusually strong

The review prompts repeatedly insist on evidence, specific references, and
concrete change proposals.

Observed patterns:

- evidence summary before recommendations
- explicit root-cause classification
- requirement that every change reference evidence
- prescribed schema for improvement proposals

**Assessment:** This is one of the strongest parts of the current prompt style.

**Likely upside:** Less hand-wavy criticism, better traceability, easier human
triage, stronger post-hoc evaluation.

**Research angle:** Compare against work on structured critique, evidence-based
decision support, and schema-constrained generation.

### 4. Negative constraints do a lot of governance work

The more change-oriented prompts use a heavy concentration of prohibition and
containment language:

- "Do not redesign unrelated sections"
- "Do not add new roles"
- "Do not combine PRODUCER and CONSUMER scope in a single task"
- "Do not apply changes without explicit approval"

Rough signal from the reviewed corpus:

- `support/v1.8/pipeline-review-2026-03-19.md` has especially high directive
  density, including multiple "Do not", "must", and precision markers
- the protocol review prompt is less forceful, but still highly rule-bound

**Assessment:** Negative constraints are effectively preventing drift, but they
are carrying more load than positive success criteria in some prompts.

**Risk:** Overuse of negative phrasing can narrow exploration without always
showing what "good" looks like.

**Improvement:** Pair prohibitions with positive target states. Example:

- Instead of only "Do not redesign unrelated sections"
- Add "Restrict changes to the named packages and preserve surrounding
  behavior unless evidence shows the boundary itself is wrong"

### 5. Goal stacking is the biggest clarity tax

The clearest weakness is that some prompts ask the agent to do too many things
in one pass.

Example pattern:

- diagnose the issue
- update multiple protocol files
- update templates
- generate a downstream prompt for another agent
- preserve versioning logic
- avoid unrelated redesign

**Assessment:** The prompt still works, but it increases task-switching inside a
single response plan.

**Risks introduced:**

- partial compliance hidden by high effort
- shallow reasoning on one sub-goal because another sub-goal is more concrete
- lower-quality critique because the agent is already thinking about execution
- weaker verification because implementation and packaging become the dominant
  completion signal

**Improvement:** Split review prompts into explicit phases:

1. Diagnose and classify
2. Propose smallest fix
3. Wait for approval or apply approved change
4. Package downstream artifacts

### 6. Output schemas are a major asset

Your prompts consistently define output structure:

- JSON for lens analysis
- named sections for protocol review proposals
- structured pass criteria in section review

**Assessment:** This almost certainly improves consistency and comparability
across agents and sessions.

**Tradeoff:** Very rigid schemas can sometimes cause the agent to prioritize
field completion over surfacing a deeper, unexpected issue.

**Improvement:** Add one explicit "unmodeled concern" field to review outputs
where appropriate.

### 7. Warmth is low, but not the problem

The prompt tone is not especially warm, but it is also not abrasive. That is
probably fine. The bigger issue is not sentiment in the emotional sense; it is
whether the language leaves room for calibrated doubt.

Current pattern:

- direct instructions
- low relational padding
- low ambiguity tolerance
- high confidence procedural wording

**Assessment:** The prompts are optimized for compliance, not dialogue.

**Important distinction:** This is different from being rude. The core issue is
that the prompts rarely say when the agent should pause, qualify, or challenge
assumptions.

### 8. Uncertainty scaffolding is thin

The review prompts often ask for evidence and specificity, but they less often
ask for calibration.

Mostly missing today:

- confidence ratings on findings
- explicit assumption logs
- "what would change your mind?" prompts
- permission to challenge the framing before fixing it

**Why it matters:** In review tasks, false confidence is often more expensive
than slower progress. Without a clear uncertainty channel, the agent may choose
a crisp but fragile interpretation.

**Improvement:** Add a short calibration clause such as:

"If the evidence is incomplete or the framing appears wrong, state the
assumption explicitly before proposing a fix."

---

## Overall Assessment

### What is working well

- Strong role definition
- Strong evidence-first framing
- Strong scope control
- Strong output formatting
- Strong bias toward smallest viable fix

### What is most likely hurting performance

- Too many stacked objectives in single review prompts
- Heavy reliance on negative constraints without equal positive exemplars
- Limited uncertainty and assumption signaling
- Compression of analysis and implementation into one task frame

### High-level scorecard

| Dimension | Score (1-5) | Notes |
|---|---:|---|
| Role clarity | 5 | Excellent and consistent |
| Scope containment | 5 | Strong anti-drift language |
| Evidence orientation | 5 | Among the strongest qualities in the corpus |
| Output specificity | 5 | Structured and reusable |
| Cognitive load | 3 | Goal stacking creates avoidable load |
| Uncertainty calibration | 2 | Rarely requested explicitly |
| Positive exemplars | 3 | Strong rules, fewer examples of ideal behavior |
| Linguistic flexibility | 3 | Great for bounded review, less good for reframing |

---

## Recommended Prompt-Level Improvements

### 1. Separate diagnosis from implementation

When a prompt asks for both critique and code changes, split the phases
explicitly or require a checkpoint between them.

### 2. Pair prohibitions with positive success criteria

For every major "do not", add one sentence describing the desired form of the
solution.

### 3. Cap goal stacking

Try to keep a review prompt to one primary objective and one secondary
deliverable. If there are more than two major outcomes, split the prompt.

### 4. Add a calibration clause

Use one short reusable sentence:

"If the task is ambiguous, identify the ambiguity and state the assumption you
are using before proceeding."

### 5. Add one field for unmodeled concerns

This reduces schema lock-in and gives the reviewing agent a place to surface
important issues that do not fit the expected rubric.

### 6. Prefer short, layered sentences over compressed paragraphs

The highest-risk prompts are not vague; they are dense. Breaking them into
smaller instruction blocks will likely help more than adding more detail.

---

## Suggested Review Request Template

Use this when asking an agent to perform a review:

```markdown
## Role
You are performing a [type] review.

## Objective
Determine whether [artifact / implementation / protocol] satisfies [goal].

## Evidence
Read: [ordered inputs]

## Review Questions
1. What failed or is at risk?
2. What evidence shows it?
3. What is the smallest fix in the correct layer?
4. What remains uncertain?

## Constraints
- Stay within [scope]
- Do not change [out-of-scope areas]
- If framing is ambiguous, state the assumption before proceeding

## Output
[schema or section list]
```

This preserves the strengths of the current style while lowering cognitive
compression and improving calibration.

---

## Research Crosswalk

Use these themes when comparing the findings above against academic literature:

- **Instruction specificity vs. overload:** When does more structure improve
  reliability, and when does it overload the model?
- **Negative constraints vs. positive exemplars:** Are "do not" rules enough,
  or do models perform better with examples of desired behavior?
- **Role prompting and evaluator framing:** How much does assigned role change
  critique depth, strictness, or false confidence?
- **Uncertainty elicitation:** What prompt patterns increase calibrated
  uncertainty reporting without collapsing decisiveness?
- **Schema-constrained critique:** Do structured outputs improve review quality,
  or do they hide novel findings?
- **Task decomposition in prompts:** When should diagnosis, implementation, and
  packaging be split into separate stages?
- **Human factors / discourse analysis:** How do tone, urgency, and directive
  density affect agent compliance and independent reasoning?

Suggested search terms:

- "LLM critique prompt structure"
- "role prompting evaluation reliability"
- "uncertainty elicitation large language models"
- "instruction overload prompt engineering"
- "schema constrained LLM evaluation"
- "politeness directness LLM compliance"
- "prompt decomposition review tasks"

---

## Proposed Lens D Summary

The new fourth lens should evaluate:

- sentiment and stance in operator review prompts
- instruction architecture and goal stacking
- constraint style and ambiguity handling
- rewrite opportunities that preserve rigor while improving agent legibility

That lens belongs in the pipeline because prompt wording is part of the control
surface. If the review language is systematically over-compressed or
over-constraining, it can degrade efficiency, correctness, and learning even
when the rest of the pipeline is well designed.
