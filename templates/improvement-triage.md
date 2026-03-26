# Improvement Triage Template

> Standard flow for processing improvement candidates from
> `.agent/improvement-candidates.jsonl`. Run after each calibration
> review or when the backlog exceeds 10 untriaged entries.

## Triage Decisions

For each candidate, assign one of:

| Decision | Meaning | Next Step |
|---|---|---|
| **accept** | Worth implementing | Create task in tasks.jsonl, require eval coverage |
| **defer** | Good idea, not now | Add rationale, revisit next quarter |
| **reject** | Not worth pursuing | Add rationale, close permanently |
| **superseded** | Covered by existing work | Link to superseding task ID |

## Candidate Schema

```json
{
  "id": "imp-001",
  "source": "session|assess|calibration|incident|operator",
  "date": "2026-03-27",
  "description": "Brief description of the improvement",
  "evidence": "What data supports this? (session count, failure rate, etc.)",
  "decision": "accept|defer|reject|superseded",
  "rationale": "Why this decision",
  "task_id": "tf-070 (if accepted)",
  "triaged_date": "2026-03-27"
}
```

## Triage Checklist

For each untriaged candidate (`decision` is null or missing):

1. **Read the evidence.** Is it quantified? If not, can you pull data from
   assess.py or run records to quantify it?

2. **Check for duplicates.** Search tasks.jsonl and other candidates for
   overlapping scope. If found, mark as `superseded`.

3. **Assess impact vs. effort.** Use the same scale as task sizing:
   - Small (< 1 session) + High impact → accept immediately
   - Large (3+ sessions) + Low impact → defer or reject
   - Medium + Medium → discuss with operator

4. **Require eval coverage.** Every accepted improvement that changes
   agent behavior MUST have a corresponding eval test. No eval = no accept.

5. **Set the decision.** Update the candidate entry with decision, rationale,
   and (if accepted) the new task ID.

## Protocol Review

When an accepted improvement changes a protocol (flow skill, hook behavior,
CLAUDE.md policy), follow this review process:

1. **Draft the change.** Write the protocol update as a diff or new section.
2. **Identify affected evals.** Which existing tests verify this behavior?
3. **Write new evals first.** Add tests that verify the new behavior BEFORE
   implementing the change.
4. **Apply the change.** Update the protocol.
5. **Run full eval suite.** All tests must pass, including new ones.
6. **Update calibration thresholds** if the change affects any metric in
   `.agent/thresholds.json`.

## Improvement Sources

| Source | How Candidates Arrive |
|---|---|
| Session analysis | assess.py flags patterns (high rework, repeated escalations) |
| Calibration review | Quarterly review identifies threshold mismatches |
| Incidents | `.agent/incidents.jsonl` entries with recurring root causes |
| Operator feedback | Direct input during or between sessions |
| Conversation mining | Patterns from indexed session transcripts |
