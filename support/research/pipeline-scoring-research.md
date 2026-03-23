# Pipeline Scoring: Git History + Agent Telemetry

> **Date:** 2026-03-22
> **Context:** Research into published methods for evaluating multi-agent development pipelines
> using git commit artifacts and structured execution logs.
> **Applies to:** THE_FACTORY v1.9 infrastructure (runs.jsonl, incidents.jsonl, scorecards.jsonl)

## Key Sources

### Git-Derived Code Quality

**GitClear AI Code Quality Study (2025)**
Analyzed 211 million lines of code. Introduced "churn rate" — the percentage of code rewritten
within 14 days of being authored — as a proxy for rework quality. Finding: churn rose from 5.5%
(2020) to 7.9% (2024) as AI-assisted coding increased. Code duplication grew 4x.
- Source: gitclear.com/ai_assistant_code_quality_2025_research
- Applicable metric: **14-day churn rate** computable from `git log --follow`

**GitGoodBench (JetBrains Research, ACL REALM 2025)**
Evaluates agent performance on version control tasks. Scores: commit message quality, change
cohesion within commits, logical progression across a branch, commit size appropriateness.
Baseline: GPT-4o achieved 21.11% solve rate on Git workflow tasks.
- Source: arXiv:2505.22583
- Applicable metric: **commit cohesion** (files per commit in same domain), **progression score**

**"How AI Coding Agents Modify Code" (MSR, January 2026)**
Analyzed 24,014 merged agentic PRs (440,295 commits) vs. 5,081 human PRs (23,242 commits).
Key finding: agent PRs differ most in commit count and file breadth, not lines changed. Agent PRs
show slightly higher description-to-diff semantic alignment.
- Source: arXiv:2601.17581
- Applicable metric: **files-touched breadth**, **description-to-diff alignment**

### Multi-Agent Evaluation

**MultiAgentBench / MARBLE (ACL 2025)**
Replaces binary pass/fail with milestone-based KPIs. Segments tasks into sub-goals, tracks which
milestones each agent achieves, computes KPI as ratio of milestones completed. Evaluates planning
quality, communication effectiveness, and coordination topologies. Finding: graph topology
performed best; cognitive planning improved milestone achievement by 3%.
- Source: arXiv:2503.01935
- Applicable metric: **milestone completion ratio** (maps to flowPhase in runs.jsonl)

**"Beyond Task Completion" (December 2025)**
Proposes four-pillar framework evaluating LLMs, Memory, Tools, and Environment. Key insight:
binary task-completion metrics miss behavioral deviations that only surface at runtime. Their
framework catches policy violations and validation-flow deviations that pass/fail misses.
- Source: arXiv:2512.12791
- Applicable metric: **policy adherence rate** (did agent follow flow phases?)

**DeepEval Agent Metrics**
Granular metric taxonomy for agent evaluation:
- TaskCompletionMetric: did the agent achieve the goal?
- StepEfficiencyMetric: unnecessary/redundant steps?
- PlanQualityMetric: logical, complete, efficient plan?
- PlanAdherenceMetric: did execution follow the plan?
- ToolCorrectnessMetric: right tools, right arguments?
- Source: deepeval.com/guides/guides-ai-agent-evaluation-metrics
- Applicable: step efficiency and plan adherence from execution traces

### Observability Standards

**OpenTelemetry GenAI Semantic Conventions (2025)**
Establishing standard schema for tracing AI agent systems. Defines attributes for tasks, actions,
agents, teams, artifacts, memory. Closest thing to an industry standard for agent trace format.
- Source: opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/
- Applicable: schema alignment for future interoperability

**AgentOps (arXiv:2411.05285)**
Session-level, trace-level, span-level monitoring with replay. Captures reasoning traces,
tool/API calls, session state, caching behavior, cost metrics. OTel support added March 2025.
- Source: agentops.ai
- Applicable: cost-per-task tracking pattern

## Gap in Published Work

No published system unifies git commit analysis with agent execution traces for holistic pipeline
scoring. The pieces exist independently:
- GitGoodBench scores commit structure
- DeepEval scores execution traces
- GitClear scores code churn from diffs
- OTel standardizes trace format

THE_FACTORY's combination of runs.jsonl + incidents.jsonl + phase-boundary git commits is
already closer to a unified system than anything published. The missing piece is the scoring
computation layer.

## Recommended Metrics for THE_FACTORY

### Tier 1: Computable Now (from existing runs.jsonl + git)

| Metric | Formula | Source |
|---|---|---|
| Task success rate | `success / total` grouped by task_type | runs.jsonl |
| Rework rate | `rework_required: true / total` | runs.jsonl |
| Attempt efficiency | `mean(attempt_count)` by task_type | runs.jsonl |
| Incident rate | `incidents / runs` per period | incidents.jsonl |
| Root cause distribution | group by `root_cause_classification` | incidents.jsonl |
| Milestone completion ratio | `flowPhase reached / total phases` | runs.jsonl (needs flowPhase field) |

### Tier 2: Computable with Git Script

| Metric | Formula | Source |
|---|---|---|
| 14-day churn rate | lines rewritten within 14 days / total lines | git log |
| Commit cohesion | files in same layer per commit / total files per commit | git log + path analysis |
| Branch commit count | commits per task branch | git log |
| Revert frequency | reverts / total commits per period | git log |
| Files-touched breadth | unique directories per task branch | git log |

### Tier 3: Requires Schema Extension

| Metric | Formula | Source |
|---|---|---|
| Phase-boundary commit quality | structured assessment per commit | new field in runs.jsonl |
| Token cost per task type | `estimated_cost` grouped by task_type | runs.jsonl (field exists, not populated) |
| Operator time per task | wall-clock from dispatch to close | needs timestamp pairs |
| Description-to-diff alignment | semantic similarity score | NLP on commit msg vs diff |

## Relationship to WFC-001

The WFC-001 proposal (Lightweight Workflow Controller) in PROTOCOL_IMPROVEMENTS.md lists
"baseline metrics" as prerequisite #3. This research validates that requirement and defines
what those baselines should measure. The controller's value proposition — "operator minutes
per task decreases by >30%" — needs the Tier 1 metrics as a baseline before implementation
can be justified.
