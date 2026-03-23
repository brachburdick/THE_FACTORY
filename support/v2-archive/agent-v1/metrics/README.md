# Pipeline Metrics

Four metric families tracked from structured data in `.agent/`.

---

## 1. Outcome Metrics

Source: `.agent/runs.jsonl`, `.agent/incidents.jsonl`

| Metric | Formula | Target |
|--------|---------|--------|
| First-pass success rate | (tasks with result=success on attempt 1) / (total tasks) | >70% |
| Escaped defect rate | (incidents with failure_type=escaped_defect) / (total completed tasks) | <5% |
| Rework rate | (tasks with rework_required=true) / (total completed tasks) | <15% |
| Validator false pass rate | (incidents with failure_type=false_pass) / (total validator passes) | <3% |
| Validator false fail rate | (incidents with failure_type=false_fail) / (total validator fails) | <5% |
| QA disagreement rate | (tasks where qa_result != validator_result) / (tasks with both) | <10% |
| Operator override rate | (tasks where operator overrode validator/qa verdict) / (total tasks) | Track only |

## 2. Efficiency Metrics

Source: `.agent/runs.jsonl`, `.agent/tasks.jsonl`

| Metric | Formula | Target |
|--------|---------|--------|
| Cycle time per task | (task completion timestamp - task creation timestamp) | Track only |
| Handoff count per task | (number of handoffs for a single task) | ≤3 for debug, ≤5 for feature |
| Blocked rate | (tasks with status=blocked at any point) / (total tasks) | <20% |
| Operator minutes per task | (estimated human time per task) | Track only |

## 3. Cost Metrics

Source: `.agent/runs.jsonl`

| Metric | Formula | Target |
|--------|---------|--------|
| Tokens per task | input_tokens + output_tokens per run | Track only |
| Tool calls per task | tool_calls per run | Track only |
| Cost per successful task | estimated_cost for tasks with result=success | Track only |
| Cost per rework | estimated_cost for tasks with rework_required=true | Track only |

## 4. Qualitative Metrics

Source: `.agent/reviews/scorecards.jsonl`

| Metric | Scale | Description |
|--------|-------|-------------|
| Clarity | 1-5 | Was the output clear and well-structured? |
| Confidence | 1-5 | How confident is the reviewer that the output is correct? |
| Friction | 1-5 | How much unnecessary friction was encountered? (1=smooth, 5=painful) |
| Surprise | 1-5 | Were there unexpected behaviors or outputs? (1=none, 5=many) |
| Taste alignment | 1-5 | Does the output match the operator's quality expectations? |

Scores of 1-2 or 4-5 require a one-sentence evidence note in the scorecard.

---

## 5. Intent-Quality Metrics

Source: `.agent/incidents.jsonl`, `.agent/runs.jsonl`

| Metric | Formula | Target |
|--------|---------|--------|
| Late [ASK OPERATOR] incidents | (incidents with failure_type=missing_intent) / (total tasks) | <10% |
| Mid-build reversals | (incidents with failure_type=mid_build_reversal) / (total tasks) | <5% |
| Validator failures from missing intent | (incidents where escaped_stage=dispatch and root_cause=SPECIFICATION) / (total incidents) | Track only |
| Assumption invalidation frequency | (assumptions invalidated per evidence review) | Track only |
| Operator UX dissatisfaction | (scorecards with taste_alignment ≤ 2) / (total scorecards) | <10% |

---

## Infrastructure Overhead Metrics

Source: Token profiling during sessions

| Metric | Formula | Target |
|--------|---------|--------|
| Infrastructure overhead ratio | (context at task start - system prompt floor) / total context window | <8% |
| Flow efficiency ratio | (context consumed by productive work) / (total context consumed) | >80% |
| Phase completion rate | (tasks completing all flow phases without escalation) / (total tasks) | >70% debug, >60% feature, >80% refactor |
| Flow accuracy | (tasks where initial classification was correct) / (total tasks) | >90% |
| Gate violation rate | (gate skips) / (total gate transitions) | <5% |
