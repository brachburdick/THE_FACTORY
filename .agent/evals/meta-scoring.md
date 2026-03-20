# Meta-Infrastructure Scoring Rubric

Use this rubric to compare infrastructure versions. Score each dimension 1-5.

## Dimensions

### 1. Context Efficiency (weight: 3x)
How much of the context window is consumed by infrastructure before real work begins?
- 1: >30% of context consumed by infrastructure loading
- 3: 10-15% consumed, most loaded on demand
- 5: <5% consumed at startup, all additional context loaded per-task

### 2. Session Bootstrap Time (weight: 2x)
How long (in tokens/time) does it take an agent to become productive?
- 1: Agent must read >10 files before starting work
- 3: Agent reads 1-2 files, begins work within first response
- 5: Agent reads CLAUDE.md only, triggers skills as needed

### 3. Anti-Drift Mechanism Strength (weight: 3x)
How reliably are conventions enforced across sessions?
- 1: Conventions exist only as prose rules in docs
- 3: Some conventions have schema validation or tests
- 5: All critical conventions have executable evals + CI enforcement

### 4. Documentation Freshness (weight: 2x)
What fraction of documentation is current and actively used?
- 1: >50% of docs are stale, duplicated, or orphaned
- 3: Periodic cleanup, some stale docs persist
- 5: Keep/delete filter enforced, all docs justify their existence

### 5. Session Artifact Hygiene (weight: 2x)
How much cruft accumulates per completed milestone?
- 1: >5 session files per milestone, no cleanup policy
- 3: Session files created but triaged regularly
- 5: No session files created; state stored structurally, scratch discarded

### 6. Handoff Reliability (weight: 2x)
How often do handoffs between domains succeed without human intervention?
- 1: Handoffs are prose, frequently misinterpreted
- 3: Handoffs have templates, sometimes validated
- 5: Handoffs are schema-validated, rejected if malformed

### 7. Scalability (weight: 1x)
How well does the infrastructure handle adding a new project to the portfolio?
- 1: New project requires creating multiple new agent roles and templates
- 3: New project reuses most infrastructure with some customization
- 5: New project inherits meta-level skills and schema, needs only project CLAUDE.md

## Scoring

Weighted score = sum of (dimension score × weight) / sum of weights

Record scores for each version in VERSION.md for longitudinal tracking.
