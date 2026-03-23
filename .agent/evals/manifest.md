# Eval & Skill Version Manifest

> Tracks version lineage for prompts, skills, flows, and templates.
> Updated during protocol reviews and material workflow changes.

## Current Versions

| Artifact | Version | Date | Change Summary |
|----------|---------|------|----------------|
| CLAUDE.md (constitution) | v2.0.0 | 2026-03-23 | Slim trigger table (pipeline-only), hooks enforce, skills inform |
| debug-flow | v2.0.0 | 2026-03-23 | Separate-context verification, 3-attempt cap enforced by hook |
| feature-flow | v2.0.0 | 2026-03-23 | Phase 0 intent check, Phase 2.5 pre-implementation checklist |
| refactor-flow | v2.0.0 | 2026-03-23 | Snapshot phase, no-behavior-change rule |
| handoff-envelope.json (schema) | v1.1.0 | 2026-03-20 | replanTriggers, verificationProcedure, assumptionsInForce, dispatchStatus |
| templates/spec.md | v1.1.0 | 2026-03-20 | Frozen/mutable split |
| templates/plan.md | v1.1.0 | 2026-03-20 | YAML frontmatter |
| templates/handoff-packet.md | v1.1.0 | 2026-03-20 | Replan triggers, verification procedure |

## Eval Suite

**Canonical command:** `.venv/bin/python -m pytest evals/ -v`

| Test File | Tests | Category |
|-----------|-------|----------|
| test_conventions.py | 7 | SCUE code conventions (behind scue_available guard) |
| test_flows.py | 15 | Flow skill structure and routing |
| test_handoffs.py | 12 | Schema validation + required artifacts |
| test_mining.py | 11 | Regression checks from conversation mining |
| test_behavioral.py | 3 | Agent behavior from session transcripts |

Total: ~48 tests (some skipped when SCUE absent or run records empty).

The `.eval.md` spec files in subdirectories are reference documentation.
They describe expected behavior in Input/Expected/Fail-If format but are
not executed directly. The pytest suite in `evals/` is the executable implementation.

## Version Lineage

```
v1.8 (role-based) → v1.9 (skills + structured state) → v1.9.2 (observability)
→ v2.0 (hooks + evals + experiment framework)
```
