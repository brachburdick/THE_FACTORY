# Eval: handoff-schema-valid

## Should: Produce valid JSON matching the handoff envelope schema
- Input: "Hand off the bridge analysis work to the frontend skill"
- Expected: JSON object with all required fields (schemaVersion, sourceAgent, targetSkill, summary, artifacts, taskRef)
- Fail if: Missing required fields, extra fields (additionalProperties: false), summary >500 chars

## Should NOT: Use markdown handoff format
- Input: "Create a handoff for the next phase of work"
- Expected: JSON envelope, not markdown template
- Fail if: Produces markdown handoff packet instead of JSON

## Should: Include taskRef pointing to task tracker
- Input: "Hand off task-003 to the frontend skill"
- Expected: `taskRef` field contains "task-003" matching an entry in .agent/tasks.jsonl
- Fail if: taskRef is empty, missing, or doesn't correspond to a tracked task
