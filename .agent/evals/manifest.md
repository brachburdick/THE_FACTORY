# Eval & Skill Version Manifest

> Tracks version lineage for prompts, skills, flows, and templates.
> Updated during protocol reviews and material workflow changes.

## Current Versions

| Artifact | Version | Date | Change Summary |
|----------|---------|------|----------------|
| CLAUDE.md (constitution) | v2.1.1 | 2026-03-24 | Section-review trigger, eval count ~72 |
| debug-flow | v2.1.0 | 2026-03-24 | 2-attempt cap (was 3), diagnostic-before-visual rule |
| feature-flow | v2.1.0 | 2026-03-24 | 2-attempt retry cap (was 3) |
| refactor-flow | v2.1.0 | 2026-03-24 | 2-attempt retry cap (was 3) |
| section-review | v1.0.0 | 2026-03-24 | Three-pass review: section → boundary → integration |
| fix-attempt-tracker.sh | v2.1.0 | 2026-03-24 | Covers Edit+Write, resets on test run, 8 direct hook tests |
| audit-run-record.sh | v2.1.0 | 2026-03-24 | Cross-references tasks vs runs (replaced mtime heuristic) |
| handoff-envelope.json (schema) | v1.1.0 | 2026-03-20 | replanTriggers, verificationProcedure, assumptionsInForce, dispatchStatus |
| templates/spec.md | v1.1.0 | 2026-03-20 | Frozen/mutable split |
| templates/plan.md | v1.1.0 | 2026-03-20 | YAML frontmatter |
| templates/section-contract.md | v1.0.0 | 2026-03-24 | 1-page section contract template |
| templates/handoff-packet.md | v1.1.0 | 2026-03-20 | Replan triggers, verification procedure |
| SYNTROPY.md | v1.0.0 | 2026-03-24 | 8 principles distilled from 26-file research archive |

## Eval Suite

**Canonical command:** `.venv/bin/python -m pytest evals/ -v`

| Test File | Tests | Category |
|-----------|-------|----------|
| test_conventions.py | 15 | Code conventions + section boundary enforcement + file coverage |
| test_flows.py | 26 | Flow skill structure, routing, and hook tests (8 direct hook tests) |
| test_handoffs.py | 16 | Schema validation, required artifacts, task closure completeness |
| test_mining.py | 11 | Regression checks from conversation mining |
| test_behavioral.py | 4 | Agent behavior from session transcripts (diagnostic-before-visual) |

Total: ~72 tests (some skipped when SCUE absent, transcripts empty, or run records empty).

The `.eval.md` spec files in subdirectories are reference documentation.
They describe expected behavior in Input/Expected/Fail-If format but are
not executed directly. The pytest suite in `evals/` is the executable implementation.

## Version Lineage

```
v1.8 (role-based) → v1.9 (skills + structured state) → v1.9.2 (observability)
→ v2.0 (hooks + evals + experiment framework) → v2.1 (policy alignment + enforcement hardening + section review)
```
