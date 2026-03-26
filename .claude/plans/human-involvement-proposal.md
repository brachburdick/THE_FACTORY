# Human Involvement Research → THE_FACTORY Improvements

**Source:** Deep Research Report — "Human Involvement in Automated CI/CD and ML Pipelines"
**Branch:** v2.2
**Status:** Proposal — awaiting operator approval
**Relation:** Complements `.claude/plans/human-oversight-improvements.md` (tf-024–tf-030). That plan came from AI coding agent autonomy research; this one comes from CI/CD and DORA evidence. Where they converge, this proposal strengthens the case. Where they diverge, this adds new items.

---

## Key Findings Applied to THE_FACTORY

THE_FACTORY is a single-operator pipeline managing AI agent sessions across multiple projects. The agent (Claude Code) is the "pipeline executor"; the operator (Brach) is the human reviewer. This maps cleanly onto the report's four-level taxonomy:

| Level | THE_FACTORY equivalent | Current state |
|---|---|---|
| Fully automated | Low-risk tasks with auto-approve | Partially — no risk classifier yet (tf-024) |
| Human-on-the-loop | Agent works, operator monitors via state snapshots | Yes — state-snapshot + run records |
| Human-in-the-loop | Plan gates, AskUserQuestion, fix-attempt cap | Yes — flow skills enforce this |
| Human-in-command | CLAUDE.md, section contracts, task specs, risk policies | Yes — but policies are prose, not enforced thresholds |

---

## What's Already Covered by Existing Proposals

These findings from the report reinforce tasks already in the queue:

| Report Finding | Existing Task | Reinforcement |
|---|---|---|
| Risk-tiered approval paths (not one-size-fits-all) | tf-024 (risk classifier) | DORA's "don't treat all changes equally" directly supports this |
| Blast radius scoping | tf-025 (scope check) | Report's blast radius formula validates section-contract enforcement |
| Compound error accumulation (Lusser's Law) | tf-026 (error budget) | Report's "3–7 steps between checkpoints" matches tf-026's step-budget design |
| Pre-flight context sufficiency | tf-027 (readiness checks) | Report's "ambiguity lint" pattern strengthens the case |
| PR/commit size discipline | tf-029 (PR size guardrail) | Report's DORA "smaller safe releases" evidence supports this |
| Oversight pattern tracking | tf-030 (trust calibration) | Report's emphasis on measuring where humans are placed, not whether |

**No changes needed** to tf-024–tf-030. The CI/CD evidence independently arrives at the same recommendations.

---

## New Improvements (Not Yet Captured)

### N1. Operator Review Latency SLO

**Report basis:** DORA reports teams with fast code reviews have ~50% better delivery performance. SPACE framework identifies "waiting for review" as a productivity drag. Review latency is a first-class performance variable.

**THE_FACTORY gap:** We track task completion time and session metrics, but not how long the operator takes to review plans, approve phases, or respond to escalations. If the bottleneck shifts from agent execution to operator availability, we won't know.

**Proposal:** Track `time_to_operator_response` in run records — the elapsed time between an agent escalation (AskUserQuestion, plan gate, etc.) and the operator's response. Surface as a metric in `assess.py` trend analysis.

- Not an SLO yet — measure first for 20+ sessions, then decide if a target makes sense.
- Helps answer: "Is the operator the bottleneck, or is the agent?"
- Reveals whether interrupt batching (tf-028) is actually reducing wait time.

**Effort:** Small — extend run record schema + assess.py reporting.

---

### N2. Eval Flakiness Budget

**Report basis:** Flaky tests correlate with 3x merge time slowdown. Manual investigation costs ~$5.67 per incident vs $0.0002 for automated rerun. Flaky test handling consumes ≥2.5% of productive dev time. The recommendation: automatically rerun known-flaky tests, invest in root-cause removal, set a restart budget threshold.

**THE_FACTORY gap:** The eval suite (~73 tests) has no flakiness tracking. If a test fails intermittently, the agent wastes a fix-attempt on a phantom issue, or the operator wastes time re-running. We don't know which tests are flaky because we don't track pass/fail history per test.

**Proposal:**
1. Add a `test_results` field to run records capturing per-test pass/fail.
2. After 30+ recorded runs, flag tests that fail >10% of the time without corresponding code changes as "flaky candidates."
3. When a test fails during a session and it's a known-flaky candidate, automatically rerun once before consuming a fix-attempt from the budget (tf-026).
4. Maintain a flakiness ledger at `.agent/eval-flakiness.jsonl` — each entry records test name, fail date, code changed (yes/no), rerun result.

**Effort:** Medium — schema additions + fix-attempt-tracker integration.

---

### N3. Ambiguity Detection in Task Specs

**Report basis:** A recurring failure mode for pipeline agents is acting on underspecified intent. The report recommends an "ambiguity lint" phase before execution — block if intent is ambiguous or missing key parameters.

**THE_FACTORY gap:** tf-027 (pre-flight readiness) checks for *structural* completeness (acceptance criteria present, section assigned, risk set). It doesn't check for *semantic* ambiguity — vague terms like "improve," "optimize," "clean up," or "make it better" that lead to scope creep and divergent outcomes.

**Proposal:** Add ambiguity flags to the pre-flight checklist in flow skills:
- Flag task descriptions containing ambiguity markers: "improve," "optimize," "clean up," "better," "faster," "safer," "minimal," "various" without quantified criteria.
- When flagged, the agent asks the operator to specify: measurable success criteria, scope boundaries, and what "done" looks like.
- This is guidance, not a hard block — the operator can override with "proceed as-is."

**Effort:** Small — extend tf-027's pre-flight checklist with an additional check.

---

### N4. "Stop-the-Line" Circuit Breaker

**Report basis:** The Andon/Jidoka principle — any worker can halt the line when a defect is detected. The report frames this as a pipeline circuit breaker that prioritizes stopping propagation over maintaining throughput.

**THE_FACTORY gap:** The fix-attempt-tracker blocks after 2 source mutations without tests. But there's no mechanism for the agent to *self-halt* when it detects environmental signals that suggest the session is going wrong — e.g., test failures increasing instead of decreasing, touching files outside the task's expected scope, or accumulating a chain of errors.

**Proposal:** Add a "circuit breaker" check to the fix-attempt-tracker:
- **Regression signal:** If the test count of failures goes UP after a fix attempt (not just "still failing" but "more things broke"), immediately halt and escalate. Don't use the second attempt.
- **Drift signal:** If the set of modified files has grown to 2x+ the initial estimate (from the plan), pause and present a scope-creep summary.
- **Error chain signal:** If 3+ consecutive tool calls return errors (not test failures — tool errors like file-not-found, syntax errors, permission denied), halt and escalate.

**Effort:** Medium — extend fix-attempt-tracker logic.

---

### N5. Session Postmortem in Learning Loop

**Report basis:** The report's pipeline flowchart ends with a "Learning loop: postmortem / metrics / thresholds" step. The recommendation is to feed operational outcomes back into threshold calibration.

**THE_FACTORY gap:** `assess.py` analyzes session quality after the fact, and run records capture outcomes. But there's no structured postmortem step where findings explicitly feed back into *changing thresholds or policies*. Learning stays in `LEARNINGS.md` as prose — it doesn't update the risk classifier defaults, step budgets, or flakiness thresholds.

**Proposal:** Add a quarterly "calibration review" template:
1. Pull stats from assess.py: sessions by risk tier, intervention rates, rework rates, average phase length.
2. For each metric with a threshold (step budget, fix-attempt cap, PR size guideline, flakiness budget): compare actual distribution to current threshold.
3. Output a recommendation: tighten, loosen, or keep each threshold.
4. Operator approves changes. Updated thresholds go into a `.agent/thresholds.json` that hooks and skills read.

This closes the loop from "measure" → "act on measurement." Without it, tf-026/028/029/030 produce data that nobody uses.

**Effort:** Medium — template + thresholds.json schema + hook/skill integration.

---

## Combined Priority Map

Existing proposals (tf-024–030) + new proposals (N1–N5), ordered by impact and dependency:

| Priority | Item | Type | Effort | Dependency |
|---|---|---|---|---|
| 1 | tf-027 + N3 | Pre-flight readiness + ambiguity detection | Small | None |
| 2 | tf-024 | Task risk classifier | Medium | tasks.jsonl schema |
| 3 | tf-025 | Blast radius scope check | Medium | tf-024 |
| 4 | tf-026 + N4 | Compound error budget + circuit breaker | Medium | fix-attempt-tracker |
| 5 | N1 | Operator review latency tracking | Small | run record schema |
| 6 | tf-029 | PR size guardrail | Small | None |
| 7 | tf-028 | Interrupt budget tracking | Small | state-snapshot |
| 8 | N2 | Eval flakiness budget | Medium | run record schema |
| 9 | tf-030 | Trust calibration metrics | Medium | run record schema |
| 10 | N5 | Calibration review loop | Medium | N1, tf-028, tf-030 |

**Rationale:** Pre-flight prevents bad sessions from starting (cheapest intervention). Risk classification enables tiered autonomy. Blast radius + error budgets enforce boundaries at runtime. The rest is observability that feeds the long-term calibration loop (N5). N5 is last because it needs data from everything above it.

---

## What This Proposal Does NOT Recommend

- **External approval boards or CAB-style gates.** DORA evidence is unambiguous: these hurt delivery performance with no evidence of quality improvement. THE_FACTORY's single-operator model is correct.
- **ML-style active learning or abstention.** Relevant for data-labeling pipelines but not for a code-generation workflow. The agent's uncertainty signals are environmental (test results, scope drift), not probabilistic.
- **Automated anomaly detection on pipeline telemetry.** Premature — THE_FACTORY doesn't have enough volume to train baseline models. The circuit breaker (N4) uses simple heuristic signals instead.
- **Heavyweight process changes.** Every item above is either a hook extension, a skill-level guidance addition, or a schema field. No new approval workflows, no new roles, no new tools.
