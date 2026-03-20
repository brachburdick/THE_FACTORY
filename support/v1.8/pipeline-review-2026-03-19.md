# Protocol Review: Session Summary Responsibility Split & Contract Integrity

> **Instructions for the human operator:**
> Start a fresh Architect-level conversation. Load these files **in order**:
> 1. This file (`reviews/pipeline-review-2026-03-19.md`)
> 2. `OPERATOR_PROTOCOL.md`
> 3. `PROTOCOL_IMPROVEMENTS.md`
> 4. `IMPLEMENTATION_PROMPT.md`
> 5. Root `templates/session-summary.md`
> 6. Root `templates/validator-verdict.md`
> 7. Root `templates/handoff-packet.md`
> 8. Root `templates/tasks.md`

---

## Your Role

You are an Architect agent performing a targeted protocol review. You have two change packages to implement, plus a downstream deliverable. Apply each change precisely. Do not redesign unrelated sections.

After completing both change packages and updating the root protocol, templates, and IMPLEMENTATION_PROMPT.md, produce a **Protocol Enforcer prompt** as your final output — a self-contained document the operator can hand to a fresh Protocol Enforcer agent to propagate these changes to project-level infrastructure (preambles, templates, startup prompts, AGENT_BOOTSTRAP.md).

---

## Change Package 1: Session Summary Responsibility Split

### Problem

v1.7 added ~15 new fields to the session summary, requiring every implementing agent to produce compliance metadata (routing recommendations, self-assessments, exit checklists, artifact supersession tracking) alongside factual work recaps. Agents already fail to produce session summaries at all (documented in PROTOCOL_IMPROVEMENT.md: Developer and Architect both skipped mandatory artifacts in v1.6.1). Adding more fields worsens this failure mode.

### Design Decision (approved by operator)

Split session summary responsibilities into three layers:

1. **Producer owns factual recap** — fields that map directly to what the agent just experienced. Only the producing agent knows these facts with certainty.
2. **Validator owns compliance interpretation** — artifact completeness, scope compliance, recommended next step, interface-impact detection. The Validator already reads the session summary + handoff + diff and is in the best position for analytical verification.
3. **Hook owns existence gate** — the required output file exists at the exact path. Simple, binary, structural.

### Specific Changes

#### 1. Session Summary Template (`templates/session-summary.md`)

Slim to producer-owned fields only:

```markdown
# Session Summary: [FILL: TASK_ID]

> Status: [FILL: COMPLETE | PARTIAL | BLOCKED]
> Project Root: [FILL: /absolute/path/to/project]

## Role
[FILL: role name. Use "Orchestrator-inline" for approved inline fixes.]

## Objective
[FILL: restate the handoff objective]

## Status
[FILL: COMPLETE | PARTIAL | BLOCKED]

## Work Performed
- [FILL: what was actually done]

## Files Changed
- `[FILL: path/to/file]` — [FILL: what changed and why]
- [FILL: or "None"]

## Artifacts Produced
- `[FILL: path/to/artifact]` — [FILL: what it is]
- [FILL: or "None"]

## Interfaces Added or Modified
- [FILL: exact signatures, payload fields, endpoint shapes, or "None"]

## Decisions Made
- [FILL: decision]: [FILL: rationale]. Alternative considered: [FILL: rejected option and why].
- [FILL: or "None"]

## Scope Violations
- [FILL: needed out-of-scope change, or "None"]

## Remaining Work
- [FILL: what is left undone, or "None"]

## Blocked On
- [FILL: unresolved dependency, decision, or "None"]

## Missteps
- [FILL: command/tool failure, retry, or environment surprise with specifics, or "None"]

## Learnings
- [FILL: durable lesson or skill-file candidate, or "None"]

## Follow-Up Items
- [FILL: backlog-worthy out-of-scope item, or "None"]
```

**Removed fields** (moved to Validator or eliminated):
- `Revision Of` / `Supersedes` / `Superseded By` metadata — collapse to a single `Supersedes` field in the Validator Verdict when relevant. The producing agent rarely knows the full supersession chain.
- `Routing Recommendation` — moved to Validator Verdict as `Recommended Next Step` (already exists there).
- `Exit Checklist` — eliminated. The hook enforces the non-negotiable gate (file exists). The Validator checks completeness. A self-reported checklist adds compliance load without enforcement value.
- `Self-Assessment` — moved to Validator Verdict. The Validator's confidence in the verdict is the meaningful assessment, not the producer's self-evaluation.

**Retained fields** (producer knows these best):
- `Artifacts Produced` — only the producer knows exactly what it wrote and where.
- `Interfaces Added or Modified` — only the producer knows what signatures it created.
- `Follow-Up Items` — the producer surfaces these during work; the Orchestrator promotes them.

#### 2. Validator Verdict Template (`templates/validator-verdict.md`)

Add compliance metadata fields that the Validator now owns:

```markdown
## Compliance Check
- Session summary exists at expected path: [YES | NO]
- Session summary has all required fields: [YES | NO — list missing]
- Artifacts declared in session summary exist on disk: [YES | NO — list missing]
- Interface changes properly flagged: [YES | NO | N/A]

## Supersession
- Artifacts superseded by this session: [list with paths, or "None"]

## Recommended Next Step
- [NEXT TASK | QA DISPATCH | DEVELOPER RETRY | OPERATOR DECISION]
- Dispatch mode: [ORCHESTRATOR DISPATCH | DIRECT DISPATCH]
- [Why this is the correct next step]
```

The `## Compliance Check` section replaces the producer's exit checklist. The Validator verifies mechanically — did the files get written, are the fields present, do the declared artifacts exist. This is verification, not self-reporting.

The `## Supersession` section replaces the three metadata fields from the session summary. The Validator has the context (handoff packet + session summary + diff) to determine what was superseded.

The `## Recommended Next Step` section already exists in v1.7 but gains the `Dispatch mode` subfield so the Orchestrator knows whether to dispatch the next step itself or flag it for operator direct-dispatch.

#### 3. COMMON_RULES.md — Universal Exit Sequence

Replace the current 4-step exit sequence with a simpler version:

```markdown
## Before Ending Your Session

1. Write the required artifact(s) to the exact output path from your handoff packet.
2. If your work produced learnings, append them to `LEARNINGS.md`.
3. Tell Brach: "Session summary written to `[path]`."
```

Three steps. All directly tied to actions the agent just performed. No metadata, no routing analysis, no self-assessment. The Validator handles verification; the hook handles enforcement.

#### 4. OPERATOR_PROTOCOL.md — Section 2.0 (Artifact Metadata)

Simplify the metadata header for session summaries:

```markdown
> Status: [COMPLETE | PARTIAL | BLOCKED]
> Project Root: [/absolute/path/to/project]
```

Two fields, not five. `Revision Of`, `Supersedes`, `Superseded By` remain required on *planning artifacts* (specs, plans, task breakdowns, UI specs) where the Architect or Designer knows the lineage. They are removed from session summaries and verdicts, where supersession tracking is the Validator's job.

#### 5. OPERATOR_PROTOCOL.md — Section 2.2 (Session Summary schema)

Update the inline schema to match the slimmed template above. Remove the removed fields from the schema definition.

#### 6. OPERATOR_PROTOCOL.md — Section 2.7 (Validator Verdict schema)

Add the `## Compliance Check`, `## Supersession`, and expanded `## Recommended Next Step` sections to the inline schema.

#### 7. OPERATOR_PROTOCOL.md — Section 6.1 (Validator Preamble)

Add to the Validator's process:

```markdown
6. Perform compliance check:
   - Verify session summary exists at the path specified in the handoff packet's `## Dispatch > Output path`.
   - Verify all required fields are present and non-empty (or explicitly "None").
   - Verify every artifact listed in `## Artifacts Produced` exists on disk.
   - If any interface changes are listed in `## Interfaces Added or Modified`, verify they are flagged per the `[INTERFACE IMPACT]` protocol or covered by the handoff's scope.
7. Determine supersession: if this session's output replaces a prior artifact, list it in `## Supersession`.
8. Recommend next step with dispatch mode.
```

#### 8. OPERATOR_PROTOCOL.md — Section 6.3 (Orchestrator preamble additions)

Update the Orchestrator's input priority:

```markdown
## Reading Priority
For completed Developer sessions: read the Validator Verdict first. It contains compliance status, recommended next step, and dispatch mode. Read the raw session summary only when:
- The session is BLOCKED or PARTIAL (no verdict exists yet)
- The verdict flags issues that require understanding the producer's reasoning
- You need the exact `## Follow-Up Items` or `## Learnings` content

For non-Developer sessions (Architect, Designer, Researcher): read the session summary directly. These roles do not go through the Validator.
```

#### 9. IMPLEMENTATION_PROMPT.md — Update deliverable specs

Update the COMMON_RULES.md spec to reference the simplified exit sequence.
Update the VALIDATOR.md spec to include the compliance check responsibilities.
Update the session-summary template deliverable to match the slimmed schema.
Update the validator-verdict template deliverable to match the expanded schema.

---

## Change Package 2: Contract Integrity Through Task Decomposition

### Problem

Data fields get silently dropped when a single Developer session modifies both the producer and consumer sides of a contract boundary. The agent changes the payload shape on one side and forgets to update the other. This has been observed multiple times in SCUE (bridge → tracking, API → frontend).

### Design Decision (approved by operator)

Do not add new roles (Contract Agent, Producer Agent, Consumer Agent). Instead, enforce the same isolation through the Architect's task decomposition. The Architect already breaks features into tasks — make it explicit that contract-touching work gets split by interface boundary.

### Specific Changes

#### 1. OPERATOR_PROTOCOL.md — Section 2.6 (Task Breakdown)

Add a field to each task:

```markdown
- **Interface Scope:** [CONTRACT_ONLY | PRODUCER | CONSUMER | END_TO_END | NONE]
```

With guidance:

```markdown
**Interface Scope tagging:**
- `CONTRACT_ONLY`: This task defines or updates the contract (docs/interfaces.md, type definitions, test fixtures). No implementation.
- `PRODUCER`: This task implements the producing side of a contract. Must reference a completed CONTRACT_ONLY task or existing stable contract.
- `CONSUMER`: This task implements the consuming side. Same constraint.
- `END_TO_END`: This task validates field parity across the full path. Typically a Validator or QA task.
- `NONE`: This task does not touch any interface boundary.

When a feature involves contract changes, the Architect should decompose into at least: one CONTRACT_ONLY task, one PRODUCER task, one CONSUMER task. These must be sequenced (contract before implementation). They may run PRODUCER and CONSUMER in parallel if the contract task is complete.
```

#### 2. OPERATOR_PROTOCOL.md — Section 6.3 (Architect preamble additions)

Add to the Architect's task breakdown responsibilities:

```markdown
## Interface Scope Decomposition
When a feature or bug fix requires changes to a contract boundary (WebSocket payloads, API response shapes, type definitions, dataclass fields, message schemas):

1. Tag each task with `Interface Scope` (see §2.6).
2. Create a CONTRACT_ONLY task first: define the contract in `docs/interfaces.md`, create or update test fixtures, and write the canonical field inventory.
3. Create separate PRODUCER and CONSUMER tasks that reference the completed contract.
4. Do not combine PRODUCER and CONSUMER scope in a single task. The cost of an extra session is lower than the cost of a field drop.

When the contract change is trivial (adding one optional field with a clear default), the Architect may combine PRODUCER and CONSUMER into one task with a note explaining why the split is unnecessary.
```

#### 3. Field Inventory Format

Add to OPERATOR_PROTOCOL.md Section 2 (new subsection 2.11):

```markdown
### 2.11 Field Inventory

**Written by:** Architect (during CONTRACT_ONLY tasks) or Developer (when handoff requires it)
**Consumed by:** Validator (for field-by-field verification), QA Tester (for fixture validation)

For any message shape, payload, or DTO under active modification, include a field inventory in the contract documentation (`docs/interfaces.md` or the relevant spec):

| Field | Type | Required | Producer | Consumer | Tested |
|-------|------|----------|----------|----------|--------|
| [name] | [type] | [yes/no] | [layer] | [layer] | [yes/no] |

This table is the Validator's verification source for contract-touching tasks. The Validator checks:
- Every field listed is emitted by the producer
- Every field listed is consumed by the consumer
- Field names, types, and required/optional status match across producer and consumer
- The `Tested` column reflects actual test coverage

When a CONTRACT_ONLY task produces a field inventory, it must also produce or update a canonical fixture file in `tests/fixtures/` that downstream PRODUCER and CONSUMER tasks can use for testing.
```

#### 4. IMPLEMENTATION_PROMPT.md — Update Architect spec

Add `Interface Scope` tagging and field inventory creation to the Architect's deliverable spec.

#### 5. Conditional Field Preservation Checklist (Skill File, not template)

This is NOT a template addition. Create guidance for a project-level skill file that Developers load when their task has `Interface Scope: PRODUCER` or `CONSUMER`:

```markdown
When a task is tagged with Interface Scope PRODUCER or CONSUMER, the Developer should load the project's contract integrity skill file (if it exists) for field-preservation guidance specific to the project's stack and patterns.
```

Add a note to the Architect preamble spec: when producing tasks with `Interface Scope` tags, include the contract integrity skill file in the task's `Context files` if the project has one.

---

## Downstream Deliverable: Protocol Enforcer Prompt

After applying both change packages to `OPERATOR_PROTOCOL.md`, `IMPLEMENTATION_PROMPT.md`, and root `templates/`, produce a self-contained prompt document that the operator can hand to a fresh Protocol Enforcer agent.

The prompt must:
1. Reference the updated `OPERATOR_PROTOCOL.md` and `IMPLEMENTATION_PROMPT.md` as inputs.
2. Instruct the Protocol Enforcer to update the SCUE project (`DjTools/scue/`) specifically:
   - Update `preambles/COMMON_RULES.md` — simplified exit sequence
   - Update `preambles/VALIDATOR.md` — compliance check responsibilities
   - Update `preambles/DEVELOPER.md` — remove any references to removed session summary fields
   - Update `preambles/ORCHESTRATOR.md` — reading priority (verdict first, summary second)
   - Update `preambles/ARCHITECT.md` — Interface Scope decomposition, field inventory
   - Update `templates/session-summary.md` — slimmed schema
   - Update `templates/validator-verdict.md` — expanded schema
   - Update `templates/tasks.md` — Interface Scope field
   - Create `skills/contract-integrity.md` — field preservation guidance skeleton for SCUE's stack (Python backend, TypeScript frontend, WebSocket payloads)
   - Update `AGENT_BOOTSTRAP.md` if any layout references changed
   - Update startup prompts if any loading sequences changed
3. Instruct the Enforcer to clear the SCUE `docs/agents/PROTOCOL_IMPROVEMENT.md` entries that are addressed by these changes (the two BUG entries about artifact skipping).
4. Instruct the Enforcer to produce a migration checklist as its final output.

The prompt must be loadable by a fresh agent with no context from this conversation. Include all necessary context inline.

---

## Rules

- One root cause = one change. Do not bundle unrelated fixes.
- Prefer the smallest change that fixes the problem.
- Do not remove protocol sections. Restructure, clarify, or extend.
- Present all proposals before applying. Operator approves each.
- Bump version to 1.8 after applying.
- Update `PROTOCOL_IMPROVEMENTS.md` resolved section with entries for both change packages.

## Process

1. Read all loaded files.
2. Present the two change packages as structured proposals (per PROTOCOL_REVIEW_PROMPT.md Step 3 format).
3. Wait for operator approval.
4. Apply approved changes to `OPERATOR_PROTOCOL.md`, root `templates/`, and `IMPLEMENTATION_PROMPT.md`.
5. Produce the Protocol Enforcer prompt as the final deliverable.
6. Update `PROTOCOL_IMPROVEMENTS.md`.
