# Oversight Matrix

**Simplified 2026-03-26** (was 3×3, now 2-tier)

## Two Tiers

| Tier | When | What Happens |
|---|---|---|
| **Routine** | Low-risk task, known pattern, clear criteria | Proceed without checkpoints. Post-hoc review via run record. |
| **Gated** | Everything else (features, bugs, refactors, unknowns) | Pause at phase gates for operator confirmation. High-risk tasks require approved plan. |

## How Risk Is Determined

Set explicitly on the task (`risk` field in tasks.jsonl) or inferred by the risk-classifier hook:

- **Low** → Routine: tests, docs, config, lint, typo, frontmatter, license, readme
- **Medium** → Gated: features, bug fixes, refactors (default)
- **High** → Gated + plan required: security, migration, schema, auth, credentials, cross-section

## What Hooks Enforce

| Hook | Routine | Gated | Type |
|---|---|---|---|
| fix-attempt-tracker | Active (budget=10) | Active (budget=10) | Blocking |
| risk-classifier | Skip | Allow (medium) / Block without plan (high) | Blocking |
| blast-radius | Active | Active | Blocking |
| plan-gate | Skip | Active for high-risk | Blocking |
| reference-check | Active | Active | Advisory (warns on rename→eval conflicts) |
| build-integrity | Active | Active | Advisory (warns on infra file edits) |
| git-guard | Active | Active | Blocking |
| audit-run-record | Active | Active | Advisory (warns if no run record) |

Compound budget is **10 mutations** regardless of risk. Circuit breaker thresholds: **4 edit-test cycles**, **10 unique files**. These are universal — if you hit them, something is wrong regardless of risk level.

## Escalation Triggers

| Trigger | Effect |
|---|---|
| 2+ fix attempts exhausted | Pause, run tests |
| Files outside owned_paths | Blocked by blast-radius |
| No acceptance criteria | Flag to operator before proceeding |
| Prior incident on same component | Flag to operator |

## Metrics

Track in run records: `operator_interventions`, `agent_escalations`, `result`.
Feed into `assess.py` for trend analysis.

State snapshot now captures `baseline_test_failures` — list of failing tests at session end, so the next session knows which failures are pre-existing vs. newly introduced.
