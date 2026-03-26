# v2.2 Consolidated Improvement Plan

**Date:** 2026-03-26
**Branch:** v2.2
**Status:** Approved — master backlog for next version
**Sources:** 12 plan/proposal files (Claude + GPT), v2.2 compass analysis, existing tasks.jsonl

---

## Purpose

This document is the single source of truth for all improvements targeting the next version of THE_FACTORY. It consolidates findings from:

- `v3-migration-proposal.md` — Claude Code standards audit
- `human-oversight-improvements.md` — AI coding agent autonomy research (tf-024–030)
- `automation-proposal.md` — operator-removal roadmap (L2→L4)
- `deep-research-proposal.md` — external TFv2 audit findings
- `automation-deep-research-synthesis.md` — pipeline automation deep research
- `human-involvement-proposal.md` — CI/CD human involvement research
- `decomposition-research-proposal.md` — software decomposition research
- `analysis-to-action.md` — landscape analysis action items
- `gpt/2026-03-26-tf-review-action-proposal.md` — GPT assessment: repo hardening
- `gpt/automation-action-proposal.md` — GPT assessment: automation operationalization
- `gpt/SDP-001-the-factory-software-decomposition-action-plan.md` — GPT assessment: decomposition
- `gpt/human-involvement-proposal.md` — GPT assessment: human oversight model

Every improvement is either mapped to an existing task, assigned a new task ID, or explicitly deferred with rationale.

---

## Already Tracked — Execute As-Is

### Existing tasks (tasks.jsonl)

| Task ID | Summary | Status |
|---|---|---|
| tf-011 | Review-cycle skill | pending |
| tf-012 | Edit() hygiene rule in flow skills | pending |
| tf-013 | Session scope guideline (cap 1-2 objectives) | pending |
| tf-014 | Phase handoff prompt template | pending |
| tf-024 | Task risk classifier (risk field in tasks.jsonl) | pending |
| tf-025 | Blast radius scope check (PreToolUse hook) | pending, blocked by tf-024 |
| tf-026 | Compound error budget (step-budget per phase) | pending |
| tf-027 | Pre-flight readiness checks in flow skills | pending |
| tf-028 | Interrupt budget tracking in state snapshot | pending |
| tf-029 | PR size guardrail (convention eval) | pending |
| tf-030 | Trust calibration metrics in run records | pending |

### v2.2 Compass Priorities (from memory, not yet in tasks.jsonl as individual tasks)

| Priority | Summary | Notes |
|---|---|---|
| P1 | Native hooks migration | Hooks already native; minor cleanup remains (see tf-040) |
| P2 | CI-gate eval suite | See tf-041 (CI workflows) |
| P3 | Formalize section contracts | Reinforced by tf-049 (extended skill frontmatter) |
| P4 | Drop experiment framework → Promptfoo | Execute when touching experiments |
| P5 | Drop token dashboard → Langfuse | Execute when Langfuse is mature |
| P6 | LLM trigger fallback | Prerequisite: tf-055 (trigger miss logging) |
| P7 | JSONL → SQLite | Execute when corruption/concurrency appears |
| P8 | Skill load audit | Independent |

---

## Net-New Tasks — Batched by Dependency and Value

### Batch 1: Quick Wins (1-2 sessions)

Low-effort, high-clarity improvements. No dependencies. Ship first.

| Task ID | Summary | Sources | Effort |
|---|---|---|---|
| tf-037 | Add YAML frontmatter to 5 portfolio-level skills | v3-migration 2.1 | Small |
| tf-038 | Eval: test_all_skills_have_frontmatter | v3-migration 2.2 | Small |
| tf-039 | Eval: test_native_hooks_settings_valid | v3-migration 1.3 | Small |
| tf-040 | Switch state-snapshot hook from Stop to SessionEnd | v3-migration 1.2 | Small |
| tf-041a | Declare dependency profiles in pyproject.toml (experiments, observability, evals) | deep-research 1, GPT/tf-review W1 | Small |
| tf-041b | Add LICENSE file (operator chooses MIT/Apache-2.0/private) | deep-research 2, GPT/tf-review W1 | Trivial |
| tf-041c | Normalize Langfuse env var (LANGFUSE_HOST vs LANGFUSE_BASE_URL) | GPT/automation P0 | Trivial |

### Batch 2: Schema & CI Foundation (2-3 sessions)

Prerequisite for all observability, automation, and enforcement work downstream.

| Task ID | Summary | Sources | Effort | Depends On |
|---|---|---|---|---|
| tf-042 | JSON schemas for tasks.jsonl, runs.jsonl, incidents.jsonl | v3-migration 5.1, GPT/SDP-001 W4, GPT/human-involvement | Medium | None |
| tf-043 | Eval: test_all_jsonl_entries_valid | v3-migration 5.2 | Medium | tf-042 |
| tf-044 | CI workflow templates (.github/workflows/ for evals, nightly assess, manual experiments) | automation-proposal, automation-synth 1, GPT/automation P1, GPT/tf-review W2 | Medium | None |
| tf-045 | Structured output for assess.py + experiment.py (--out flag, JSON reports) | GPT/automation P0 | Small | None |
| tf-046 | JSON/shell sanity checks in CI (shellcheck hooks, json.tool settings.json) | automation-synth 6 | Trivial | tf-044 |
| tf-047 | Artifact retention policy (retention-days on CI artifacts) | automation-synth 5 | Trivial | tf-044 |

### Batch 3: Policy & Oversight Layer (2-3 sessions)

Builds on tf-024 (risk classifier). Makes oversight evidence-driven instead of blanket gates.

| Task ID | Summary | Sources | Effort | Depends On |
|---|---|---|---|---|
| tf-048 | Risk-tiered oversight matrix + oversight policy section in CLAUDE.md | GPT/human-involvement 1+5, human-involvement-proposal | Medium | tf-024 |
| tf-049 | Augment tf-027 pre-flight with ambiguity detection (flag vague terms without quantified criteria) | human-involvement N3 | Small | tf-027 |
| tf-050 | Stop-the-line circuit breaker (regression/drift/error-chain signals halt session) | human-involvement N4, GPT/human-involvement 4 | Medium | tf-026 |
| tf-051 | Three-loop control model documentation in CLAUDE.md (inner/middle/outer) | decomposition-research 4 | Small | None |

### Batch 4: Observability & Measurement (2-3 sessions)

Metrics that feed the calibration loop. Measurement before enforcement.

| Task ID | Summary | Sources | Effort | Depends On |
|---|---|---|---|---|
| tf-052 | Pipeline SLOs (completion rate, rework rate, escalation rate, test-gate failure rate) | decomposition-research 5, GPT/SDP-001 W4 | Medium | tf-042 |
| tf-053 | Operator review latency tracking (time_to_operator_response in run records) | human-involvement N1, GPT/human-involvement 3 | Small | tf-042 |
| tf-054 | Eval flakiness budget (per-test pass/fail history, auto-rerun known-flaky before consuming fix-attempt) | human-involvement N2 | Medium | tf-042 |
| tf-055 | Trigger table miss logging (log unmatched inputs to .agent/trigger-misses.jsonl) | analysis-to-action 3b | Small | None |

### Batch 5: Architecture Documentation (1-2 sessions)

Durable rationale artifacts. No code changes, high future-session value.

| Task ID | Summary | Sources | Effort | Depends On |
|---|---|---|---|---|
| tf-056 | ADR template + 3 seed ADRs (single-agent-with-skills, file-based-coordination, sections-as-bounded-contexts) | decomposition-research 3, analysis-to-action 3d, GPT/SDP-001 W1 | Medium | None |
| tf-057 | Artifact taxonomy document (every artifact type, schema ref, producer, consumer, validation) | decomposition-research 1, GPT/SDP-001 W1 | Small | None |
| tf-058 | Standard abstain packet template (structured escalation format for AskUserQuestion) | GPT/human-involvement 2 | Small | None |

### Batch 6: Automation Prerequisites (2-3 sessions)

Prepares the repo for autonomous sessions and external contributors.

| Task ID | Summary | Sources | Effort | Depends On |
|---|---|---|---|---|
| tf-059 | Idempotency keys design for event-driven sessions (event_id dedup) | automation-synth 2 | Small | None (design only) |
| tf-060 | Extend skill frontmatter schema (inputs, outputs, success_criteria, failure_policy) | decomposition-research 6, GPT/SDP-001 W2 | Medium | tf-037 |
| tf-061 | Doctor/bootstrap script (fresh-clone validation: Python, .venv, env vars, portfolio repos) | GPT/tf-review W1 | Medium | tf-041a |
| tf-062 | Standalone experiment tasks (inline fixtures, no project repo dependency) | deep-research 6, GPT/tf-review W4 | Medium | None |
| tf-063 | Workspace setup docs (standalone vs portfolio mode, project layout) | deep-research 3, GPT/tf-review W1 | Medium | None |

### Batch 7: Deferred — Execute After Batches 1-6

These depend on earlier work or have low urgency.

| Task ID | Summary | Sources | Effort | Depends On |
|---|---|---|---|---|
| tf-064 | Calibration review loop (quarterly threshold tuning from metrics → thresholds.json) | human-involvement N5 | Medium | tf-052, tf-053, tf-054 |
| tf-065 | Portable hook runtime (no hardcoded .venv/bin/python, graceful fallback) | deep-research 4, GPT/tf-review W3 | Small | tf-044 |
| tf-066 | Improvement loop formalization (triage flow for candidates, protocol review template) | GPT/tf-review W5, GPT/automation P2 | Medium | tf-045 |
| tf-067 | Dependency/build-script integrity guardrail (detect high-risk file mutations) | GPT/SDP-001 W5 | Medium | tf-042, tf-024 |
| tf-068 | Section-review manager-worker pilot (one controlled multi-agent experiment) | GPT/SDP-001 W6 | Large | tf-060, tf-042 |
| tf-069 | Context checkpointing research (session knowledge capture prototype) | analysis-to-action 3a | Research | None |

---

## Sequencing Diagram

```
Batch 1: Quick Wins ─────────────────────────────────────────┐
  tf-037..041c (frontmatter, evals, LICENSE, deps, env fix)  │
                                                              │
Batch 2: Schema & CI ────────────────────────────────────────┤
  tf-042..047 (schemas, CI workflows, structured output)     │
                                                              │
Existing: tf-024..030 ───────────────────────────────────────┤
  (risk classifier, blast radius, error budget, pre-flight,  │
   interrupt tracking, PR size, trust metrics)                │
                                                              │
Batch 3: Policy & Oversight ─────────────────────────────────┤
  tf-048..051 (oversight matrix, ambiguity, circuit breaker, │
   three-loop docs)                                           │
                                                              │
Batch 4: Observability ──────────────────────────────────────┤
  tf-052..055 (SLOs, review latency, flakiness, trigger log) │
                                                              │
Batch 5: Architecture Docs ──────────────────────────────────┤
  tf-056..058 (ADRs, taxonomy, abstain packet)               │
                                                              │
Batch 6: Automation Prereqs ─────────────────────────────────┤
  tf-059..063 (idempotency, skill schema, doctor, standalone)│
                                                              │
Batch 7: Deferred ───────────────────────────────────────────┘
  tf-064..069 (calibration loop, portable hooks, pilot, etc.)
```

Batches 1-2 are strict prerequisites. Batches 3-6 can interleave. Batch 7 waits for data from earlier batches.

---

## Explicitly Declined

These were recommended by one or more plans but are not worth pursuing:

| Recommendation | Why Declined | Source |
|---|---|---|
| Vector DB / embedding-based skill retrieval | Trigger table + keyword matching sufficient for <20 skills. Log misses instead (tf-055). | deep-research 5, analysis-to-action 4b |
| Multi-agent swarm / LangGraph / CrewAI | Single-agent validated by DeepMind/Anthropic. One narrow pilot (tf-068) is sufficient. | analysis-to-action 4a, GPT/SDP-001 |
| Temporal / Redis Streams / Argo / Kubernetes | Current scale doesn't justify. GitHub Actions is the right orchestration layer. | automation-proposal, automation-synth, GPT/automation |
| External PM tools (Linear/Jira) | No team to coordinate. tasks.jsonl is sufficient. | automation-proposal |
| Managed memory services (Mem0, AWS Memory) | File-based state works. Move to SQLite (v2.2 P7) only on corruption/concurrency. | analysis-to-action 4c |
| OpenTelemetry + Prometheus + Grafana | Langfuse covers tracing. Custom metrics not needed yet. | automation-synth |
| Approval boards / CAB-style gates | DORA evidence: hurts delivery, no quality benefit. Single-operator model is correct. | human-involvement, GPT/human-involvement |
| ML confidence scoring for autonomy gating | LLMs poorly calibrated. Environmental signals (tests, scope, sections) are reliable. | human-oversight-improvements |

---

## Relationship to Source Plans

After this consolidation, the individual plan files in `.claude/plans/` are **archived references**. This document supersedes all of them for task planning purposes. The source files remain useful for understanding the research rationale behind each improvement.

---

## Success Criteria for v2.2 Completion

All of these must be true before declaring v2.2 complete:

1. Batches 1-4 fully implemented (quick wins + schema + policy + observability)
2. tf-024 through tf-030 implemented (human oversight tasks)
3. CI runs eval suite on every push/PR
4. Run records include risk, oversight mode, and intervention metadata
5. At least 3 ADRs documenting core architectural decisions
6. assess.py reports pipeline SLO metrics
7. No improvement candidate from any source plan is unaccounted for (tracked, declined, or deferred with rationale)
