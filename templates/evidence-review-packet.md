---
status: [FILL: DRAFT | FINAL]
project_root: [FILL: /absolute/path/to/project]
pdr_ref: [FILL: path to Project Definition Record]
review_trigger: [FILL: prototype | first_e2e_slice | operator_discomfort | architectural_surprise | repeated_failures | batch_uncertainty | pre_batch_commit]
date: [FILL: YYYY-MM-DD]
---

# Evidence Review Packet: [FILL: SHORT_TITLE]

## What Changed Since Last Review
- [FILL: Completed tasks, artifacts produced, decisions made]

## Evidence Observed
- [FILL: What the team observed during execution — test results, performance data, user feedback, integration outcomes]

## Assumptions Invalidated
- [FILL: Assumptions from the PDR or previous packets that turned out to be wrong. Cite the original assumption.]

## Assumptions Strengthened
- [FILL: Assumptions that gained supporting evidence. Cite the evidence.]

## New Questions Surfaced
- [FILL: Questions that emerged during execution and need operator input or further investigation]

## Proposed Changes
<!-- Changes to requirements, UX, architecture, or scope. Each must cite the evidence that motivates it. -->
- [FILL: Proposed change — evidence: [what was observed], impact: [what it affects]]

## Items Intentionally Deferred
- [FILL: Work or decisions explicitly pushed to a later phase, with reason]

## Next-Slice Recommendation
[FILL: What should be built or investigated next, and why]

## Dispatch Status

**[FILL: READY | READY WITH EXPLICIT ASSUMPTIONS | NOT READY]**

If `READY WITH EXPLICIT ASSUMPTIONS`:
- [FILL: List each assumption being accepted, its confidence level, and what would invalidate it]

If `NOT READY`:
- [FILL: What must be resolved before dispatch can proceed]
