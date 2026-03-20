---
status: [FILL: DRAFT | APPROVED | SUPERSEDED]
project_root: [FILL: /absolute/path/to/project]
revision_of: [FILL: artifact path or "none"]
supersedes: [FILL: artifact path(s) or "none"]
superseded_by: [FILL: artifact path(s) or "none"]
pdr_ref: [FILL: path to Project Definition Record or "none"]
evidence_ref: [FILL: path to most recent Evidence Review Packet or "none"]
---

# Spec: [FILL: FEATURE_NAME]

## Frozen Intent
<!-- These fields are set by the operator and must not be changed by agents without operator approval. -->
<!-- Changes require citing the upstream PDR item or Evidence Review Packet that caused the change. -->

### Problem Statement
[FILL: what problem this feature solves, referencing PDR if available]

### Target Users
[FILL: who benefits from this feature]

### Desired Outcome
[FILL: what success looks like]

### Non-Goals
- [FILL: explicitly excluded work]

### Hard Constraints
- [FILL: non-negotiable rule]

### Quality Priorities
[FILL: rank of performance, correctness, polish for this feature]

## Mutable Specification
<!-- Agent-authored, timestamped. Changes must cite the upstream PDR item or Evidence Review Packet. -->

### Summary
[FILL: one-paragraph summary of the feature]

### User-Facing Behavior
[FILL: what the user experiences]

### Technical Requirements
- [FILL: requirement with acceptance criterion]
- [FILL: requirement with acceptance criterion]

### Interface Definitions
[FILL: exact types, signatures, or contracts. Copy-pasteable, not prose.]

```typescript
// Replace with actual interface definitions.
```

### Layer Boundaries
- **[FILL: Layer X]** is responsible for: [FILL: scope]
- **[FILL: Layer Y]** is responsible for: [FILL: scope]
- Interface between them: [FILL: exact boundary or reference]

### Edge Cases
- [FILL: edge case]: [FILL: expected behavior]

### Open Questions
- `[DECISION NEEDED]`: [FILL: question]
- [FILL: or "None"]

### Change Log
<!-- When spec changes during implementation, record the change and its upstream cause. -->
<!-- Format: [DATE] [CHANGE] — caused by [PDR item / Evidence Review Packet / operator decision] -->
