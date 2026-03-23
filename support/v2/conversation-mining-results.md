# Conversation Mining Results — Phase 0 of v2 Migration

**Date:** 2026-03-23
**Sessions analyzed:** 20 (top by content size from 148 extracted)
**Method:** Three parallel lens agents (Process Efficiency, Quality & Correctness, Learning & Knowledge) each sampled all 20 transcripts, then findings were synthesized and cross-referenced with PROTOCOL_IMPROVEMENTS.md.

---

## Cross-Lens Patterns

These findings appear in multiple lenses — they're the highest-signal items because they affect efficiency, quality, and knowledge simultaneously.

### Pattern 1: No Persistent Project State Between Sessions
- **Lens A:** 10% of all tokens spent on context ramp-up. Every session re-reads CLAUDE.md, milestones, specs, task trackers, codebase structure.
- **Lens C:** 1500+ wasted tool calls across 20 sessions from re-exploring SCUE file structure. 15 of 20 sessions begin with 50-150 tool calls of exploration.
- **Root cause:** No mechanism carries "what I learned about this project" from session N to session N+1.
- **PROTOCOL_IMPROVEMENTS.md alignment:** [FRICTION] B3 — "Large implementation tasks that get interrupted lose all pre-loaded context."
- **Evidence sessions:** 5c936ae2 (discovered Analysis Viewer already built after extensive exploration), 8d5678e1 (found 3 tasks already done), bdab0578 (18 reads before first edit), 55c4677e (20 reads before first edit), 7fa2c863 (30+ reads before first edit)

### Pattern 2: API Misuse from Missing Reference Docs
- **Lens B:** API misuse is the #1 bug type — 7 instances across 4 sessions. Methods that don't exist, wrong argument patterns, misunderstood return types.
- **Lens C:** beat-link API specifics repeatedly researched via WebSearch (4 sessions, 400+ wasted tool calls). Each session re-discovers the same API details.
- **Root cause:** No API reference for external dependencies. Agents resort to WebSearch, source reading, and trial-and-error.
- **PROTOCOL_IMPROVEMENTS.md alignment:** [FRICTION] B1 — "Java bridge API discovery requires `javap` on cached Gradle JARs. Three tool calls needed just to find the correct method name."
- **Evidence sessions:** 3dd385ca (100-msg subagent for CdjStatus research), 1f74f457 (beat-link upgrade required reading source), b2de4e44 (236-msg subagent for DLP protocol), 5c936ae2 (async def vs def API misuse)

### Pattern 3: Normalized Test Failures Hide New Regressions
- **Lens B:** 2 TestBatchJobLifecycle failures carried across 3+ sessions as "same pre-existing failures." Layer 1 tests skipped in most sessions due to missing numpy.
- **Lens C:** Task tracker staleness means agents can't distinguish "known broken" from "newly broken."
- **Root cause:** No "zero known failures" gate. Broken tests become invisible background noise.
- **PROTOCOL_IMPROVEMENTS.md alignment:** [BUG] B4 — "Task marked 'ready for dispatch' despite functional bug. Typecheck passed but code was broken."
- **Evidence sessions:** 5c936ae2 (accepted pre-existing failures), 7fa2c863 (same), bdab0578 (missing psutil rediscovered)

### Pattern 4: Redundant Subagent Exploration
- **Lens A:** #1 anti-pattern. Up to 29 subagents in one session, many reading overlapping files. Estimated 8% of total tokens wasted.
- **Lens C:** Research subagents independently re-trace the same data flows (track resolution, bridge lifecycle) because they don't know what other agents already found.
- **Root cause:** Subagents have no shared awareness. No mechanism to say "agent X already read these files."
- **Evidence sessions:** 3dd385ca (29 subagents, 6 launched at same timestamp reading overlapping files), 7fa2c863 (7 agents, glob typos causing re-exploration), 0eed7a89 (duplicate "Read backend bridge files" agents), 9a291fdc (12 subagents for 48 main tool calls)

### Pattern 5: Cold-Tier Documentation Doesn't Prevent Bug Recurrence
- **Lens B:** ADR-018 waveform anti-pattern re-introduced in EventTimeline despite being documented and already fixed in WaveformCanvas.
- **Lens C:** Unpersisted knowledge — XDJ-AZ garbage BPM, Finder start order, DLP device handling — known from prior sessions but not in any skill or hook.
- **Root cause:** ADRs and docs are "write once, hope agents read" artifacts. Structural prevention (shared components, hooks, lints) is the only reliable gate.
- **PROTOCOL_IMPROVEMENTS.md alignment:** [GAP] B2 — "ADR-018 documents correct waveform rendering but no automated check prevents the anti-pattern from recurring."
- **Evidence sessions:** 5c936ae2 (self-reported ADR-018 violation), multiple sessions rediscovering XDJ-AZ quirks

---

## Ranked Improvements

Scored by impact (1-5) × frequency (1-5) × feasibility (1-5). Max score = 125.

| Rank | Category | Title | Impact | Freq | Feas | Score | Type |
|------|----------|-------|--------|------|------|-------|------|
| 1 | PIPELINE | Session-start state snapshot + codebase orientation skill | 5 | 5 | 4 | 100 | skill + hook |
| 2 | PIPELINE | External API reference docs (beat-link, pyrekordbox) | 4 | 4 | 5 | 80 | skill augmentation |
| 3 | PIPELINE | Zero known failures gate | 5 | 4 | 4 | 80 | hook + eval |
| 4 | PIPELINE | Subagent scope deduplication guidance | 4 | 4 | 3 | 48 | skill |
| 5 | PROJECT | Fix layer1 test environment (numpy) | 4 | 4 | 3 | 48 | project fix |
| 6 | PIPELINE | Feature-completion quick-check in landing procedure | 4 | 3 | 4 | 48 | convention |
| 7 | PIPELINE | Shared waveform rendering component (structural ADR enforcement) | 5 | 2 | 3 | 30 | project refactor |
| 8 | PIPELINE | Preview/UI verification skill (reduce thrashing) | 3 | 3 | 3 | 27 | skill |
| 9 | PIPELINE | Pre-session health check hook (typecheck + pytest) | 3 | 3 | 3 | 27 | hook |
| 10 | PROJECT | Declare all Python dependencies (import audit) | 3 | 2 | 4 | 24 | eval + CI |

### Improvement Details

#### 1. Session-Start State Snapshot + Codebase Orientation Skill (Score: 100)

**What:** Two complementary artifacts:
- A **codebase orientation skill** (`scue/skills/codebase-orientation.md`) loaded at session start for any SCUE work. Contains: file-to-responsibility map, data flow chains, feature completion status, key gotchas.
- A **state snapshot** (`.agent/state-snapshot.json`) written during landing procedure. Contains: current branch, last commit, active tasks, flow phase, key files modified, open blockers.

**Why:** Eliminates the 10% ramp-up cost that hits 100% of sessions (Lens A) and the 1500+ wasted exploration tool calls (Lens C). This is the single change that would most reduce waste across the entire corpus.

**How to measure:** Count Read/Glob/Explore calls before first Edit in future sessions. Target: <5 (currently 15-30).

#### 2. External API Reference Docs (Score: 80)

**What:** Augment `skills/beat-link-bridge.md` and `skills/pioneer-hardware.md` with:
- CdjStatus method return types and units (BPM, not BPM*100; ms, not seconds)
- Finder lifecycle and start order (TimeFinder before MetadataFinder before BeatGridFinder)
- XDJ-AZ quirks (658.63 BPM when no track, BLUE-style waveforms not THREE_BAND)
- DLP vs non-DLP device handling
- pyrekordbox field units and gotchas

**Why:** API misuse is the #1 bug type (7 instances). Most of these bugs were preventable if the agent had a reference doc instead of relying on WebSearch.

**How to measure:** Count WebSearch/WebFetch calls for beat-link topics in future sessions. Target: 0 (currently 6-14 per research episode).

#### 3. Zero Known Failures Gate (Score: 80)

**What:**
- Fix or explicitly skip (with tracked issue) the 2 TestBatchJobLifecycle failures
- Fix the numpy environment issue so layer1 tests run
- Add a hook or convention: `pytest` must exit 0. No "same pre-existing failures" accepted.
- Pre-session health check runs `npm run typecheck` + `pytest -q` to surface state immediately.

**Why:** Normalized failures hide new regressions. Two bugs persisted across 3+ sessions because agents accepted "2 failed, 193 passed — same as before" as passing.

**How to measure:** Pre-existing failures at session start. Target: 0.

#### 4. Subagent Scope Deduplication (Score: 48)

**What:** Add guidance to flow skills: when launching parallel Explore subagents, give each a specific file scope (e.g., "read only `bridge/` files", "read only `frontend/src/components/`"). Don't launch two agents with overlapping directories.

**Why:** 8% of tokens wasted on redundant subagent exploration. The worst sessions (3dd385ca, 9a291fdc) had subagents reading the same files in parallel.

**How to measure:** Count overlapping file reads across subagents in a session.

#### 5. Fix Layer1 Test Environment (Score: 48)

**What:** Add numpy (and any other missing deps) to the dev/test environment so `test_layer1/` actually runs.

**Why:** The core analysis pipeline has weaker test coverage than the bridge layer. Skipping layer1 tests means analysis bugs escape to production.

#### 6. Feature-Completion Quick-Check in Landing Procedure (Score: 48)

**What:** During "Land the Plane," update the codebase orientation skill's feature status section. Mark what was built, what was verified, what remains.

**Why:** Session 5c936ae2 wasted significant time planning to implement a feature that was already complete. Task tracker wasn't updated from the prior session.

#### 7-10: Lower priority improvements documented above.

---

## Efficiency Metrics (Baseline)

From Lens A analysis across 20 sessions (~3,200 tool calls):

| Waste Category | Estimated % | Tool Calls |
|---|---|---|
| Context ramp-up | 10% | ~320 |
| Redundant subagent exploration | 8% | ~256 |
| Research over-fetching | 3% | ~96 |
| Preview/UI thrashing | 3% | ~96 |
| Search pattern failures | 2% | ~64 |
| **Total estimated waste** | **~25%** | **~800** |

## Quality Metrics (Baseline)

From Lens B analysis:

| Bug Type | Instances | Sessions |
|---|---|---|
| API misuse | 7 | 3dd385ca, 5c936ae2, 1f74f457, 8d5678e1 |
| Logic error | 4 | 3dd385ca, 2f753841 |
| Spec misunderstanding | 3 | 3dd385ca, 7fa2c863, bdab0578 |
| Type error | 1 | 5c936ae2 |
| Integration issue | 1 | bdab0578 |

- **Bugs caught in-session:** 12 of 16 (75%)
- **Bugs escaped:** 4 of 16 (25%) — mostly pre-existing failures carried forward
- **Verification gap:** No session ran full integration tests (FE + BE together)

## Knowledge Metrics (Baseline)

From Lens C analysis:

| Knowledge Gap | Sessions Affected | Est. Wasted Tool Calls |
|---|---|---|
| SCUE codebase orientation | 15 | 1500+ |
| Feature completion status | 5 | 500+ |
| beat-link API specifics | 4 | 400+ |
| Track resolution data flow | 4 | 200+ |
| Bridge lifecycle state machine | 3 | 150+ |

## Efficiency Wins to Preserve

1. **Parallel subagent research for independent domains** — works well when scopes don't overlap (5c936ae2, 46aa0cda)
2. **Feature-flow skill structure** — sessions following the flow have 5-12% waste vs 15-25% for unstructured sessions
3. **Greenfield generative sessions** — lowest waste (~5%). Reading specs then writing code is the most efficient pattern.

---

## How These Findings Feed v2 Migration

| Finding | v2 Migration Phase | Action |
|---|---|---|
| Session state snapshot | Phase 1 (Observability) | Write snapshot in Langfuse Stop hook |
| Codebase orientation skill | Phase 2 (Eval/Skills) | Create skill, add to trigger table |
| API reference docs | Phase 2 (Eval/Skills) | Augment existing skills |
| Zero failures gate | Phase 1 (Observability) | Add as hook enforcement |
| Subagent dedup | Phase 3 (Slim Constitution) | Add guidance to flow skills |
| Baseline metrics | Phase 4 (Experiments) | Use as pre-migration baseline for A/B comparison |

These baselines (25% waste, 75% bug catch rate, 15-30 reads before first edit) become the "before" measurements that the experiment framework in Phase 4 will compare against.
