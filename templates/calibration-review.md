# Calibration Review Template

> Quarterly review pulling assess.py stats, comparing actual distributions
> to thresholds, outputting tighten/loosen/keep recommendations.

## Review Period

- **Quarter:** Q_ 20__
- **Sessions reviewed:** __ (from assess.py `--last N`)
- **Date:** ____-__-__

## Data Sources

Run these before filling in the template:

```bash
# Session statistics
.venv/bin/python scripts/assess.py --last 50

# Flakiness analysis (if tracked)
.venv/bin/python -c "
from scripts.assess import analyze_flakiness
analyze_flakiness()
"
```

## Threshold Review

For each metric, compare the actual distribution to the current threshold.
Recommend: **tighten** (threshold too generous), **loosen** (threshold too strict,
causing false blocks), or **keep** (threshold is well-calibrated).

### Fix-Attempt Budget

| Metric | Current Threshold | Actual (p50 / p90 / max) | Recommendation |
|---|---|---|---|
| Low-risk mutations/phase | 15 | __ / __ / __ | keep / tighten / loosen |
| Medium-risk mutations/phase | 7 | __ / __ / __ | keep / tighten / loosen |
| High-risk mutations/phase | 4 | __ / __ / __ | keep / tighten / loosen |
| Fix-attempt cap (consecutive edits) | 2 | __ / __ / __ | keep / tighten / loosen |

**Notes:**

### PR Size

| Metric | Current Threshold | Actual (p50 / p90 / max) | Recommendation |
|---|---|---|---|
| Net LOC per commit | 200 (warning) | __ / __ / __ | keep / tighten / loosen |

**Notes:**

### Eval Flakiness

| Metric | Current Threshold | Actual | Recommendation |
|---|---|---|---|
| Flaky candidate rate | >10% fail over 20+ runs | __ tests flagged | keep / tighten / loosen |

**Notes:**

### Session Scope

| Metric | Current Guidance | Actual (p50 / p90) | Recommendation |
|---|---|---|---|
| Objectives per session | 1-2 (guidance) | __ / __ | keep / tighten / loosen |

**Notes:**

## Outcome Distribution

From run records:

| Result | Count | % | Trend vs. Last Quarter |
|---|---|---|---|
| success | | | |
| partial | | | |
| failed | | | |
| blocked | | | |
| escalated | | | |

## Oversight Level Distribution

| Level | Count | % | Notes |
|---|---|---|---|
| autonomous | | | |
| checkpoint | | | |
| supervised | | | |

## Escalation Analysis

- **Total escalations:** __
- **Most common trigger:** __
- **Escalations that led to operator intervention:** __
- **Escalations that were false alarms:** __

## Recommendations

### Thresholds to Update

Write changes to `.agent/thresholds.json`:

```json
{
  "fix_attempt_cap": 2,
  "compound_budget": { "low": 15, "medium": 7, "high": 4 },
  "pr_size_warning_loc": 200,
  "flakiness_threshold_pct": 10,
  "flakiness_min_runs": 20,
  "session_scope_max_objectives": 2,
  "updated": "____-__-__",
  "review_quarter": "Q_ 20__"
}
```

### Process Changes

_List any process improvements identified during review._

### New Eval Cases

_List any failure patterns that should become eval test cases._

## Sign-off

- Reviewed by: __
- Date: __
