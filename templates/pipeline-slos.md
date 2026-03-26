# Pipeline SLOs

> Service Level Objectives for THE_FACTORY pipeline. Measured from `.agent/runs.jsonl`
> data. Review quarterly via calibration loop (tf-064).

## Metrics

| Metric | Definition | Source Field | Target | Measurement Window |
|--------|-----------|--------------|--------|-------------------|
| **Completion Rate** | % of runs with `result: "success"` | `result` | ≥ 80% | Rolling 20 runs |
| **Rework Rate** | % of tasks that appear in 2+ runs (re-opened or re-attempted) | `task_id` count | ≤ 15% | Rolling 20 runs |
| **Escalation Rate** | % of runs with `result: "blocked"` (operator had to intervene) | `result` | ≤ 20% | Rolling 20 runs |
| **Test-Gate Failure Rate** | % of runs where `evals_failed > 0` at close | `evals_failed` | ≤ 5% | Rolling 20 runs |
| **Operator Review Latency** | Median `time_to_operator_response` across runs (tf-053) | `time_to_operator_response` | Measure first, SLO after 20+ data points | Rolling 20 runs |

## Status

These SLOs are **targets, not enforcements**. The outer loop (assess.py) reports actuals
vs. targets. Enforcement happens only after sufficient data confirms the targets are
achievable and the right thresholds.

### Maturity Levels

1. **Measure** — Collect data, report in assess.py (current state)
2. **Alert** — Flag when metric drifts >2σ from rolling average
3. **Enforce** — Block or gate when metric crosses threshold

All metrics start at Level 1. Promotion to Level 2/3 requires operator approval via
calibration review.

## How to Read

Run `python scripts/assess.py --last 20` to see current values against these targets.
The `--out` flag produces a JSON report suitable for CI dashboards.

## Calibration

Targets should be reviewed every 20-30 sessions or quarterly (whichever comes first).
Use the calibration review template (tf-064, when available) to compare actuals against
targets and adjust thresholds.

Adjustments follow this protocol:
- **Tighten** if metric has been consistently better than target for 2+ review cycles
- **Loosen** if metric consistently misses target despite reasonable effort
- **Keep** if metric hovers near target (within 10% relative)
