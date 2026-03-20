---
status: [FILL: DRAFT | APPROVED | SUPERSEDED]
project_root: [FILL: /absolute/path/to/project]
revision_of: [FILL: artifact path or "none"]
supersedes: [FILL: artifact path(s) or "none"]
superseded_by: [FILL: artifact path(s) or "none"]
---

# Tasks: [FILL: FEATURE_NAME]

## Dependency Graph
[FILL: task ordering and parallel waves]

## Tasks

### TASK-001: [FILL: short descriptive name]
- **Layer:** [FILL: architectural layer]
- **Estimated effort:** [FILL: under 30 minutes if properly atomized]
- **Depends on:** [FILL: TASK-ID or "none"]
- **Scope:** [FILL: files or modules touched]
- **Inputs:** [FILL: what must already exist]
- **Outputs:** [FILL: what must exist after completion]
- **Interface Scope:** [FILL: CONTRACT_ONLY | PRODUCER | CONSUMER | END_TO_END | NONE]
- **QA Required:** [FILL: YES | NO — with reason]
- **State Behavior:** [FILL: linked artifact | [INLINE — simple] | [REQUIRES DESIGNER]]
- **Acceptance Criteria:**
  - [ ] [FILL: testable condition]
  - [ ] [FILL: testable condition]
  - [ ] [FILL: if interface values change, update `docs/interfaces.md` in the same session or flag `[INTERFACE IMPACT]` and stop]
  - [ ] All pre-existing tests pass
- **Context files:** [FILL: paths the implementing agent must read]
- **Status:** [ ] Not started / [x] Complete / [~] Partial / [!] Blocked
