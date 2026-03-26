# Human Oversight Improvements for THE_FACTORY

**Source:** `THE_FACTORY_human_oversight` research document (2026-03)
**Branch:** v2.2
**Status:** Proposal — awaiting operator approval

---

## Executive Summary

The research synthesizes production data from GitHub Copilot, Claude Code, Cursor, CodeRabbit, METR, and DORA across millions of developer interactions. The core finding: **no single autonomy level optimizes all quality dimensions simultaneously**. Speed peaks at L4–L5, quality peaks at L2–L3, and compound error math (85% per-step accuracy → 80% failure at 10 steps) makes unbounded autonomous runs catastrophic for non-trivial work.

THE_FACTORY already implements several best practices from the research (reversibility-based hooks, fix-attempt caps, state snapshots). This proposal identifies **gaps** and maps them to concrete improvements.

---

## What THE_FACTORY Already Does Well

| Research Recommendation | Existing Implementation |
|---|---|
| Reversibility heuristic for action classification | `git-guard.sh` blocks irreversible git ops |
| Cap autonomous fix attempts | `fix-attempt-tracker.sh` — 2-attempt cap with test-reset |
| Pre-flight context loading | Session protocol: state-snapshot → tasks.jsonl → LEARNINGS.md |
| Scoped autonomous runs (3–7 steps) | Flow skills scope work phases; plan-gate enforces spec-before-code |
| Post-session state persistence | `state-snapshot.py` Stop hook |
| Workflow-boundary interruptions | Flow skills define natural checkpoints (spec → implement → verify) |

---

## Gap Analysis: 7 Improvements

### 1. Task Risk Classifier (Hook)
**Research basis:** The breakeven analysis shows the confidence threshold varies dramatically by task risk — auto-approve above 95% for low-risk, ask at any uncertainty for high-risk. The document's three-tier model (low/medium/high risk) maps directly to THE_FACTORY's flow routing.

**Gap:** THE_FACTORY classifies tasks by *type* (debug/feature/refactor) but not by *risk*. A trivial lint fix and a database migration both enter the same feature-flow.

**Proposal:** Add a `risk` field to task entries in `tasks.jsonl` with values `low | medium | high`. Flow skills read the risk level and adjust autonomy:
- **Low risk** (test generation, docs, config, lint fixes): Skip plan-gate, auto-approve edits, post-hoc review only.
- **Medium risk** (feature implementation, refactoring): Current behavior — plan-gate required, 2-attempt fix cap.
- **High risk** (schema migrations, security, architecture, cross-section changes): Require explicit operator confirmation before *each* autonomous phase. Block auto-approve entirely.

Risk is set by the operator in the task spec or inferred from signals: files touched cross multiple sections → high; single test file → low; `security` or `migration` in task description → high.

**Implementation:** New `risk-classifier.sh` PreToolUse hook. Reads active task risk from `tasks.jsonl`, blocks edits in high-risk tasks without an approved plan.

**Task ID:** `tf-024`
**Depends on:** None

---

### 2. Blast Radius Scope Check (Hook)
**Research basis:** Blast radius = permissions × accessible tools × reachable systems × duration. The "functionality-autonomy inverse" principle: as capabilities increase, autonomy must decrease. OWASP 2026 mandates ephemeral, network-isolated execution.

**Gap:** THE_FACTORY's section contracts define ownership boundaries, but nothing enforces that an agent session *stays within* its assigned section during autonomous execution. The `fix-attempt-tracker` counts mutations but doesn't check *where* they land.

**Proposal:** Extend PreToolUse hooks to cross-reference Edit/Write file paths against the active task's section scope. If a mutation targets a file outside the task's section(s), escalate to the operator before proceeding.

**Implementation:** `blast-radius-check.sh` reads the task's section from `tasks.jsonl`, loads the section contract's `owned_paths`, and blocks out-of-scope edits with exit 2. Already have section contracts and boundary enforcement evals — this makes the enforcement runtime rather than review-time.

**Task ID:** `tf-025`

---

### 3. Compound Error Budget (Metric + Guardrail)
**Research basis:** Lusser's Law — 85% per-step accuracy → 80% failure at 10 steps. Claude 3.7's success probability halves every hour. METR found ~50% of SWE-bench-passing PRs wouldn't merge.

**Gap:** THE_FACTORY tracks fix attempts (2-cap) but has no concept of *total autonomous step count* within a session phase. An agent can make 15 sequential reads/edits across a long feature implementation without a checkpoint.

**Proposal:** Add a `step-budget` counter to flow skills. Each phase (spec, implement, verify) gets a configurable step budget (default: 7 for medium-risk, 4 for high-risk, 15 for low-risk). When the budget is exhausted, the agent must checkpoint with the operator — present a progress summary and get approval to continue.

**Implementation:** Extend `fix-attempt-tracker.sh` to track total tool calls per phase (not just source mutations). Add a `phase_step_count` field to the state file. Reset on explicit operator approval or phase transition. This is the "3–7 steps maximum between human checkpoints" recommendation made concrete.

**Task ID:** `tf-026`

---

### 4. Pre-flight Readiness Checks (Skill Enhancement)
**Research basis:** Factory.ai's Agent Readiness System evaluates 60+ criteria before an agent starts. The research emphasizes investing in pre-flight context sufficiency over runtime ambiguity detection, because LLMs cannot reliably distinguish well-specified from underspecified tasks.

**Gap:** THE_FACTORY's session protocol loads state-snapshot and tasks.jsonl, but doesn't validate that the *task itself* is sufficiently specified before work begins. Tasks with missing acceptance criteria, no section assignment, or ambiguous scope proceed anyway.

**Proposal:** Add a pre-flight checklist to flow skills. Before entering `implement` phase, verify:
1. Task has explicit acceptance criteria (or `done_criteria` field)
2. Task has a section assignment (or explicitly marked `cross-section`)
3. Risk level is set (default to `medium` if absent)
4. Relevant test suite runs cleanly (baseline)
5. No conflicting in-progress tasks on overlapping files

Fail the pre-flight with a clear message identifying what's missing. The operator fills the gaps before the agent proceeds.

**Implementation:** Add to feature-flow and refactor-flow SKILL.md as a mandatory first step. Not a hook — this is skill-level guidance that the agent follows, enforced by the plan-gate (no plan approved without pre-flight passing).

**Task ID:** `tf-027`

---

### 5. Interrupt Budget Tracking (Metric)
**Research basis:** Developers need 15–20 minutes to enter flow. Optimal deep work is 90-minute sessions. Post-commit boundary interruptions get 52% engagement vs. 62% dismissal mid-task. Target: ≤5 meaningful interruptions per day.

**Gap:** THE_FACTORY has no concept of interrupt frequency. The `AskUserQuestion` tool fires whenever the agent is uncertain, with no awareness of how many times it has already interrupted the operator in this session or today.

**Proposal:** Track interrupts (AskUserQuestion calls, plan approvals, escalations) in the state snapshot. Add an `interrupts_today` counter that persists across sessions. Flow skills should:
- Batch non-blocking clarifications rather than asking one at a time
- Prefer proceeding with a reasonable default over asking, for low-risk decisions
- Surface the interrupt count in the session summary so the operator can calibrate

This is observability, not enforcement — we measure first, then decide if a cap makes sense.

**Implementation:** Extend `state-snapshot.py` to track `interrupt_count` per session. Add to run record for trend analysis. Review after 10 sessions.

**Task ID:** `tf-028`

---

### 6. PR Size Guardrail (Eval)
**Research basis:** Graphite data shows 50-line PRs merge ~40% faster and are 15% less likely to be reverted. CodeRabbit found AI-generated code has 1.7× more issues. AI PRs wait 4.6× longer for review. The optimal review window is 200–400 LOC at under 300 LOC/hour.

**Gap:** THE_FACTORY has no guidance on PR size. Agent sessions can produce 500+ line diffs in a single commit.

**Proposal:** Add a convention eval that flags commits exceeding 200 LOC of net changes. Not a hard block — a warning in the run record and a recommendation to split. Flow skills should advise splitting large implementations into multiple focused commits at phase boundaries.

**Implementation:** New eval in `evals/test_conventions.py` that reads the last commit's diff stat and warns if net additions exceed 200 lines. Add guidance to feature-flow SKILL.md: "If implementation exceeds ~200 LOC, split into focused commits at natural phase boundaries."

**Task ID:** `tf-029`

---

### 7. Trust Calibration Metrics (Observability)
**Research basis:** Anthropic's data shows experienced users evolve toward supervisory oversight — auto-approve rates rise but so do interrupt rates (5% → 9%), indicating *different, not less* oversight. Stack Overflow 2025: 46% of devs don't trust AI output accuracy.

**Gap:** THE_FACTORY tracks task completion and run records but doesn't track *oversight patterns* — how often the operator intervenes, what triggers intervention, whether the agent's self-initiated stops were warranted.

**Proposal:** Extend run records with oversight metadata:
- `operator_interventions`: count of times operator interrupted or redirected
- `agent_escalations`: count of agent-initiated stops/questions
- `auto_approved_phases`: count of phases that needed no operator input
- `rework_count`: number of reverts or redo cycles

Over time, this data shows whether THE_FACTORY's autonomy level is calibrating correctly — trending toward fewer unnecessary interruptions without missing real problems.

**Implementation:** Extend run record schema in `.agent/schemas/`. Update `state-snapshot.py` to capture intervention events. Add to `assess.py` analysis for trend reporting.

**Task ID:** `tf-030`

---

## Priority Order

| Priority | Task | Risk | Effort | Dependencies |
|---|---|---|---|---|
| 1 | Pre-flight Readiness (tf-027) | Low | Small | None — skill guidance only |
| 2 | Task Risk Classifier (tf-024) | Medium | Medium | tasks.jsonl schema addition |
| 3 | Blast Radius Scope Check (tf-025) | Medium | Medium | Section contracts (done), tf-024 |
| 4 | Compound Error Budget (tf-026) | Medium | Medium | fix-attempt-tracker extension |
| 5 | PR Size Guardrail (tf-029) | Low | Small | None |
| 6 | Interrupt Budget Tracking (tf-028) | Low | Small | state-snapshot extension |
| 7 | Trust Calibration Metrics (tf-030) | Low | Medium | run record schema extension |

**Rationale:** Pre-flight and risk classification are highest priority because they prevent bad runs from starting — cheaper than detecting problems mid-run. Blast radius and error budgets are runtime enforcement that builds on the risk classifier. PR size and interrupt tracking are observability that feeds future calibration. Trust metrics are the long-term feedback loop.

---

## What This Proposal Does NOT Include

- **LLM confidence scoring:** The research confirms generative code LLMs are not well-calibrated and reasoning fine-tuning degrades abstention ability by 24%. No internal confidence mechanism is reliable enough to gate autonomy decisions. We rely on environmental signals (test results, lint, section boundaries) instead.
- **Multi-agent coordination:** DeepMind and Anthropic research confirms single-agent with dynamic skills outperforms multi-agent. THE_FACTORY's architecture is already correct here.
- **Formal uncertainty quantification:** No production coding agent does this successfully. The pre-flight + risk classifier + environmental signals approach is the pragmatic alternative.
