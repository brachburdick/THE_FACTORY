# Conversation Mining: v2.2→v3.0 Sprint Synthesis

**Date:** 2026-03-26
**Sessions analyzed:** 8 (7 THE_FACTORY, 1 SCUE)
**Lenses:** A (Process Efficiency), B (Quality & Correctness), C (Learning & Knowledge)

---

## Cross-Lens Patterns

These findings appear in 2+ lens reports, indicating high-signal root causes.

### Pattern 1: Rewrite-without-reading-evals (A+B+C)

**Lenses:** A (anti-pattern #1, 3 sessions), B (verification gap #1, 5+ fix cycles in 337dd2da), C (naming/renaming rework pattern)

**Evidence:** Sessions 337dd2da, b8458acc, f1e40ee5. Agent rewrites files or renames concepts without grepping for eval assertions that test for specific strings. Produces a predictable cycle: rewrite → test failure → read eval → fix rewrite → retest. In 337dd2da, all three flow skills were rewritten from scratch, triggering 5+ fix cycles and ~30 tool calls of waste.

**Root cause:** No pre-edit step checks for downstream consumers (evals, hooks, other files). The agent treats the file being edited as self-contained.

---

### Pattern 2: Hook state leaks across test runs (A+B+C)

**Lenses:** A (flaky tests in 3 sessions), B (test isolation gap, "most persistent cross-session issue"), C (fix-attempt-tracker state cleanup ranked #2 infrastructure candidate)

**Evidence:** Sessions f1e40ee5, ebea2df6, 337dd2da. The fix-attempt-tracker.state file accumulates during a session's own Edit/Write calls, then pollutes the test suite. Each session independently discovers and works around the problem (state reset, rerun) without fixing the root cause. Circuit breaker off-by-one was dismissed as "pre-existing" in f1e40ee5 and carried through two more sessions.

**Root cause:** No test fixture resets hook state files between test classes.

---

### Pattern 3: Repeated structural re-reading (A+C)

**Lenses:** A (anti-pattern #2, redundant re-reads in 6/8 sessions), C (knowledge gap #1 and #2: settings.json wiring in 4 sessions, flow skill structure in 5 sessions)

**Evidence:** settings.json hook structure re-read in sessions f1e40ee5, ebea2df6, 337dd2da, 4cb11bfd. Flow skills re-read in 5 sessions. ~10 tool calls per occurrence for settings.json alone.

**Root cause:** Slowly-changing structural knowledge is not persisted. Every session re-discovers hook wiring groups, flow skill phase structure, and CLAUDE.md layout from scratch.

---

### Pattern 4: Environment debugging spirals (A+B)

**Lenses:** A (anti-pattern #3, 25+ calls in 02bbfd93), B (hardware verification gap)

**Evidence:** Session 02bbfd93 spent 25+ tool calls on network debugging (ARP, ping, routing, port scanning) when the XDJ-AZ was simply not powered on. Session 83bb2ae7 tried file:// URLs before discovering Chrome MCP doesn't support them.

**Root cause:** Agent enters multi-step investigation loops instead of asking the user one clarifying question.

---

### Pattern 5: Write-instead-of-Edit for tested files (B+C)

**Lenses:** B (convention violation in 337dd2da, ed058c05), C (scoping decisions that lead to rework)

**Evidence:** Two sessions used Write (full rewrite) instead of Edit (targeted change) for files with eval coverage. Session 337dd2da rewrote all 3 flow skills from scratch and triggered cascading eval failures. Session ed058c05 rewrote settings.json and produced invalid JSON.

**Root cause:** Write is easier for large changes but eliminates the diff-visible safety net and increases error surface.

---

## Ranked Improvements

| Rank | Category | Title | Impact | Freq | Feasibility | Score | Type |
|------|----------|-------|--------|------|-------------|-------|------|
| 1 | PIPELINE | Pre-edit downstream reference check | 5 | 4 | 4 | 80 | hook |
| 2 | PIPELINE | Fix test isolation for hook state | 5 | 3 | 5 | 75 | eval-fixture |
| 3 | PIPELINE | Settings.json hook wiring memory | 4 | 5 | 5 | 100→ ranked by waste | memory |
| 4 | PIPELINE | 3-probe-then-ask escalation rule | 4 | 3 | 5 | 60 | convention |
| 5 | PIPELINE | Baseline test failures in state snapshot | 4 | 3 | 4 | 48 | hook |
| 6 | PIPELINE | Subagent prompt template (extraction-specific) | 3 | 3 | 5 | 45 | skill |
| 7 | PIPELINE | Prefer Edit over Write for tested files | 4 | 3 | 3 | 36 | convention |
| 8 | PROJECT | beat-link API reference doc | 4 | 2 | 4 | 32 | doc |
| 9 | PIPELINE | Flow skill phase structure memory | 3 | 5 | 5 | 75→ ranked by waste | memory |
| 10 | PROJECT | Hook composition integration tests | 4 | 2 | 3 | 24 | eval |
| 11 | PIPELINE | Rename-across-codebase skill | 3 | 2 | 4 | 24 | skill |
| 12 | PROJECT | SCUE hardware pre-flight script | 3 | 2 | 4 | 24 | script |
| 13 | PROJECT | Pro DJ Link network setup memory | 3 | 2 | 5 | 30 | memory |
| 14 | PIPELINE | Plan/proposal index | 3 | 1 | 5 | 15 | doc |
| 15 | PIPELINE | Session-start test snapshot hook | 3 | 2 | 3 | 18 | hook |

### Detail: Top 5

**#1: Pre-edit downstream reference check** (Score: 80)
Before any Edit/Write that renames a string, section, or constant, grep `evals/` + all hook scripts for the old value. Could be implemented as a PreToolUse hook advisory (warn, not block) or as a mandatory step in flow skills. Sessions b8458acc, f1e40ee5, 337dd2da all hit this. Single highest-impact improvement.
- **Measure:** Count of rename→eval-failure cycles per session (target: 0)

**#2: Fix test isolation for hook state** (Score: 75)
Add a session-level `autouse` fixture in `conftest.py` that resets `fix-attempt-tracker.state` (and any other hook state files) before every test class. This eliminates the most persistent cross-session verification issue.
- **Measure:** Zero flaky test reruns needed per session (target: 0, current: ~1-2 per session)

**#3: Settings.json hook wiring memory** (Score: effective 100 by waste)
Create a memory entry documenting: hook groups (PreToolUse, PostToolUse, Stop, SessionEnd), matcher patterns, command template with `$CLAUDE_PROJECT_DIR`, and which hooks are currently wired. Re-read in 4+ sessions at ~10 tool calls each.
- **Measure:** Reads of settings.json per session (target: ≤1, current: 2-4)

**#4: 3-probe-then-ask escalation rule** (Score: 60)
After 3 failed environment/hardware probes, ask the user before continuing to investigate. Add to CLAUDE.md or flow skills. Would have saved 25+ tool calls in 02bbfd93.
- **Measure:** Environment debugging tool calls before user query (target: ≤3)

**#5: Baseline test failures in state snapshot** (Score: 48)
Extend the state snapshot hook to record which tests are currently failing at session start. Prevents agents from wasting time investigating pre-existing failures (sessions b8458acc, ebea2df6).
- **Measure:** Tool calls spent on pre-existing test failures (target: 0)

---

## Aggregate Statistics

| Metric | Value |
|--------|-------|
| Sessions analyzed | 8 |
| Total tool calls | ~876 |
| Estimated waste | ~15% weighted average |
| Bugs introduced | 17 |
| Caught by tests | 47% |
| Caught by verification | 35% |
| Escaped | 18% (3 bugs) |
| Efficiency scores | 2×5, 3×4, 3×3 (avg 3.9) |
| Quality scores | 1×5, 5×4, 1×3, 1×4 (avg 4.0) |
| Learning scores | 1×5, 3×4, 2×3, 1×2 (avg 3.5) |

### What's working well
1. **Structured handoff prompts** — sessions with detailed handoff prompts (f1e40ee5, ebea2df6) scored 5/5 efficiency and completed 12-13 tasks each
2. **2-mutation-then-test discipline** — hook-enforced cadence prevented compound errors in all implementation sessions
3. **Parallel subagent research** — when given specific extraction prompts, subagents delivered high-ROI results (beat-link API root cause, context audit data table)

### What needs work
1. **Pre-edit reference checking** — the single most common rework pattern across the sprint
2. **Test isolation** — hook state leaking across tests was discovered and worked around 3 times without root-causing
3. **Knowledge persistence** — structural information about THE_FACTORY is re-discovered every session

---

## Meta-Observations

1. **The v2.2→v3.0 sprint was unusually compressed** (all 8 sessions in one day). This means cross-session learning had no chance to happen via memory — each session started cold. Under normal pacing with days between sessions, memory writes would have more time to accumulate.

2. **The extraction-based analysis (JSONL→condensed narrative) lost some nuance.** Tool call timing and interleaving are flattened. A future improvement: include wall-clock time gaps between tool calls to identify pauses/waiting.

3. **Lens D (Prompt Linguistics) was removed from this analysis.** The operator's language was consistent across sessions (direct, low-emotion, front-loaded directives). A linguistic lens would have low signal for this sprint because the operator style was uniform.

4. **The highest-scoring sessions (f1e40ee5, ebea2df6) shared one trait:** they received structured handoff prompts from the prior session, not raw user instructions. This suggests the handoff format is the single highest-leverage process artifact.
