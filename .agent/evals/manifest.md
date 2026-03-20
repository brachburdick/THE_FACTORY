# Eval & Skill Version Manifest

> Tracks version lineage for prompts, skills, flows, and templates.
> Updated during protocol reviews and material workflow changes.
> Referenced by run records to correlate outcomes with specific versions.

## Current Versions

| Artifact | Version | Date | Change Summary |
|----------|---------|------|----------------|
| CLAUDE.md (constitution) | v1.9.2 | 2026-03-20 | Task-type routing, flow skills, trigger table, observability, intent capture |
| OPERATOR_PROTOCOL.md | v1.9.2 | 2026-03-20 | Governance layer with observability, dispatch, review cadence, iteration caps |
| debug-flow | v1.1.0 | 2026-03-20 | Added negative constraints, verification subagent, incident logging, run records |
| feature-flow | v1.1.0 | 2026-03-20 | Added Phase 0 intent check, negative constraints, verification subagent, run records |
| refactor-flow | v1.1.0 | 2026-03-20 | Added negative constraints, verification subagent, run records |
| templates/spec.md | v1.1.0 | 2026-03-20 | Frozen/mutable split, PDR/evidence refs, change log |
| templates/handoff-packet.md | v1.1.0 | 2026-03-20 | Replan triggers, verification procedure, evidence, assumptions, dispatch status |
| templates/project-definition-record.md | v1.0.0 | 2026-03-20 | New: frozen core + mutable clarifications |
| templates/evidence-review-packet.md | v1.0.0 | 2026-03-20 | New: event-driven learning artifact |
| templates/orchestrator-state.md | v1.1.0 | 2026-03-20 | Added evidence packet ref, session digest, active assumptions |
| handoff-envelope.json (schema) | v1.1.0 | 2026-03-20 | Added replanTriggers, verificationProcedure, evidenceRequired, assumptionsInForce, dispatchStatus |
| run-record.json (schema) | v1.0.0 | 2026-03-20 | New: task execution telemetry |
| incident-record.json (schema) | v1.0.0 | 2026-03-20 | New: failure tracking with root-cause classification |
| scorecard-record.json (schema) | v1.0.0 | 2026-03-20 | New: experiential review scorecard |
| templates/plan.md | v1.1.0 | 2026-03-20 | YAML frontmatter, PDR/evidence refs, change log |
| templates/validator-verdict.md | v1.1.0 | 2026-03-20 | Frontmatter moved to top of file |

## Eval Cases

| Eval | Version | Tests |
|------|---------|-------|
| conventions/ | v1.9.0 | Frontmatter format, file naming, metadata rules |
| flows/ | v1.9.1 | Flow routing accuracy, gate compliance |
| handoffs/ | v1.9.0 | Handoff envelope validation |
| skills/ | v1.9.0 | Skill trigger accuracy |

## Version Lineage

```
v1.8 (role-based) → v1.9 (skills + structured state) → v1.9.1 (flow skills + routing) → v1.9.2 (observability + intent + dispatch)
```

## Variant Testing Log

<!-- When testing old-vs-new workflow variants, record results here. -->
<!-- Format: [DATE] [VARIANT] old: [version], new: [version], eval set: [name], result: [summary] -->
