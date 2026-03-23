# Protocol Review Session

> **Instructions for the human operator:**
> Trigger in two ways:
>
> **1. Batch review (periodic):** When `PROTOCOL_IMPROVEMENTS.md` has accumulated enough entries.
>
> **2. Evidence-driven review:** When run records, incident logs, or eval results show
> a pattern worth addressing.
>
> Start a fresh conversation. Load these files **in order**:
> 1. `PROTOCOL_REVIEW_PROMPT.md` (this file)
> 2. `CLAUDE.md`
> 3. `OPERATOR_PROTOCOL.md`
> 4. `PROTOCOL_IMPROVEMENTS.md`
> 5. Relevant run records from `.agent/runs.jsonl` and incident logs from `.agent/incidents.jsonl`
> 6. Relevant eval results from `.agent/evals/`

---

## Your Role

You are performing a protocol review. Read the evidence, diagnose root causes, and propose
specific changes to the operating model. Apply targeted fixes based on observed failures —
do not redesign the system.

## What You Receive

- `CLAUDE.md` — the runtime constitution
- `OPERATOR_PROTOCOL.md` — the governance layer
- `PROTOCOL_IMPROVEMENTS.md` — observation backlog
- Run records and incident logs (structured data)
- Eval results (if relevant)

## Your Process

### Step 1: Gather Evidence

Read all inputs. Identify which evidence sources are available:
- Backlog entries from `PROTOCOL_IMPROVEMENTS.md`
- Run records from `.agent/runs.jsonl`
- Incident logs from `.agent/incidents.jsonl`
- Review scorecards from `.agent/reviews/scorecards.jsonl`
- Eval results from `.agent/evals/`

Present an evidence summary before proposing changes.

### Step 2: Classify Root Causes

For each issue, classify the root cause:

| Classification | Meaning |
|---------------|---------|
| `SPECIFICATION_OR_SYSTEM_DESIGN` | The intent, spec, or architecture was wrong or incomplete |
| `HANDOFF_OR_ALIGNMENT` | The handoff between stages lost information or introduced drift |
| `VERIFICATION_OR_TERMINATION` | The verification step missed the problem or the loop didn't terminate |

Multiple entries often share one underlying cause. Group them.

Present classifications. Operator may adjust.

### Step 3: Triage by Priority

| Priority | Criteria |
|----------|----------|
| **P0 — Fix now** | BUG: agents violate protocol and no gate catches it |
| **P1 — Fix soon** | GAP: real situation had no protocol guidance |
| **P2 — Improve** | FRICTION: protocol works but is unnecessarily slow |
| **P3 — Consider** | IDEA: not yet validated by a real failure |

### Step 4: Apply Scaffold-First Bias

Before proposing any change, evaluate fixes in this order:
1. **Schema fix** — can the artifact schema prevent this?
2. **Hook or validation fix** — can an automated check catch this?
3. **Checklist or gate fix** — can a flow skill gate prevent this?
4. **Eval fix** — can an eval case detect drift toward this failure?
5. **Dispatch-quality fix** — can better intent capture prevent this?
6. **Model-selection change** — only if all above are insufficient

### Step 5: Propose Changes

For each group (P0 first), answer these questions:

```markdown
### Change Proposal: [SHORT_NAME]

**Addresses:** [issue numbers/descriptions]
**Root cause classification:** [SPECIFICATION | HANDOFF | VERIFICATION]

**What failed?**
[One sentence]

**What evidence shows it?**
[Reference to run records, incidents, evals, or backlog entries]

**Why did the current gate miss it?**
[One sentence]

**Smallest fix in the correct layer:**
- **File:** [which file]
- **Section:** [which section]
- **Current behavior:** [what it says now, or "not addressed"]
- **Proposed behavior:** [what it should say]

**What eval or metric should improve if this works?**
[Specific metric or eval case]

**Trade-offs:** [downsides or added complexity]
```

### Step 6: Human Review

Present all proposals. Operator approves, rejects, or modifies each.
Do not apply changes without explicit approval.

### Step 7: Apply Approved Changes

For each approved proposal:
1. Make the change to the relevant file(s).
2. Update `PROTOCOL_IMPROVEMENTS.md`:
   - Pending → Resolved with version and description.
   - Reviewed but postponed → move to Deferred with reason.
3. Update `.agent/evals/manifest.md` with version lineage.
4. Update `.agent/VERSION.md` if the change is material.

### Step 8: Summary

Produce a changelog entry:

```markdown
## Version [X.Y] — [DATE]

### Changes
- [Change 1]: [one-line description]
- [Change 2]: [one-line description]

### Evidence Used
- [run records, incident logs, eval results referenced]

### Deferred
- [Entries reviewed but not addressed, with reason]
```

## Rules

- One root cause = one change proposal. Don't bundle unrelated fixes.
- Prefer the smallest change that fixes the problem.
- Fix problems closest to where they occur: prefer skill/template changes over constitution changes.
- Defer IDEA entries with no supporting evidence unless the operator overrides.
- Never remove protocol sections. You may restructure, clarify, or extend.
- Every proposed change must reference evidence, not just intuition.
- Protocol changes must pass an eval before being considered permanent.

## Writing Quality

- No redundant sentences.
- No hedging language. Write directives, not suggestions.
- No duplicated rules. If a rule exists in one place, reference it.
- Dense over verbose.
