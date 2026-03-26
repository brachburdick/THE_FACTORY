# Automation Proposal: From Operator-Managed to Event-Driven Pipeline

**Date:** 2026-03-26
**Branch:** v2.2
**Input:** Research document "Automating AI agent pipelines: eliminating the human operator"
**Relationship to v2.2 roadmap:** Extends it. v2.2 focuses on internal tooling cleanup (hooks, evals, dashboards). This proposal adds the *external* automation layer that removes the human operator loop.

---

## Thesis

THE_FACTORY currently operates at **Level 2** (Collaborator) — the operator starts every session, assigns every task, triages every observation, and reviews every output. The research confirms that production-proven technology exists to reach **Level 4** (Approver) — the pipeline runs autonomously, the operator reviews completed PRs and handles escalations.

This proposal maps the research findings to concrete, shippable changes for THE_FACTORY, ordered by impact and dependency.

---

## Phase 1 — Event-Driven Session Triggers (replaces manual "start a session")

**Problem:** Every agent session today begins with the operator typing a prompt. This is the single biggest throughput bottleneck — the pipeline is idle whenever the operator is away.

**What to build:**

1. **GitHub Issue → Session trigger.** When an issue is assigned to a bot label (or `@claude` is mentioned in a PR/issue), a GitHub Action starts a Claude Code session with the issue body as prompt. The Claude Code GitHub Action already supports this pattern.

2. **CI failure → Fix session.** When CI fails on a branch, trigger a Claude Code session scoped to the failing tests/build errors. The Elastic "human-supervised AI autonomous contribution" pattern — agent receives error, generates fix, pushes commit, CI restarts.

3. **Cron → Maintenance sessions.** Scheduled sessions for: eval suite runs, documentation drift checks, dependency updates, backlog grooming. Use GitHub Actions cron or the Claude Agent SDK's programmatic `query()`.

4. **Task queue consumption.** When a task in `.agent/tasks.jsonl` is marked `pending` and unblocked, a trigger can start a session that claims and works it — no operator needed.

**Prerequisite:** v2.2 Priority 2 (CI-gate the eval suite) must land first — autonomous sessions need automated quality checks before their output reaches a human.

**Ship as:** GitHub Actions workflow definitions in `.github/workflows/`. One workflow per trigger type. Start with CI-failure trigger (lowest risk, highest signal).

---

## Phase 2 — Automated Task Graph Management (replaces manual queue management)

**Problem:** The operator currently decides task ordering, priority, and dependency. `.agent/tasks.jsonl` has the data but no automation consuming it.

**What to build:**

1. **Priority scoring.** Each task gets a computed priority from: dependency readiness (unblocked > blocked), task type (fix > feature > refactor), age (older > newer), explicit operator priority override. A script or hook computes this on task creation/update.

2. **Auto-claim on session start.** When a session starts (from Phase 1 triggers or manually), it reads the task queue, picks the highest-priority unblocked task, and claims it. Remove the current manual "check tasks.jsonl and claim" step from Session Protocol.

3. **Dependency chain resolution.** When a task completes, scan for blocked tasks whose blockers are now all resolved. Mark them `pending`. If Phase 1 triggers are active, this automatically starts the next session.

**Ship as:** Python script in `scripts/task-dispatch.py` + hook integration. The script is the "scheduler" — triggers call it, it returns the next task to work.

---

## Phase 3 — Eval-Driven Self-Improvement (replaces manual observation triage)

**Problem:** The operator currently reads session transcripts, identifies protocol weaknesses, writes improvement candidates to `improvement-candidates.jsonl`, and decides when to act on them. This is the most cognitively expensive operator role.

**What to build:**

1. **Failure-to-eval conversion.** When a session logs an incident (`.agent/incidents.jsonl`), automatically generate a draft eval test case in `.agent/evals/`. Use the incident's reproduction steps as the eval scenario. Operator reviews and promotes to `evals/`.

2. **Post-session consolidation.** After every session, run a "dream" pass that: extracts corrections/failures from the session, checks them against existing evals and learnings, writes new entries to `LEARNINGS.md` or drafts new eval cases. This is the Auto Dream pattern — already partially implemented via state-snapshot hook, but not doing knowledge extraction.

3. **Protocol optimization loop.** When eval scores on a skill or CLAUDE.md section degrade below threshold: automatically generate variant instructions, test them against the eval suite, deploy the winning variant. Start simple (A/B between current and proposed), evolve toward DSPy/GEPA-style optimization later.

**Prerequisite:** v2.2 Priority 2 (CI-gated evals) and Priority 4 (Promptfoo migration) — need machine-readable eval results before automating improvement decisions.

**Ship as:**
- `scripts/incident-to-eval.py` — converts incidents to draft eval cases
- Post-session hook addition to state-snapshot hook — runs consolidation
- `scripts/protocol-optimize.py` — generates and tests instruction variants

---

## Phase 4 — Layered Output Review (partially replaces manual PR review)

**Problem:** The operator reviews every line of agent output. The research shows AI-generated code has 1.7x more issues than human code, so human review stays — but automated pre-screening can catch the mechanical stuff.

**What to build:**

1. **LLM Judge gate.** Before any PR is opened by an autonomous session, a separate Claude call reviews the diff for: scope creep (changes beyond the task description), test disabling or weakening, security issues (OWASP top 10 patterns), style violations. Spotify's pattern — vetoes ~25% of sessions.

2. **Confidence-based routing.** The agent self-reports confidence at session end (already captured in run records). Low-confidence sessions get flagged for priority human review. High-confidence sessions with clean LLM Judge results can be auto-merged to a staging branch.

3. **Keep human review as final gate.** The operator reviews PRs on their schedule (overnight PR pattern). The automation ensures they only see pre-screened, quality-filtered work.

**Ship as:**
- `scripts/pr-judge.py` — LLM judge that reviews diffs before PR creation
- GitHub Actions workflow that runs the judge on PRs from bot branches
- Labels/annotations on PRs indicating confidence level and judge results

---

## Phase 5 — Safety Architecture (required before Phase 1 goes live)

**Problem:** Autonomous sessions without safety controls can loop, overspend, or make destructive changes.

**What to build:**

1. **Budget controls.** Hard token limit per session (`max_budget_usd` in Claude Agent SDK). Hard wall-clock timeout. These are non-negotiable — the research cites a $180/20-minute runaway incident.

2. **Escalation circuit breaker.** If a session hits 3 consecutive tool denials, 2 failed fix attempts (already tracked by fix-attempt hook), or encounters an ambiguous requirement — stop and create a "needs-human" task rather than flailing.

3. **Branch isolation.** Autonomous sessions work on `bot/task-{id}` branches, never on `main` or feature branches. Git guard hook already prevents main commits — extend it to enforce branch naming for autonomous sessions.

4. **Sandbox execution.** For sessions that run shell commands, use Docker-based isolation (Docker Desktop 4.60+ MicroVMs). Network allow-list scoped to the project's known dependencies.

**Ship as:** Configuration in `.claude/settings.json` + GitHub branch protection rules + Docker Compose file for sandbox.

---

## What NOT to Build

The research covers Temporal, Redis Streams, Inngest, and other heavy orchestration infrastructure. **THE_FACTORY doesn't need any of this yet.** The current scale is one operator, a handful of projects, sessions measured in dozens per week. The right orchestration layer at this scale is:

- **GitHub Actions** for event-driven triggers and CI
- **`.agent/tasks.jsonl`** (or SQLite per v2.2 Priority 7) for task state
- **Shell scripts + hooks** for dispatch logic
- **Claude Agent SDK** if/when programmatic session control is needed

Temporal and Redis are for teams running thousands of concurrent agent sessions. Premature adoption would add infrastructure burden without solving a real problem.

Similarly, skip:
- **Linear/Jira integration** — the task queue is in `.agent/tasks.jsonl`, adding an external PM tool is overhead without a team
- **Slack triggers** — no team to notify; GitHub is the single communication channel
- **Memory frameworks (Letta/MemGPT)** — Claude Code's built-in memory + MEMORY.md + LEARNINGS.md is sufficient at current scale

---

## Implementation Order

```
                    ┌──────────────────┐
                    │  v2.2 Priorities │
                    │  1-2 (hooks,     │
                    │  CI-gated evals) │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Phase 5: Safety │  ← must land before any autonomous sessions
                    │  (budget, branch, │
                    │   circuit breaker)│
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Phase 1: Event  │  ← start with CI-failure trigger only
                    │  Triggers        │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───────┐ ┌───▼────────┐ ┌───▼────────────┐
     │ Phase 2: Task  │ │ Phase 3:   │ │ Phase 4: LLM   │
     │ Dispatch       │ │ Eval Loop  │ │ Judge + Review  │
     └────────────────┘ └────────────┘ └────────────────┘
```

Phases 2, 3, and 4 are independent and can be built in parallel once Phase 1 is stable.

---

## Success Criteria

| Metric | Current (L2) | Target (L4) |
|--------|-------------|-------------|
| Sessions requiring operator to start | 100% | <20% |
| Task assignment requiring operator | 100% | 0% (auto-dispatch) |
| Observations triaged manually | 100% | <30% (auto-converted to evals) |
| PRs reviewed with no pre-screening | 100% | 0% (all LLM-judged first) |
| Operator hours per week | ~15-20h | ~3-5h (review PRs + handle escalations) |

---

## Relationship to Existing v2.2 Roadmap

This proposal **does not replace** the v2.2 priorities — it builds on top of them:

| v2.2 Priority | Status | This Proposal |
|---------------|--------|---------------|
| P1: Native hooks migration | Prerequisite | Phase 5 extends hook system |
| P2: CI-gate eval suite | Prerequisite | Phase 1, 3, 4 all depend on it |
| P3: Section contracts | Independent | No dependency |
| P4: Promptfoo migration | Prerequisite for Phase 3 | Protocol optimization needs machine-readable eval output |
| P5: Langfuse migration | Independent | Useful for monitoring autonomous sessions |
| P6: LLM trigger fallback | Absorbed into Phase 1 | Session triggers need robust intent classification |
| P7: SQLite migration | Independent | Becomes more valuable with concurrent autonomous sessions |
| P8: Skill load audit | Independent | No dependency |

The natural sequence: finish v2.2 P1-P2 → ship Phase 5 (safety) → ship Phase 1 (CI-failure trigger as first autonomous session type) → expand from there based on what works.
