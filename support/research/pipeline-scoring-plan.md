# Implementation Plan: Pipeline Scoring System

> **Date:** 2026-03-22
> **Type:** Architecture plan
> **Research basis:** `support/research/pipeline-scoring-research.md`
> **Scope:** THE_FACTORY root infrastructure (all projects benefit)

## Design Principles

1. **Build on what exists.** The run-record, incident-record, and scorecard schemas are defined.
   runs.jsonl has 10 entries. Extend, don't replace.
2. **Git is a first-class data source.** Phase-boundary commits are already protocol. Extract
   metrics from them rather than adding new tracking artifacts.
3. **Scripts over services.** Scoring runs as CLI scripts in `scripts/`, not a running process.
   Same pattern as `scripts/tasks.sh`.
4. **Thresholds come from data, not guesses.** The first 20 runs establish baselines. Thresholds
   are set at baseline + 1 standard deviation, not arbitrary values.

## Phase 1: Schema Completion (no code, just schema)

**Goal:** Ensure runs.jsonl records carry enough data to compute Tier 1 metrics.

### 1a. Add `flow_phases_completed` to run-record schema

The current schema has no field for tracking how far through a flow the task progressed.
The `result` field says pass/fail but not *where* it stopped.

```json
"flow_phases_completed": {
  "type": "array",
  "items": { "type": "string" },
  "description": "Flow phases completed (e.g., ['reproduce', 'isolate', 'diagnose', 'fix'])"
}
```

Add to `.agent/schemas/run-record.json` as optional field. Existing records remain valid.

### 1b. Add `branch_name` to run-record schema

Links the run to its git branch for commit-level analysis.

```json
"branch_name": {
  "type": "string",
  "description": "Git branch name (e.g., fix/TASK-042-waveform-offset)"
}
```

### 1c. Add `files_changed` count to run-record schema

Avoids needing to reconstruct from git for basic breadth analysis.

```json
"files_changed": {
  "type": "integer",
  "minimum": 0,
  "description": "Number of files changed in this run"
}
```

### 1d. Start populating optional fields

The run-record schema already has `estimated_cost`, `input_tokens`, `output_tokens`,
`tool_calls`, `latency_ms`. These are currently never populated. The session protocol's
"land the plane" step should estimate these when possible. Claude Code's `/cost` output
provides the data.

**Constitution change:** Update the session protocol "land the plane" step to say:
> Include optional fields (`input_tokens`, `output_tokens`, `tool_calls`, `latency_ms`,
> `estimated_cost`, `flow_phases_completed`, `branch_name`, `files_changed`) when you
> can measure or estimate them.

**No new schemas.** No new files. Three optional fields added to an existing schema.

---

## Phase 2: Git Metrics Script

**Goal:** A script that reads git log and computes code-churn and commit-quality metrics.

### 2a. `scripts/git-metrics.sh`

Accepts a branch name (or date range) and outputs:

```
Branch: fix/TASK-042-waveform-offset
Commits: 4
Files changed: 7
Directories touched: 3
Layer cohesion: 0.86 (6/7 files in same layer)
Avg lines per commit: 45
```

Implementation: `git log --numstat` parsed with awk. Layer detection by path prefix
(`scue/bridge/` = layer0, `scue/layer1/` = layer1, `frontend/` = frontend, etc.).

### 2b. `scripts/churn-rate.sh`

Computes 14-day churn rate across the repo (or a project subdirectory):

```
Period: 2026-03-08 to 2026-03-22
Lines authored: 1,247
Lines churned (rewritten within 14 days): 89
Churn rate: 7.1%
```

Implementation: For each line changed in the period, check if the same file+region was
modified again within 14 days. This is an approximation — full GitClear-style analysis
requires per-line tracking. A simpler proxy: count files that appear in commits more than
14 days apart within the window.

**Simpler v1 proxy:** Count commits that touch the same file within 14 days and report
the ratio. This is less precise than line-level churn but computable with basic git commands
and captures the signal (files being reworked quickly).

---

## Phase 3: Pipeline Scorecard Script

**Goal:** A script that reads runs.jsonl + incidents.jsonl and produces a scorecard.

### 3a. `scripts/pipeline-scorecard.sh`

Reads JSONL files, computes metrics, outputs a summary:

```
Pipeline Scorecard (2026-03-20 to 2026-03-22)
═══════════════════════════════════════════════
Runs: 10
  success: 10 (100%)    partial: 0    failed: 0    blocked: 0

By task type:
  feature: 7 (100% success, 1.0 avg attempts)
  debug:   3 (100% success, 1.0 avg attempts)

Rework rate: 0% (0/10)
Incident rate: 0 incidents / 10 runs

Milestone completion: N/A (flow_phases_completed not yet populated)
Cost efficiency: N/A (estimated_cost not yet populated)

Baseline status: 10/20 runs collected. 10 more needed before thresholds.
```

Implementation: `jq` queries against the JSONL files. No dependencies beyond jq.

### 3b. Baseline establishment

After 20 runs, the script computes baseline values and writes them to
`.agent/baselines.json`:

```json
{
  "established_date": "2026-04-XX",
  "run_count": 20,
  "metrics": {
    "success_rate": { "value": 0.90, "stddev": 0.05 },
    "avg_attempt_count": { "value": 1.3, "stddev": 0.4 },
    "rework_rate": { "value": 0.10, "stddev": 0.06 },
    "incident_rate": { "value": 0.05, "stddev": 0.03 }
  }
}
```

Thresholds are then: baseline value ± 1 stddev. A scorecard run that exceeds a threshold
gets flagged.

---

## Phase 4: Integration into Session Protocol

**Goal:** Scoring becomes part of the natural workflow, not an afterthought.

### 4a. Protocol review trigger

Add to the protocol review cycle: before reviewing protocol changes, run
`scripts/pipeline-scorecard.sh` to ground discussion in data. This replaces the current
pattern of reviewing PROTOCOL_IMPROVEMENTS.md entries without quantitative evidence.

### 4b. Eval case for run-record completeness

Add an eval case in `.agent/evals/conventions/` that validates:
- Every run record has the required fields per schema
- Optional fields are populated at increasing rates over time
- `flow_phases_completed` is present on runs after Phase 1 is implemented

### 4c. Scorecard in "land the plane"

After baseline is established, the session-end protocol can optionally run
`scripts/pipeline-scorecard.sh` and flag if any metric has crossed a threshold since
last scorecard. This is informational — it doesn't block work.

---

## Phase 5: Git + Telemetry Correlation (Future)

**Goal:** Link run records to git branches for combined analysis.

### 5a. `scripts/run-git-report.sh`

Given a run_id, pulls the branch_name from runs.jsonl, runs git-metrics against that
branch, and produces a combined report:

```
Run: run-2026-03-21-001
Task: FE-LIVE-DECK-PIONEER-WF
Type: feature
Result: success
Attempts: 1
Phases: [spec, implement, test, qa]

Git metrics:
  Branch: feature/pioneer-waveform-fallback
  Commits: 6
  Files: 12
  Layer cohesion: 0.75
  Churn (14d): 0%

Assessment: Clean single-attempt feature. Moderate file breadth (12 files across
3 directories). Layer cohesion slightly below target — review if cross-layer
changes were necessary.
```

### 5b. Incident-to-commit correlation

When an incident is filed, the `task_id` links to a run, which links to a branch.
`scripts/run-git-report.sh` can show the specific commits that produced the incident,
enabling root-cause analysis at the commit level.

---

## What NOT to Build

- **No dashboard.** Scripts output to stdout. Pipe to a file if you want history.
- **No database.** JSONL + jq is sufficient for the data volume (~50-100 runs/month).
- **No real-time monitoring.** Scoring runs on-demand or at session boundaries.
- **No NLP/embedding analysis.** Description-to-diff alignment (Tier 3) is deferred
  until Tier 1 and 2 prove useful.
- **No OTel integration.** The research shows OTel conventions are stabilizing but
  not yet mature enough to adopt. Revisit when v1.0 of GenAI semantic conventions ships.

## Implementation Order

| Phase | Effort | Prerequisite | Deliverable |
|---|---|---|---|
| 1: Schema completion | ~30 min | None | Updated run-record.json, constitution tweak |
| 2: Git metrics script | ~2 hours | None (independent of Phase 1) | `scripts/git-metrics.sh`, `scripts/churn-rate.sh` |
| 3: Pipeline scorecard | ~2 hours | Phase 1 (for schema), 10+ runs (for data) | `scripts/pipeline-scorecard.sh` |
| 4: Protocol integration | ~30 min | Phase 3 + 20 runs (for baselines) | Eval case, protocol review update |
| 5: Correlation reports | ~2 hours | Phase 1 + Phase 2 + Phase 3 | `scripts/run-git-report.sh` |

Phases 1 and 2 can be done in parallel. Phase 3 depends on Phase 1. Phase 4 depends on
data accumulation (20 runs). Phase 5 is optional until correlation analysis proves needed.

## Relationship to WFC-001

WFC-001 (Lightweight Workflow Controller) lists "baseline metrics" as prerequisite #3.
This plan produces those baselines. Specifically:

- Phase 3 scorecard provides the "operator-minutes-per-task" baseline WFC-001 needs
- Phase 4 threshold detection tells you when the controller's value is measurable
- The decision gate (">20% of session time on mechanical routing → implement") can be
  informed by the friction scores in scorecards.jsonl once those are being populated

**Recommended sequence:** Complete Phases 1-3 of this plan → collect 20 runs →
establish baselines → then evaluate WFC-001 with real data.
