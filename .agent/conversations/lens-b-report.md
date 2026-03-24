# Lens B: Quality & Correctness Analysis

**Date:** 2026-03-24
**Sessions analyzed:** 25 (13 coding sessions with >5 edits, 12 research/small sessions)
**Analyst:** Claude Opus 4.6 (Lens B subagent)

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Sessions analyzed | 25 |
| Coding sessions (>5 edits) | 13 |
| Total edits (Write + Edit) | 621 |
| TypeScript type errors encountered | 9 |
| Build errors encountered | 12 |
| Import/module errors encountered | 3 |
| Fix-attempt-tracker hook blocks | 13 |
| Test suite runs observed | 87 |
| Test suite failures observed | 22 |
| Agent self-corrections detected | 2 |
| User-initiated corrections | 0 (substantive) |
| **Estimated defect rate** | **~0.7 bugs-requiring-fix per coding session** |

### Defect Classification

| Defect Type | Count | Sessions Affected |
|-------------|-------|-------------------|
| TypeScript type mismatch / undeclared property | 9 | 99ffb4e3, 0c73b5f7, 495b5994, 9a419670, 588a6128 |
| Build tool version incompatibility | 4 | 7f03b0df, 588a6128 |
| Import / module not found | 3 | 588a6128 |
| Environment variable misconfiguration | 2 | 99ffb4e3 |
| Canvas/DOM interaction failures (preview) | 3 | 495b5994 |
| Test infrastructure issues (set -e, python path) | 4 | 99ffb4e3, c3838b2f, 4733ad72 |

---

## Per-Session Quality Analysis

### Session 1: `1a82dd5b` (THE_FACTORY - Pipeline critique + v2 setup)
- **Edits:** 65 | **Test runs:** 30 | **Test failures:** 8
- **Quality notes:** High test failure count but these were from building the eval suite itself -- the agent wrote tests, ran them, and iterated. Test failures were caught and fixed within the session. No user complaints.
- **Quality score:** 3/5 -- failures were expected during eval suite construction, but the 8 failures suggest writing tests without verifying expectations first.

### Session 2: `7f03b0df` (THE_FACTORY - AnnaPlanna scaffold)
- **Edits:** 43 | **Build errors:** 1 | **Hook blocks:** 2
- **Quality notes:** Built entire Supabase integration that user then asked to remove -- a spec adherence failure. Tailwind v4 installed despite Node 20.18 incompatibility (version was not checked before install). The Supabase teardown was clean. Fix-attempt-tracker fired twice.
- **Quality score:** 3/5 -- the Supabase misread is the biggest quality gap; no code bugs, but wasted effort on wrong assumptions.

### Session 3: `99ffb4e3` (CRUCIBLE - Agent infra + integration tests)
- **Edits:** 62 | **TS errors:** 3 | **Build errors:** 4 | **Test failures:** 4
- **Quality notes:** Langfuse env var name wrong (`LANGFUSE_HOST` vs `LANGFUSE_BASE_URL`). The `set -e` + `pipefail` interaction caused false test failures -- agent diagnosed this correctly after 2 iterations. API key echo in terminal is a security incident. Multiple teardown.ts edit cycles (6 edits on one file).
- **Quality score:** 3/5 -- env var mismatch and `set -e` interaction are real bugs; security incident with API key echo is notable.

### Session 4: `1b2da80d` (SCUE - Strata Phase 2)
- **Edits:** 22 | **No test failures**
- **Quality notes:** Clean session. Preview server startup took 3 attempts but this was infrastructure, not code bugs. One self-correction detected. API endpoint mismatch diagnosed via network request debugging.
- **Quality score:** 4/5 -- well-executed phased delivery with minimal defects.

### Session 5: `0c73b5f7` (SCUE - Waveform rendering tuning)
- **Edits:** 30 | **TS errors:** 2 | **Build errors:** 2
- **Quality notes:** Heavy upfront reading (21 Read calls before first Write) correlated with clean implementation. The 2 TS errors were caught by typecheck before preview. No regressions.
- **Quality score:** 4/5 -- the read-first approach paid off in correctness.

### Session 6: `63561724` (SCUE - Waveform frequency analysis)
- **Edits:** 4 | **Research session**
- **Quality notes:** Primarily research. One user correction ("not quite") was about research direction, not code bugs.
- **Quality score:** 4/5 -- well-scoped research.

### Session 7: `495b5994` (SCUE - Annotation followup)
- **Edits:** 72 | **TS errors:** 1 | **Build errors:** 1 | **13 error sequences**
- **Quality notes:** This is the most quality-challenged coding session. 13 distinct error sequences, many involving preview tool failures (canvas interactions, element click misses, eval syntax errors). The agent spent ~40 preview_eval calls debugging visual rendering issues. Beatgrid line drawing required 4+ edit cycles on drawBeatgridLines.ts. Launch.json server name mismatch ("scue-backend" vs "backend") caused startup failure. Element selector `table tbody tr:first-child` failed to register clicks.
- **Quality score:** 2/5 -- excessive edit-preview-edit loops without root-cause analysis; many issues could have been caught with typecheck/console-log before visual debugging.

### Session 8: `9a419670` (SCUE - Arrangement engine proposal)
- **Edits:** 45 | **TS errors:** 1
- **Quality notes:** Proposal document underwent 20+ sequential Edit() calls -- while not a correctness issue, this approach risks inconsistency between edits. One TS error caught and fixed.
- **Quality score:** 3/5 -- document quality was good but the editing approach was fragile.

### Session 9: `bca50125` (CRUCIBLE - stub session)
- **Quality score:** N/A -- 6 messages, no meaningful work.

### Session 10: `12c56fb3` (THE_FACTORY - Conversation export)
- **Quality score:** N/A -- utility session, 2 edits.

### Session 11: `c3838b2f` (THE_FACTORY - Pipeline v2 migration)
- **Edits:** 89 | **Build errors:** 1 | **Test runs:** 29 | **Test failures:** 9
- **Quality notes:** Highest edit count. Test failures were largely deliberate -- building a 42-test eval suite where initial failures guided implementation. 3 legitimate test failures caught real issues: (1) model file missing dataclass, (2) print() in source files that should be excluded, (3) skill file paths mismatched trigger table. All 3 were fixed correctly. The agent correctly identified that test failures were "evals catching real issues" rather than bugs in the tests.
- **Quality score:** 4/5 -- the test-driven approach worked well; the agent distinguished between test bugs and real issues effectively.

### Session 12: `588a6128` (THE_FACTORY - PABProject / Tinyshop)
- **Edits:** 83 | **TS errors:** 2 | **Build errors:** 3 | **Import errors:** 2 | **Hook blocks:** 8
- **Quality notes:** Most hook blocks of any session (8). Repeated Tailwind v4 incompatibility (same as session 2 -- a regression of unpersisted knowledge). `UploadResponse` type missing `filename` property (TS2339) was a genuine type safety bug -- the agent wrote code referencing a field that didn't exist on the type. The fix-attempt-tracker correctly blocked further edits, forcing test runs. Node version incompatibility hit again (20.18 vs Vite 8 requirement).
- **Quality score:** 2/5 -- repeated known issues (Tailwind v4, Node version), type safety gap with UploadResponse, 8 hook blocks indicate the agent was writing code faster than it could verify.

### Session 13: `48a05e83` (SongFormer research)
- **Quality score:** 5/5 -- clean research, no code.

### Session 14: `4733ad72` (SCUE continuation + ground truth)
- **Edits:** 25 | **Hook blocks:** 3 | **Test runs:** 7 | **Test failures:** 1
- **Quality notes:** Loaded wrong project context from state-snapshot (Tinyshop instead of SCUE). 16 tests written and all passing. Feature flow skill loaded but abandoned. 3 hook blocks indicate edit-before-test tendency.
- **Quality score:** 3/5 -- state-snapshot leading to wrong context is a correctness-adjacent issue; otherwise clean.

### Sessions 15-25: Research/small sessions
- Quality scores range 4-5/5. No meaningful defects in research-only sessions.

---

## Top 3 Quality Anti-Patterns

### 1. Edit-Before-Verify Loops (affects 4 sessions: 588a6128, 495b5994, 4733ad72, 7f03b0df)

The agent frequently writes multiple file edits before running typecheck, build, or tests. The fix-attempt-tracker hook fires 13 times across the corpus, meaning the agent attempted 4+ consecutive edits without verification at least 13 times. In session 588a6128, this happened 8 times in a single session.

**Evidence:**
- Session 588a6128: 8 hook blocks, TS2339 error on `UploadResponse.filename` that would have been caught by a single `tsc --noEmit`
- Session 495b5994: 13 error sequences, many from writing code then discovering via visual preview that it didn't work
- Session 4733ad72: 3 hook blocks, agent tried `python` instead of `.venv/bin/python` repeatedly

**Impact:** Each edit-before-verify cycle wastes ~3-5 tool calls (edit, discover error, read error, re-edit). Across 13 occurrences, this is ~50-65 wasted tool calls.

**Recommendation:** Add a pre-edit skill step: "Before editing, verify the last edit compiled. If no build/typecheck has run since the last edit, run one before making the next edit." The fix-attempt-tracker hook already enforces this after 3 edits -- consider lowering the threshold to 2.

### 2. Repeated Environment Incompatibility (affects 2 sessions: 7f03b0df, 588a6128)

The same Tailwind v4 + Node 20.18 incompatibility was hit in sessions 7f03b0df and 588a6128. The first session discovered that Tailwind 4's Vite plugin approach doesn't work and requires Tailwind 3 + PostCSS. The second session hit the exact same issue, spending ~10 tool calls re-discovering and re-fixing it.

Additionally, Vite 8 requires Node 20.19+, which was hit in both sessions. The Langfuse `LANGFUSE_HOST` vs `LANGFUSE_BASE_URL` env var mismatch in 99ffb4e3 is the same pattern -- an environment fact that should have been persisted.

**Impact:** ~20 wasted tool calls across 2 sessions, plus user frustration from watching the same failure repeat.

**Recommendation:** Create an environment compatibility memory file (e.g., `LEARNINGS.md` or `.agent/environment.md`) that records: Node version constraints, framework version pins, and env var naming conventions. The project-scaffold skill should check this file before installing dependencies.

### 3. Visual Debugging Without Structured Diagnostics (affects 2 sessions: 495b5994, 1b2da80d)

In session 495b5994, the agent used ~40 preview_eval calls to debug canvas rendering issues. The pattern was: edit code -> take screenshot -> examine screenshot -> edit again. This "visual debugging" approach is slow and imprecise. Console logs, typecheck output, and structured assertions catch most rendering bugs faster.

Specific failures:
- `preview_eval` threw `SyntaxError: Identifier 'canvas' has already been declared` (agent re-declared a variable)
- Element click `table tbody tr:first-child` failed to select a track (wrong selector)
- Beatgrid lines not rendering -- agent didn't check console logs first, went straight to visual inspection

**Impact:** Session 495b5994 consumed 323 tool calls (the third highest), with perhaps 40% spent on visual debugging loops.

**Recommendation:** Add to the debug-flow skill: "For rendering bugs, first check (1) console errors, (2) typecheck, (3) component props. Only use visual preview for final verification after the diagnostic checks pass."

---

## Top 3 Quality Wins

### 1. Read-First Implementation (Session 0c73b5f7 - Waveform Tuning)

Session 0c73b5f7 executed 21 Read calls before the first Write. This heavy upfront context loading resulted in one of the cleanest coding sessions: only 2 TS errors (caught by typecheck before preview), no regressions, no user corrections. The spec was followed precisely.

**Why it worked:** By understanding the existing codebase thoroughly before making changes, the agent avoided the type mismatches and integration failures that plagued other sessions.

**Recommendation:** Formalize this as a guideline: "For implementation tasks, read at least the target file, its imports, and its consumers before writing any code."

### 2. Test-Driven Eval Suite Construction (Session c3838b2f - Pipeline v2)

Despite having the highest edit count (89) and 9 test failures, session c3838b2f had strong quality outcomes. The agent built a 42-test eval suite and used test failures as a diagnostic tool -- when tests failed, it correctly distinguished between "the test caught a real issue" and "the test itself has a bug." Three real issues were caught: a model file missing dataclass annotation, print() calls in library code, and mismatched skill file paths in the trigger table.

**Why it worked:** Test failures drove discovery. The agent treated failures as information, not obstacles, and fixed root causes rather than papering over them.

### 3. Fix-Attempt-Tracker Hook as Quality Gate (Sessions 588a6128, 4733ad72)

While the fix-attempt-tracker generated 13 blocks, each block successfully forced the agent to verify its work before continuing. In session 588a6128, block #2 triggered a `npm run build` that caught the `UploadResponse.filename` type error. In session 4733ad72, blocks forced test runs that confirmed 16 tests were passing.

**Why it worked:** Deterministic enforcement (hooks) is more reliable than prompt-level discipline. The agent sometimes ignored the spirit of "verify before continuing" but the hook prevented runaway edit cycles.

---

## Defect Rate Analysis

| Category | Sessions | Defects Found | Rate |
|----------|----------|---------------|------|
| Coding sessions (>5 edits) | 13 | 9 | 0.69 per session |
| Research sessions | 12 | 0 | 0.00 per session |
| All sessions | 25 | 9 | 0.36 per session |

**Defect definition:** A bug that required a fix (not test infrastructure issues or deliberate TDD failures). The 9 defects are:
1. Supabase built without user confirmation (7f03b0df) -- spec adherence
2. Tailwind v4 incompatibility, first occurrence (7f03b0df) -- environment
3. Langfuse env var mismatch (99ffb4e3) -- configuration
4. `set -e` + `pipefail` false failure (99ffb4e3) -- shell scripting
5. Tailwind v4 incompatibility, repeat (588a6128) -- unpersisted learning
6. `UploadResponse.filename` type error (588a6128) -- type safety
7. Vite 8 / Node 20.18 incompatibility (588a6128) -- environment
8. launch.json server name mismatch (495b5994) -- configuration
9. State-snapshot loading wrong project context (4733ad72) -- infrastructure

**Escape rate:** 0 defects escaped to the user as unnoticed bugs. All were caught within the session, either by the agent, the build system, or the test suite. The hook system and build verification processes are working as intended for defect detection. The issue is prevention, not detection.

---

## Type Safety & Correctness Observations

- **TypeScript strictness is effective.** The 9 TS errors across the corpus were all caught by `tsc` before runtime. No runtime type errors were observed.
- **No `any` type abuse detected.** The agent used proper TypeScript types throughout.
- **Error handling gaps:** Not observed as a pattern. The agent generally added try/catch and error boundaries.
- **Null/undefined checks:** Not a significant issue. React components handled loading states appropriately.

---

## Actionable Recommendations

1. **Lower fix-attempt-tracker threshold from 3 to 2.** The data shows that 3 consecutive edits without verification is too permissive -- most bugs are introduced in the first 2 edits after a context switch. A threshold of 2 would catch issues earlier.

2. **Create an environment compatibility LEARNINGS file.** Persist Node version, framework version pins (Tailwind 3, Vite <=6), and env var naming conventions. Auto-check this file during project scaffolding.

3. **Add "diagnostic before visual" to debug-flow.** Before using preview screenshots for debugging, require: (a) `tsc --noEmit`, (b) console error check, (c) network request check. Only use visual preview for final verification.

4. **Enforce typecheck before preview_start.** Add a hook or skill guideline that requires a passing typecheck before launching preview servers. This would have prevented several error sequences in sessions 495b5994 and 588a6128.

5. **Scope state-snapshot to active project.** Session 4733ad72 loaded Tinyshop context when the task was SCUE. The state snapshot should either (a) scope to the project the user mentions, or (b) prompt for confirmation when loaded context doesn't match the stated task.
