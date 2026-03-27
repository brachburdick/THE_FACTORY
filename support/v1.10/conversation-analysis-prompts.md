# Conversation Analysis Prompts

> **Usage:** These prompts are for analyzing extracted conversation data from
> `.agent/conversations/`. Run each lens agent in parallel on the same batch
> of sessions, then feed all lens reports to the synthesis agent.
>
> **Batch size:** 5 sessions per batch. If analyzing 20 sessions, run 4 batches
> of 5, then synthesize across batches.
>
> **Input format:** Each agent receives the markdown narrative files
> (`<session-id>.md`) plus the corresponding index entries from `index.jsonl`.

---

## Step 0: Session Selection

Before running any analysis, select which sessions to analyze:

```bash
# Get the 20 most recent sessions with their metadata
python3 -c "
import json
with open('.agent/conversations/index.jsonl') as f:
    entries = [json.loads(l) for l in f if l.strip()]
entries.sort(key=lambda e: e.get('end', ''), reverse=True)
for e in entries[:20]:
    sid = e['session_id'][:12]
    msgs = e['user_messages'] + e['assistant_messages']
    tools = e['total_tool_calls']
    sa = e['subagent_count']
    start = e.get('start', '?')[:16]
    end = e.get('end', '?')[:16]
    proj = e.get('project', '').split('-')[-1]
    print(f'{sid}  {start} → {end}  {msgs:>4} msgs  {tools:>3} tools  {sa:>2} sa  {proj}')
"
```

Group into batches of 5 by time proximity (sessions close together often
relate to the same work). This helps lens agents see connections within batches.

---

## Lens A: Process Efficiency

> **Focus:** How the agent spent its time. What was productive vs. wasted.
> Where the process could be faster or cheaper.

### Prompt

```
You are analyzing Claude Code conversation transcripts to identify process
efficiency patterns. For each session transcript provided, extract:

**1. Dead ends and wasted effort**
- Points where the agent explored an approach then abandoned it
- Time/tokens spent on approaches that didn't contribute to the outcome
- Estimate the fraction of the session spent on unproductive work (rough %)
- What information, if available at session start, would have prevented the waste?

**2. Tool usage patterns**
- Which tool sequences preceded successful outcomes?
- Which tool sequences preceded rework or backtracking?
- Are there repeated multi-tool patterns that could be a single skill/script?
- Count: how many Read calls before the first Edit? (indicates ramp-up cost)

**3. Context window pressure**
- Did the session show signs of context exhaustion? (conversation compression,
  lossy summaries, agent "forgetting" earlier context)
- What was loaded that didn't need to be? What wasn't loaded that should have been?

**4. Subagent effectiveness** (if subagents were used)
- Did subagent results get used, or were they redundant?
- Were subagents launched for things the main agent could have done directly?
- Did parallel subagents duplicate each other's work?

**Output format:**
For each session, produce a structured entry:

```json
{
  "session_id": "...",
  "efficiency_score": 1-5,
  "dead_ends": [{"description": "...", "tokens_wasted_estimate": "low/med/high", "preventable_by": "..."}],
  "productive_tool_patterns": ["Read→Grep→Edit (targeted fix)", ...],
  "wasteful_tool_patterns": ["Read×15→no action (exploratory reading without goal)", ...],
  "context_pressure": "none|mild|severe",
  "top_efficiency_improvement": "one sentence: the single change that would most improve this session's efficiency"
}
```

After analyzing all sessions, produce a **cross-session summary**:
- Top 3 recurring efficiency anti-patterns
- Top 3 recurring efficiency wins (what's working well)
- Estimated total wasted effort across all sessions (rough %)
```

---

## Lens B: Quality & Correctness

> **Focus:** What bugs were introduced, caught, or missed. How verification
> worked (or didn't). Convention adherence.

### Prompt

```
You are analyzing Claude Code conversation transcripts to identify code quality
and correctness patterns. For each session transcript provided, extract:

**1. Bugs and errors**
- Bugs introduced during the session (agent wrote incorrect code)
- Bugs caught during the session (by verification, tests, or user)
- Bugs that escaped the session (mentioned as discovered later, or visible
  in the conversation as untested edge cases)
- For each bug: was it a logic error, API misuse, type error, integration
  issue, or specification misunderstanding?

**2. Verification effectiveness**
- What verification steps were taken? (tests run, manual QA, separate-context
  review, build checks)
- What did verification catch?
- What did verification miss? (bugs found later or by user)
- Were there points where verification was skipped or insufficient?

**3. Convention adherence**
- Did the agent follow established patterns in the codebase?
- Were there inconsistencies introduced? (naming, error handling, file structure)
- Did the agent check existing patterns before writing new code?

**4. Specification alignment**
- Did the implementation match what was asked for?
- Were there scope deviations (agent did more or less than requested)?
- Were ambiguities in the spec surfaced or silently resolved?

**Output format:**
For each session:

```json
{
  "session_id": "...",
  "quality_score": 1-5,
  "bugs_introduced": [{"description": "...", "type": "logic|api|type|integration|spec", "caught_by": "tests|user|verification|escaped"}],
  "verification_steps": ["ran pytest", "separate-context review", ...],
  "verification_gaps": ["no edge case testing for X", ...],
  "convention_violations": ["inconsistent naming in X", ...],
  "spec_deviations": ["added unrequested Y", "missed requirement Z", ...],
  "top_quality_improvement": "one sentence"
}
```

Cross-session summary:
- Most common bug types
- Verification gap patterns (what consistently gets missed?)
- Convention drift patterns (where are inconsistencies accumulating?)
```

---

## Lens C: Learning & Knowledge

> **Focus:** What the agent didn't know that it should have. Information that
> was discovered during the session that should be persisted. Patterns that
> indicate missing skills, hooks, memories, or documentation.

### Prompt

```
You are analyzing Claude Code conversation transcripts to identify knowledge
and learning patterns. For each session transcript provided, extract:

**1. Repeated research**
- Questions the agent investigated that were likely answered in prior sessions
- Information discovered through expensive exploration (multiple tool calls,
  subagents) that should have been immediately available
- API surface discovery that required reading source code instead of docs

**2. Missing knowledge infrastructure**
- Skills that would have helped (repeated multi-step processes without a skill)
- Hooks that would have prevented errors (pre-commit checks, startup validation)
- Memories that would have saved ramp-up time (user preferences, project
  context, prior decisions)
- Documentation gaps that caused confusion or wrong assumptions

**3. Decision patterns**
- Key decisions made during the session (architectural, implementation, scope)
- What alternatives were considered?
- What was the confidence level? (explicit uncertainty vs. confident choice)
- Which decisions led to rework? (low-confidence decisions that turned out wrong)

**4. Knowledge transfer gaps**
- Information discovered during the session that is NOT persisted anywhere
  (not in code comments, not in docs, not in memory, not in ADRs)
- Handoff information that would help the next session on this task
- Implicit knowledge the agent needed that came from the user, not the codebase

**Output format:**
For each session:

```json
{
  "session_id": "...",
  "learning_score": 1-5,
  "repeated_research": [{"topic": "...", "tokens_spent": "low/med/high", "should_be_in": "skill|doc|memory|hook"}],
  "missing_infrastructure": [{"type": "skill|hook|memory|doc", "description": "...", "frequency": "one-off|recurring"}],
  "key_decisions": [{"question": "...", "chosen": "...", "confidence": "high|med|low", "led_to_rework": true/false}],
  "unpersisted_knowledge": ["...", ...],
  "top_learning_improvement": "one sentence"
}
```

Cross-session summary:
- Top 3 knowledge gaps that recur across sessions
- Highest-value skill/hook/memory candidates (by frequency × cost)
- Decision patterns: what types of decisions most often lead to rework?
```

---

## Synthesis Agent

> **Input:** The three lens reports (A, B, C) from one or more batches.
> **Goal:** Combine findings into ranked, actionable improvements.

### Prompt

```
You have received analysis reports from three specialized lens agents that
examined the same set of conversation transcripts:

- **Lens A (Process Efficiency):** [paste report]
- **Lens B (Quality & Correctness):** [paste report]
- **Lens C (Learning & Knowledge):** [paste report]

Your job is to synthesize these into a single prioritized improvement plan.

**Step 1: Cross-lens pattern identification**
Identify findings that appear in multiple lens reports. These are the highest-
signal items because they affect multiple dimensions simultaneously.

Examples:
- If Lens A says "agent wasted time researching beat-link API" and Lens C says
  "beat-link API documentation is missing" — that's one root cause appearing
  in two lenses. The fix (create beat-link API reference doc) addresses both
  efficiency and knowledge gaps.
- If Lens B says "review missed a contract mismatch" and Lens D says "the
  review request stacked diagnosis, implementation, and packaging into one
  prompt without a verification checkpoint" — that's a pipeline issue in the
  wording and structure of the review request itself.

**Step 2: Classify each finding**

For each finding, classify as:
- **PROJECT improvement** — the code, architecture, or project docs need to change
- **PIPELINE improvement** — the process, skills, hooks, memories, or protocol need to change

This distinction matters because they feed different improvement loops.

**Step 3: Rank by (impact × frequency × feasibility)**

For each improvement:
- **Impact:** How much would this improve outcomes? (1-5)
- **Frequency:** How often does this issue arise across sessions? (1-5)
- **Feasibility:** How easy is this to implement? (1-5)
- **Score:** impact × frequency × feasibility (max 125)

**Step 4: Produce the output**

Output a ranked list of improvements:

```json
{
  "analysis_date": "YYYY-MM-DD",
  "sessions_analyzed": 20,
  "batches": 4,

  "cross_lens_patterns": [
    {
      "pattern": "description of the cross-cutting issue",
      "lenses": ["A", "C"],
      "evidence_count": 7,
      "root_cause": "one-sentence root cause"
    }
  ],

  "ranked_improvements": [
    {
      "rank": 1,
      "category": "project|pipeline",
      "title": "short title",
      "description": "what to change and why",
      "evidence": "which sessions and lens findings support this",
      "impact": 5,
      "frequency": 4,
      "feasibility": 3,
      "score": 60,
      "suggested_type": "skill|hook|memory|doc|refactor|convention|eval-case|prompt-template"
    }
  ],

  "project_improvements": ["items from ranked list where category=project"],
  "pipeline_improvements": ["items from ranked list where category=pipeline"],

  "meta_observations": [
    "observations about the analysis process itself — what was hard to assess,
     what data was missing, what would make the next analysis more effective"
  ]
}
```

**Rules:**
- Maximum 15 ranked improvements (if you have more, keep the highest-scoring)
- Every improvement must cite specific session evidence (session IDs + what happened)
- Do not propose vague improvements ("improve code quality") — be specific
  about what changes, where, and how success would be measured
- Separate project improvements from pipeline improvements — they go to
  different places and are actioned differently
```

---

## Execution Checklist

1. **Select sessions:** Run the selection script (Step 0), pick 20
2. **Batch:** Group into 4 batches of 5 by time proximity
3. **For each batch, launch 3 agents in parallel:**
   - Lens A (process efficiency) with the 5 session markdown files
   - Lens B (quality & correctness) with the same 5 files
   - Lens C (learning & knowledge) with the same 5 files
4. **Collect:** lens reports (3 lenses × N batches)
5. **Per-batch synthesis:** Run synthesis agent on each batch's 3 reports
6. **Final synthesis:** Run synthesis agent on the batch syntheses → final ranked list
7. **Triage:** ACCEPT / DEFER / REJECT each improvement
8. **Route:** Project improvements → project `.agent/project-observations.md`.
   Pipeline improvements → `PROTOCOL_IMPROVEMENTS.md`
9. **Action:** Follow v1.10 execution instructions Steps 6-9 (eval cases → implement → verify)

**Cost estimate:** ~3 agent sessions for lens analysis + 1 for synthesis = 4 total per batch.
At ~$2-3 per session, ~$8-12 per batch.
