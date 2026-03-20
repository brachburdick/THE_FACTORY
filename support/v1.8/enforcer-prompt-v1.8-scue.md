# Protocol Enforcer Prompt: SCUE Project Sync — v1.8 Changes

> **Instructions for the human operator:**
> Start a fresh Protocol Enforcer conversation. Load these files **in order**:
> 1. This file (`reviews/enforcer-prompt-v1.8-scue.md`)
> 2. `OPERATOR_PROTOCOL.md` (v1.8)
> 3. `IMPLEMENTATION_PROMPT.md`
> 4. Root `templates/session-summary.md`
> 5. Root `templates/validator-verdict.md`
> 6. Root `templates/handoff-packet.md`
> 7. Root `templates/tasks.md`
> 8. The SCUE project's existing preambles, templates, and `AGENT_BOOTSTRAP.md` (see file list below)

---

## Context

You are a Protocol Enforcer agent. The root protocol has been updated from v1.7 to v1.8 with three changes:

### Change 1: YAML Frontmatter for Artifact Metadata
All artifact metadata headers switched from blockquote format (`> Status: DRAFT`) to YAML frontmatter (`---\nstatus: DRAFT\n---`). Two tiers:
- **Full metadata** (5 fields: `status`, `project_root`, `revision_of`, `supersedes`, `superseded_by`) — for planning artifacts (handoffs, specs, plans, task breakdowns, UI specs, review reports).
- **Slim metadata** (2 fields: `status`, `project_root`) — for session summaries and verdicts.

### Change 2: Session Summary Responsibility Split
Session summaries slimmed to producer-owned fields only. Removed: `Revision Of`/`Supersedes`/`Superseded By` metadata, `Artifacts Superseded`, `Routing Recommendation`, `Exit Checklist`, `Self-Assessment`. These responsibilities moved to the Validator Verdict:
- New `## Compliance Check` section (session summary exists, fields present, declared artifacts exist on disk, interface changes flagged)
- New `## Supersession` section (artifacts superseded by this session)
- Expanded `## Recommended Next Step` with `Dispatch mode` subfield

Universal exit sequence simplified to 3 steps:
1. Write the required artifact(s) to the exact output path from your handoff packet.
2. If your work produced learnings, append them to `LEARNINGS.md`.
3. Tell Brach: "Session summary written to `[path]`."

Orchestrator gains a **Reading Priority** rule: read Validator Verdict first for completed Developer sessions; raw session summary only when BLOCKED/PARTIAL or when verdict flags issues requiring producer reasoning.

### Change 3: Contract Integrity Through Task Decomposition
Task breakdown schema gains `Interface Scope` field: `CONTRACT_ONLY | PRODUCER | CONSUMER | END_TO_END | NONE`.

Architect gains **Interface Scope Decomposition** rules:
- When a feature involves contract changes, decompose into: CONTRACT_ONLY task (define contract, field inventory, fixtures) → PRODUCER task → CONSUMER task.
- Do not combine PRODUCER and CONSUMER in a single task unless the change is trivial.
- Include contract integrity skill file in Context files for Interface Scope-tagged tasks.

New §2.11 **Field Inventory** schema: table format (Field | Type | Required | Producer | Consumer | Tested) for contract documentation. Validator uses this for field-by-field verification.

---

## Your Target

The SCUE project at `DjTools/scue/`.

## SCUE Project Files to Update

### Preambles

**`preambles/COMMON_RULES.md`**
- Replace the Universal Exit Sequence (4-step: artifact checklist, chain-status, session retro, self-assessment) with the simplified 3-step version.
- Remove any references to `Self-Assessment`, `Exit Checklist`, or `Routing Recommendation` as session summary fields.

**`preambles/VALIDATOR.md`**
- Add compliance check responsibilities (steps 6-8 from §6.1):
  - Step 6: Compliance check — verify session summary exists at expected path, all required fields present, declared artifacts exist on disk, interface changes properly flagged.
  - Step 7: Determine supersession — if this session's output replaces a prior artifact, list in `## Supersession`.
  - Step 8: Recommend next step with dispatch mode.
- Update output template reference to match expanded validator verdict schema.

**`preambles/DEVELOPER.md`**
- Remove any references to removed session summary fields (`Routing Recommendation`, `Exit Checklist`, `Self-Assessment`, `Artifacts Superseded`).
- Ensure session summary artifact output references the slimmed schema.

**`preambles/ORCHESTRATOR.md`**
- Add Reading Priority section: Validator Verdict first for completed Developer sessions; raw session summary only when BLOCKED/PARTIAL, verdict flags issues, or need exact Follow-Up Items/Learnings. Non-Developer sessions: read session summary directly.
- Remove any references to removed session summary fields in dispatch or state-reading instructions.

**`preambles/ARCHITECT.md`**
- Add Interface Scope Decomposition section:
  - Tag each task with Interface Scope (see §2.6).
  - CONTRACT_ONLY task first for contract changes.
  - Separate PRODUCER and CONSUMER tasks.
  - Trivial exception rule.
  - Include contract integrity skill file in Context files.
- Add `Interface Scope` to the list of required task tags alongside `QA Required` and `State Behavior`.

**`preambles/RESEARCHER.md`** — No changes expected unless it references removed session summary fields.

**`preambles/QA_TESTER.md`** — No changes expected unless it references removed session summary fields.

### Templates

**`templates/session-summary.md`**
- Replace with root master template. Key differences from v1.7:
  - YAML frontmatter (slim: `status`, `project_root`) instead of blockquote metadata.
  - Removed: `Revision Of`, `Supersedes`, `Superseded By` metadata fields.
  - Removed: `Artifacts Superseded`, `Routing Recommendation`, `Exit Checklist`, `Self-Assessment` sections.
  - Retained: `Artifacts Produced`, `Interfaces Added or Modified`, `Follow-Up Items`.

**`templates/validator-verdict.md`**
- Replace with root master template. Key differences from v1.7:
  - YAML frontmatter (slim: `status`, `project_root`) instead of blockquote with 5 fields.
  - Added: `## Compliance Check` section.
  - Added: `## Supersession` section.
  - Expanded: `## Recommended Next Step` with `Dispatch mode` subfield.

**`templates/handoff-packet.md`**
- Replace with root master template. Key change: YAML frontmatter (full 5 fields) instead of blockquote.

**`templates/tasks.md`**
- Replace with root master template. Key changes:
  - YAML frontmatter (full 5 fields) instead of blockquote.
  - Added `Interface Scope` field to each task.

**All other templates** (spec, plan, orchestrator-state, test-scenarios, qa-verdict, research-request, research-findings):
- If they use blockquote metadata (`> Status: ...`), switch to YAML frontmatter. Use full 5-field for planning artifacts, slim 2-field for verdicts/summaries.

### New File

**`skills/contract-integrity.md`**
Create a contract integrity skill file skeleton for SCUE's stack:

```markdown
# Contract Integrity — SCUE

## When This Applies
Load this skill when your task is tagged with `Interface Scope: PRODUCER` or `CONSUMER`.

## Stack Context
- **Backend:** Python dataclasses, FastAPI endpoints, WebSocket message handlers
- **Frontend:** TypeScript interfaces in `frontend/src/types/`, Zustand stores, WebSocket message consumers
- **Contract files:** `docs/CONTRACTS.md`, `docs/interfaces.md`, type definitions in both layers

## Field Preservation Checklist
Before declaring COMPLETE on a PRODUCER or CONSUMER task:
1. Open the field inventory from the CONTRACT_ONLY task (or `docs/interfaces.md`).
2. For each field in the inventory:
   - PRODUCER: verify your code emits this field with the correct name, type, and required/optional status.
   - CONSUMER: verify your code reads and uses this field. Check default handling for optional fields.
3. If you added or removed a field not in the inventory, STOP — flag `[INTERFACE IMPACT]`.

## Common Patterns
- WebSocket payloads: Python dataclass → `asdict()` → JSON → TypeScript type. Field names must match exactly (Python snake_case converted at serialization boundary).
- REST responses: FastAPI Pydantic model → JSON → TypeScript type.
- Zustand stores consume WebSocket messages — check store update handlers match payload shape.

## Known Gotchas
- [TODO: Fill from project experience — e.g., fields that were silently dropped in past sessions]
- Python `Optional[T]` fields default to `None` but TypeScript `T | undefined` behaves differently at runtime.
- `asdict()` on nested dataclasses produces nested dicts, not flat — consumer must handle nesting.

## Anti-Patterns
- Changing a dataclass field without updating the corresponding TypeScript type (or vice versa).
- Adding a field to the producer without updating test fixtures in `tests/fixtures/`.
- Assuming a field rename in one layer will be caught by type checking in the other layer (cross-language boundary is not type-checked).
```

### AGENT_BOOTSTRAP.md

- Review for any references to removed session summary fields or blockquote metadata format. Update if found.
- Ensure layout summary includes `skills/contract-integrity.md` if it lists skill files.

### Startup Prompts

- Review `docs/agents/startup-prompts/` for any references to removed session summary fields or blockquote metadata. Update loading sequences if any template references changed.

### Protocol Improvements

Clear the two resolved BUG entries from `docs/agents/PROTOCOL_IMPROVEMENT.md`:
- "Developer skipped session summary despite clear preamble instructions" — resolved by v1.8 simplified exit sequence (3 steps) and responsibility split (Validator owns compliance, hook owns existence).
- "Architect skipped handoff packets and test scenarios despite clear preamble instructions" — resolved by v1.8 simplified exit sequence and the principle that compliance verification is the Validator's job, not self-reported checklists.

Add a resolved note at the bottom:
```
<!-- Resolved 2026-03-19 (v1.8): Developer/Architect artifact-skipping BUGs resolved by -->
<!-- session summary responsibility split: producer owns factual recap (simplified exit -->
<!-- sequence), Validator owns compliance check, hook owns existence gate. -->
```

---

## Process

1. Read the current SCUE preambles, templates, startup prompts, and `AGENT_BOOTSTRAP.md`.
2. Compare against the updated root protocol (v1.8) and root master templates.
3. Update each file per the instructions above.
4. Preserve SCUE-specific rules (layer boundary rules, CONTRACTS.md references, SCUE design system references, etc.). Do not flatten project-specific guidance into generic boilerplate.
5. Create `skills/contract-integrity.md`.
6. Clear resolved entries from `docs/agents/PROTOCOL_IMPROVEMENT.md`.
7. Produce a migration checklist as your final output.

## Output Format

For each file:
```markdown
### File: [path/filename.md]
**Action:** CREATE | UPDATE
**Rationale:** [why this change is needed]

[full file content]
```

End with:
```markdown
## Migration Checklist
- [ ] files created: [list]
- [ ] files updated: [list]
- [ ] files superseded: [list or "none"]
- [ ] unresolved decisions: [list or "none"]
- [ ] manual follow-up: [list or "none"]
```

## Constraints

- Do not modify application source code.
- Do not delete valid SCUE-specific documentation; preserve and integrate.
- Match `OPERATOR_PROTOCOL.md` v1.8 exactly where the protocol is explicit.
- Prefer root master templates over re-inventing project-local variants.
- Keep preambles dense and operational.
