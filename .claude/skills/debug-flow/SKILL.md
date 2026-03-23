---
name: debug-flow
description: >
  Use when the task involves fixing a bug, error, regression, failing test,
  unexpected behavior, or production incident. Signals: "fix", "broken",
  "failing", "error", "regression", "not working", "crash", "timeout".
---

# Debug Flow: Reproduce → Isolate → Diagnose → Fix → Verify

## Phase 1: Reproduce
**Goal:** Confirm the bug exists and create a minimal reproduction.
**Steps:**
1. Read the bug report or failing test. Identify the expected vs. actual behavior.
2. If a test exists that demonstrates the failure, run it. Confirm it fails.
3. If no test exists, write one that captures the reported behavior. Run it. Confirm failure.
4. Record the reproduction in the task tracker: `status: reproducing`, attach test file path.

**Git:** Commit the reproduction test: `reproduce: add failing test for {bug summary}`.

**Gate:** A failing test exists that demonstrates the bug. Do NOT proceed without this.

## Phase 2: Isolate
**Goal:** Narrow the failure to the smallest possible surface area.
**Steps:**
1. Identify which files, modules, or services are involved.
2. For cross-project issues (federated GraphQL, shared packages): determine which subgraph
   or service owns the failure. Check if the issue crosses a subgraph boundary.
3. For async/event-driven issues: check Redis pub/sub, MongoDB change streams, or
   WebSocket handlers for timing or ordering problems.
4. Read only the files in the failure path. Do NOT read unrelated code.

**Gate:** You can name the specific function, handler, or query where the bug originates.

## Phase 3: Diagnose
**Goal:** Understand the root cause, not just the symptom.
**Steps:**
1. Explain the root cause in 1-2 sentences. Write it down before coding.
2. Check: is this a recurrence of a known pattern? Search `.agent/evals/` and
   the CLAUDE.md gotchas section for related failures.
3. If three fix attempts have failed, STOP. Log an incident in `.agent/incidents.jsonl`.
   Escalate to the human with a diagnostic summary. Do not continue iterating blindly.

**Gate:** Root cause is documented. Fix approach is stated before implementation begins.

## Phase 4: Fix
**Goal:** Minimal change that addresses the root cause.
**Steps:**
1. Make the smallest change that fixes the root cause. Do NOT refactor surrounding code.
2. Run the reproduction test. Confirm it passes.
3. Run the broader test suite for the affected module. Confirm no regressions.

**Git:** Commit the fix: `fix: {root cause summary}`.

**Gate:** Reproduction test passes. No new test failures.

## Phase 5: Verify & Close
**Steps:**
1. **Separate-context verification:** Before closing, run a verification step in a
   separate context (subagent or fresh review). The context that wrote the fix must
   NOT be the only context that certifies it. Even a subagent dispatch within the
   same session counts.
2. Update task tracker: `status: complete`, attach fix summary.
3. Write a run record to `.agent/runs.jsonl`.
4. **Git:** Commit the run record and any eval case: `close: run record + verify for {task-id}`.
5. If this bug pattern is likely to recur, file an eval case in `.agent/evals/`.
5. If the fix reveals a broader architectural issue, file a separate investigation task.
   Do NOT scope-creep the current fix.

## Subagent Guidance
When launching parallel Explore subagents for investigation:
- Give each agent a **specific file scope** (e.g., "read only `bridge/` files", "read only `frontend/src/components/`"). Do NOT launch two agents with overlapping directories.
- If a codebase orientation skill exists for the project, load it first — it eliminates most exploratory reads.
- Check `.agent/state-snapshot.json` at session start. It contains the branch, last commit, active tasks, and modified files from the prior session. Use it to skip re-exploration.

## Research Heuristic: Version Delta First
When investigating why a reference implementation has a capability that your project lacks,
the first research question should always be: **"What dependency versions does the reference
use vs. what we use?"** Version delta is the highest-signal diagnostic. This heuristic would
have cut a 4-agent-hour research session to ~30 minutes (beat-link 8.0.0 vs 8.1.0-SNAPSHOT).

## Negative Constraints — Do NOT:
- Do NOT refactor while fixing. Refactoring is a separate task type.
- Do NOT add features while fixing. Feature work is a separate task type.
- Do NOT write more than one reproduction test initially. One is enough to gate Phase 1.
- Do NOT silently retry more than 3 times. Log an incident and escalate.
- Do NOT skip the separate-context verification in Phase 5.
- Do NOT modify files outside the failure path unless the fix requires it.
- Do NOT change test assertions to make them pass. Fix the code, not the tests.
- Do NOT close the task without a run record in `.agent/runs.jsonl`.
- Do NOT use docs as source-of-truth for QA verification. Verify against code (types, endpoint responses, test output). Docs may be stale.
- Do NOT assume `git add` will include new source files — check `.gitignore` patterns first. If a new `.ts`/`.tsx`/`.py` file doesn't stage, the gitignore may be too broad.
