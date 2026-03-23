# Agent Self-Assessment Prompt (v2.1)

> **Usage:** Feed this prompt to any agent (any model, any role) at the end of a
> session or as a standalone reflection task. The agent produces TWO categories
> of observations — **project-level** and **pipeline-level** — and records them
> in different locations. A separate analysis agent reads these to identify
> cross-session patterns.
>
> **Important:** This prompt is model-agnostic and role-agnostic. Do not modify
> it per agent. The value comes from different agents independently surfacing
> observations using the same structure.
>
> **Key principle:** The raw conversation transcript already records WHAT happened.
> Your job here is to CLASSIFY what happened — tag it against known pattern
> categories so the analysis pipeline can aggregate across sessions. Keep
> descriptions minimal (just enough to identify the relevant moment). The
> category code and cause are the value-add.

---

## Prompt

You have just completed (or are about to complete) a work session on this
codebase. Before finishing, perform a structured self-assessment.

**Your goal is classification, not narration.** The conversation transcript
already contains the full story of what happened. You are tagging events from
this session against a known taxonomy so that patterns can be detected across
many sessions by a downstream analysis agent.

**Do not fix anything. Do not refactor. Only classify and record.**

There are two distinct categories of observations. Every observation belongs
to exactly one category. Getting this classification right is critical because
each category feeds a different improvement loop.

---

### Category A: PROJECT Observations

These are about **the code, architecture, and project-specific practices**.
The question is: "What is wrong (or could be better) in the project itself?"

Reflect across these dimensions:

**A1. Code quality issues**
Bugs, dead code, unclear abstractions, missing error handling, untested paths,
coupling that shouldn't exist, type safety gaps. Things a code review should
catch.

**A2. Convention violations or drift**
Inconsistencies in naming, structure, error handling, typing, testing patterns.
Conventions that exist but aren't followed, or gaps where no convention exists
but should.

**A3. Architecture concerns**
Layer violations, inappropriate dependencies, missing contracts between
components, data flow ambiguities, design decisions that create maintenance
burdens.

**A4. Documentation gaps**
API references that are wrong (e.g., docs reference methods that don't exist),
setup instructions that are incomplete, missing prerequisite documentation.

**Recording:** Append project observations to the project's own improvement
tracking file. For SCUE: `projects/DjTools/scue/.agent/project-observations.md`.
For CRUCIBLE: `projects/CRUCIBLE/.agent/project-observations.md`. For the
pipeline itself when assessed as a "project": `.agent/project-observations.md`.
Create the file if it doesn't exist.

Format:
```
- [A<n>] <file:function or component> — <1-sentence classification>. (from: self-assessment, <model>, <date>)
```

Example:
```
- [A1] bridge/waveform_handler.py:emit_track_waveform — dispatches BLUE style for THREE_BAND hardware. (from: self-assessment, claude-opus-4-6, 2026-03-22)
- [A3] frontend WS client + bridgeStore — no shared timer registry; each component manages its own heartbeat independently. (from: self-assessment, claude-opus-4-6, 2026-03-22)
```

Keep descriptions to **one sentence**. The conversation transcript has the full
context — the downstream analysis agent will read both this classification AND
the relevant conversation when investigating.

---

### Category B: PIPELINE Observations

These are about **how the agent worked, how the development process functioned,
and what systemic issues caused or compounded project-level problems**. The
question is: "What went wrong (or could be better) in HOW I worked, and WHY
did project-level issues arise or persist?"

This is the more important category. Every project bug has a pipeline-level
root cause — the question is whether that root cause is worth capturing.

Reflect across these dimensions:

**B1. Wasted effort**
Did you spend significant time on something unnecessary, wrong, or duplicated?
What **caused** the waste — missing information? Ambiguous spec? Wrong
assumption? Tool limitation? Outdated document? Missing hook or memory that
would have saved context/token cost in bootstrapping the environment you
needed?

**B2. Missing context / knowledge gaps**
Was there a point where you needed information not available in the files you
had access to? Was a document outdated? Was there no skill, memory, or hook
that should have existed? Did you have to discover something that a prior
session already discovered but didn't persist?

**B3. Process friction**
Was a step unnecessarily slow, manual, or error-prone? A handoff that lost
information? A gate that didn't catch what it should have? A repeated manual
step that could be automated? Context window exhaustion that forced lossy
continuation?

**B4. Agent reasoning failures**
Did you go down a wrong path? What was the reasoning error? Did you fail to
check a dependency version, validate an API reference against actual code,
verify that a spec matched reality? What check — if it existed as a protocol
step — would have prevented the error?

**B5. Communication issues**
Were there misunderstandings between you and the user? Between you and a
subagent? Between the spec and the implementation? Between what a document
said and what the code did? Was a handoff lossy?

**B6. Root cause linking**
For any PROJECT observation you recorded above, ask: **why did this issue
exist or persist?** Examples:
- "The beat-link API precondition bug (A1) existed because the spec was
  written from documentation, not verified against the actual JAR (B4: no
  protocol step validates API references in specs against real methods)."
- "The FastAPI route ordering bug (A1) persisted because there is no linting
  rule or eval case for catch-all route registration order (B2: missing
  convention enforcement)."
- "The stale ADR (A4) persisted because no convention triggers ADR review
  when upstream dependencies evolve (B2: missing staleness detection for
  dependency-linked ADRs)."

Not every project observation needs a root cause link. Only record one if the
pipeline-level cause is genuine, non-obvious, and worth acting on.

**Recording:** Append pipeline observations to `PROTOCOL_IMPROVEMENTS.md` at
the repository root. Read the existing Pending section first to avoid
duplicates.

Format:
```
- [TYPE] (B<n>) <1-sentence classification>. (from: self-assessment, <model>, <date>)
```

Where TYPE is one of:
- `BUG` — a protocol or convention was violated and nothing caught it
- `GAP` — the protocol doesn't cover a situation that arose
- `FRICTION` — the process is correct but unnecessarily slow or painful
- `IDEA` — a potential improvement, not yet validated by a failure

Example:
```
- [GAP] (B2) No checkpoint mechanism for partially-completed tasks; had to re-read 20+ files to discover prior session was 95% done. (from: self-assessment, claude-opus-4-6, 2026-03-22)
- [FRICTION] (B4) Validated API surface from docs instead of actual JAR; spent 3 tool calls discovering correct method name. (from: self-assessment, claude-opus-4-6, 2026-03-22)
```

Keep descriptions to **one sentence that includes the cause**. The pattern is:
`<what went wrong> because/due to <why>`. If you can't state the cause, the
observation isn't specific enough.

---

### Rules for both categories

- **Classify, don't narrate.** The conversation transcript is the detailed
  record. Your entry is a structured tag, not a story. One sentence max.
- **Always include a location.** File path, function name, workflow step,
  or protocol section. Entries without a location are not actionable.
- **Always include the cause.** Pattern: `<symptom> because <cause>`.
  An entry without a cause is a symptom report, not a classification.
- **Do not duplicate existing entries.** Read the target file first. If your
  observation matches an existing entry, do not add it again. If it adds new
  evidence, append: `(additional evidence: <your observation>)` to that entry.
- **Do not propose solutions.** The analysis agent will identify patterns
  and propose solutions. Your job is to classify accurately.
- **Tag the source.** Always include `(from: self-assessment, <model>, <date>)`
  so the analysis agent can track which observations cluster by model, time,
  or session type.
- **Max 5 entries per category (10 total).** If you have more, keep only the
  highest-signal ones. Fewer high-quality classifications beat many vague ones.

---

### Classification guide

Ask yourself: "If this issue were fixed, what would change?"

- If the **code** changes → PROJECT observation
- If a **process, protocol, skill, hook, convention, or document** changes → PIPELINE observation
- If **both** → Record the code issue as PROJECT, and the root cause as PIPELINE with a B6 link

Examples:
| Observation | Category | Why |
|---|---|---|
| "Route ordering bug in tracks.py" | A1 (project) | Code fix needed |
| "No linting rule prevents catch-all routes from being registered first" | B2 (pipeline) | Convention/tooling gap |
| "Agent spent 3 research rounds because it didn't check dep versions first" | B4 (pipeline) | Reasoning process improvement |
| "Agent accessed outdated ADR that was never updated when dep changed" | B2 (pipeline) | Staleness detection gap |
| "WaveformDetail.style enum precondition undocumented" | A4 (project) | Missing project doc |
| "Spec was written from docs, not verified against actual JAR" | B4 (pipeline) | Verification process gap |

---

### What NOT to do

- Do not modify any code
- Do not create new files except the observation files described above
- Do not propose fixes, refactors, or architecture changes
- Do not record observations about this prompt itself
- Do not conflate project and pipeline observations — get the classification right
