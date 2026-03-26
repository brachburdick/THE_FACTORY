# Risk-Tiered Oversight Matrix

**Task:** tf-048
**Date:** 2026-03-27
**Status:** Active — referenced from CLAUDE.md Oversight Policy section

## Purpose

Replace blanket human gates with selective oversight based on three
dimensions: risk, evidence, and ambiguity. The goal is maximum autonomy
for safe, well-evidenced work, with progressively tighter gates as
uncertainty increases.

## Dimensions

### Risk Level

Set explicitly on the task (`risk` field in tasks.jsonl) or inferred by
the risk-classifier hook.

| Level | Signals | Examples |
|---|---|---|
| Low | tests, docs, config, lint, typo, frontmatter | Add docstring, fix typo, update README |
| Medium | (default) features, bug fixes, refactors | Add endpoint, fix race condition, extract module |
| High | security, migration, schema, auth, credentials, cross-section, destructive | DB migration, auth flow change, cross-service refactor |

### Evidence Level

Assessed at pre-flight (Phase 1.5/2.5 of flow skills).

| Level | Signals |
|---|---|
| Low | Tests pass, pattern is well-known, prior success on same component |
| Medium | Tests exist but coverage is partial, first attempt at this pattern |
| High | No tests, novel pattern, prior failures or incidents on this component |

### Ambiguity Level

Assessed at intent/spec phase (Phase 0/1 of flow skills).

| Level | Signals |
|---|---|
| Low | Clear spec, explicit acceptance criteria, no open questions |
| Medium | Some open questions, criteria exist but could be more specific |
| High | Vague goals ("improve", "optimize", "clean up"), no quantified criteria |

## The Matrix

The oversight level is determined by the **highest** dimension:

```
Risk:      Low    Medium   High
Evidence:  Low    Medium   High
Ambiguity: Low    Medium   High
                                → max(all three) = oversight level
```

### Autonomous (all dimensions low)

- **Proceed without checkpoints.** Post-hoc review via run record only.
- Fix-attempt tracker still active (safety net).
- Blast-radius hook still active (scope enforcement).
- Example: fixing a typo in a test file, adding a docstring, updating config.

### Checkpoint (any medium, none high)

- **Proceed, but pause at phase gates** for operator confirmation.
- Plan-gate active: operator sees plan before implementation starts.
- Spec approval required before Phase 3 (feature-flow).
- Run record includes `operator_interventions` count.
- Example: adding a new API endpoint with clear spec, fixing a bug with
  partial test coverage.

### Supervised (any high)

- **Require approved plan** before ANY source mutations.
- Risk-classifier hook blocks edits without plan file.
- Incident logging mandatory on any deviation from plan.
- Compound budget tightened (4 mutations before checkpoint).
- Example: database migration, auth flow change, cross-section refactor,
  task with no acceptance criteria.

## Escalation Triggers

These force oversight upward regardless of the initial risk assessment:

| Trigger | Effect |
|---|---|
| 2+ fix attempts exhausted | → Supervised |
| Files outside owned_paths | → Supervised |
| Ambiguous acceptance criteria detected | → Checkpoint minimum |
| Prior incident on same component | → One level up |
| Cross-section file changes | → Supervised |
| Operator correction during session | → One level up for remainder |

## De-escalation

These allow oversight to decrease with evidence:

| Evidence | Effect |
|---|---|
| Approved plan exists | High-risk can proceed as Checkpoint |
| 3+ consecutive successes on same component | Eligible for Autonomous |
| All tests pass after fix | Fix-attempt counter resets |
| Operator explicitly sets `risk: low` | Overrides inference |

## Integration with Hooks

| Hook | Autonomous | Checkpoint | Supervised |
|---|---|---|---|
| fix-attempt-tracker | Active (budget=15) | Active (budget=7) | Active (budget=4) |
| risk-classifier | Skip (low) | Allow (medium) | Block without plan (high) |
| blast-radius | Active | Active | Active |
| plan-gate | Skip | Active | Active + mandatory |

## Integration with Flow Skills

Flow skills reference the oversight level at two points:

1. **Pre-flight readiness check** — assess risk, evidence, ambiguity.
   Set oversight level. If any dimension is high, escalate before proceeding.

2. **Phase gates** — checkpoint and supervised levels pause for operator.
   Autonomous level proceeds through gates without pausing.

The `failure_policy` field in skill frontmatter defines what happens when
the oversight level is violated (e.g., supervised task attempts ungated edit).

## Metrics

Track these in run records to inform future threshold tuning:

- `oversight_level`: autonomous | checkpoint | supervised
- `escalation_triggers`: list of triggers that fired
- `operator_interventions`: count
- `agent_escalations`: count
- `rework_count`: number of reverted-and-retried changes

Feed into `assess.py` trends for quarterly calibration reviews (tf-064).
