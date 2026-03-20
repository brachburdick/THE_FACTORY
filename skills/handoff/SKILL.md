---
name: handoff
description: Use when handing off work across a genuine domain boundary (e.g., audio analysis → DMX output, backend → frontend integration). Loads the JSON Schema envelope and validation script.
---

# Handoff Skill

## When to Use
- Crossing a genuine domain boundary (not sequential tasks in the same domain)
- Transitioning work that requires different skill context to complete
- Handing off from research/design to implementation in a different tech stack

## Handoff Envelope
All handoffs use the JSON Schema at `.agent/schemas/handoff-envelope.json`.

Required fields:
- `schemaVersion`: "1.0.0"
- `sourceAgent`: who is handing off
- `targetSkill`: which skill the receiving context should load
- `summary`: ≤500 chars describing what was done and what's needed next
- `artifacts`: list of file paths produced
- `taskRef`: ID in `.agent/tasks.jsonl`

Optional fields:
- `openQuestions`: unresolved questions for the receiver
- `blockers`: known blockers

## Validation
Before delivering a handoff, validate against the schema:
```bash
scripts/validate-handoff.sh <handoff.json>
```

Reject malformed handoffs. Do not deliver them to the receiving context.

## Anti-Patterns
- Using handoffs for sequential tasks in the same domain (just keep working)
- Omitting `taskRef` (makes the handoff untraceable)
- Writing prose handoffs instead of JSON (not schema-validated)
