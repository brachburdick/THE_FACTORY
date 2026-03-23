---
status: [FILL: COMPLETE]
project_root: [FILL: /absolute/path/to/project]
revision_of: [FILL: artifact path or "none"]
supersedes: [FILL: artifact path(s) or "none"]
superseded_by: [FILL: artifact path(s) or "none"]
---

# QA Verdict: [FILL: TASK_ID or BUG_ID]

## Verdict: [FILL: PASS | FAIL]

## Environment
- Server: [FILL: how started, flags, or "n/a"]
- Hardware: [FILL: device/mock setup, or "n/a"]
- Browser: [FILL: browser/version, or "n/a"]

## Scenarios Executed
| Scenario | Status | Notes |
|----------|--------|-------|
| [FILL: SC-001] | [FILL: PASS | FAIL | NOT_TESTED | REQUIRES_OPERATOR] | [FILL: brief note] |

## Failures
### [FILL: SC-002 or "None"]
- **Expected:** [FILL: expected behavior]
- **Observed:** [FILL: actual behavior]
- **Logs:** [FILL: minimum useful excerpts or "none"]
- **Severity:** [FILL: BLOCKING | DEGRADED | COSMETIC]

## Regression Check
- Previously passing scenarios still pass: [FILL: YES | NO — list regressions]

## Mock Tool Gaps
- [FILL: missing mock capability, or "All executed scenarios had available tooling."]

## Recommendation
[FILL: specific guidance for the next handoff. Reference scenario IDs.]
