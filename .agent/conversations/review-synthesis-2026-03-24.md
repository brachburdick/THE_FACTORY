# Review Cycle Synthesis — 2026-03-24

**Sessions analyzed:** 25 (21 substantive, 4 abandoned)
**Lenses:** A (Process Efficiency), B (Quality & Correctness), C (Learning & Knowledge)

---

## Cross-Lens Findings

### Signal Convergence (all 3 lenses agree)

1. **Edit-before-verify is the #1 anti-pattern.** Lens A calls it "Edit-Read-Edit cycling" (8 sessions). Lens B calls it "Edit-Before-Verify Loops" (4 sessions, 13 hook blocks). Lens C doesn't see it directly but notes the downstream effect: knowledge isn't consolidated before the next edit, so the same context gets re-read between edits. **All three lenses point to the same root cause: the agent writes code faster than it verifies.**

2. **Environment/version incompatibility is the #1 preventable defect.** Lens A flags it as the Tailwind v4 recurring failure (sessions 2, 12). Lens B counts it as 4 of 9 total defects. Lens C identifies it as the highest-value single memory file (Node 20.18 constraints). **A single LEARNINGS.md entry would have prevented 4 defects and saved ~40 tool calls.**

3. **SCUE component API re-reading is the #1 knowledge gap.** Lens A sees it as redundant file reads (10 sessions). Lens C quantifies it: 6 sessions, ~8000-12000 tokens wasted. Lens B doesn't flag it as a quality issue (the re-reading doesn't cause bugs), but it consumes context that could be used for verification. **A component API memory file is the highest-ROI infrastructure investment.**

4. **Short, spec-driven sessions consistently outperform long multi-objective sessions.** Lens A: sessions scoring 5/5 were all under 200 lines. Lens B: session 5 (read-first) had 0.0 defect rate vs session 7 at 13 error sequences. Lens C: sessions 13, 17, 21 had near-zero knowledge waste.

### Signal Divergence (lenses disagree or see different things)

1. **Agent() overuse** — Lens A flags this in 6 sessions (overhead for simple tasks). Lens B doesn't see it as a quality problem. Lens C sees it as sometimes valuable (parallel research). **Resolution: Agent() is good for parallel independent tasks, bad for serial tasks within operator capability.**

2. **Preview debugging loops** — Lens A and B both flag this (5 sessions, 40+ calls). Lens C doesn't see it. **This is purely a process/quality issue, not a knowledge gap — the agent knows how to debug, it just chooses the wrong tool first.**

3. **Fix-attempt-tracker threshold** — Lens B recommends lowering from 3 to 2. Lens A doesn't comment on the threshold. **The data supports 2: most bugs are introduced in the first 2 edits after a context switch.**

---

## Improvement Candidates (ranked by cross-lens impact)

### Tier 1: High impact, low effort (do this cycle)

| # | Candidate | Lenses | Est. ROI | Type |
|---|-----------|--------|----------|------|
| 1 | **Environment compatibility LEARNINGS.md** — Node 20.18, Vite <=6, Tailwind 3+PostCSS, Langfuse host URL | A,B,C | Prevents 4 defects, saves ~40 tool calls | memory |
| 2 | **SCUE component API reference** — WaveformCanvas, AnnotationTimeline, DeckWaveform props, data deps, draw pipeline | A,C | Saves ~8000-12000 tokens across 6+ sessions | memory |
| 3 | **"Diagnostic before visual" rule in debug-flow** — require typecheck + console_logs before preview_eval | A,B | Eliminates ~30% of preview calls in affected sessions | skill update |
| 4 | **Lower fix-attempt-tracker threshold to 2** | B | Catches bugs 1 edit earlier; 13 blocks in current data | hook config |

### Tier 2: Medium impact, medium effort (do if time permits)

| # | Candidate | Lenses | Est. ROI | Type |
|---|-----------|--------|----------|------|
| 5 | **Review-cycle skill** — three-lens process, session selection, batching, synthesis | C | Saves ~3000-5000 tokens per review cycle (3 cycles so far) | skill |
| 6 | **Claude Code conversation storage memory file** | C | Saves ~3500 tokens (researched twice already) | memory |
| 7 | **Edit() hygiene rule** — if >3 sequential Edit() on same file, use Write() | A | Reduces edit-cycling in 8 sessions | skill update |
| 8 | **Session scope guideline** — cap at 1-2 objectives per session | A | Sessions with 4+ objectives consistently score 2-3/5 | skill update |

### Tier 3: Lower impact or higher effort (backlog)

| # | Candidate | Lenses | Type |
|---|-----------|--------|------|
| 9 | Phase handoff prompt template | C | template |
| 10 | Project-convention alignment checker hook | C | hook |
| 11 | Dispatch template with absolute project paths | C | template |
| 12 | launch.json naming fix (scue-backend -> backend) | C | one-time fix |

---

## Metrics Baseline (for next review cycle comparison)

| Metric | Current Value | Source |
|--------|--------------|--------|
| Estimated waste % | 18-22% | Lens A |
| Defect rate (coding sessions) | 0.69/session | Lens B |
| Defect escape rate | 0% (all caught in-session) | Lens B |
| Fix-attempt-tracker blocks | 13 across 25 sessions | Lens B |
| Repeated research tokens | ~20,000-25,000 | Lens C |
| Component API re-reads | 6 sessions | Lens C |
| Eval suite size | 52 tests, 0 failures | Pipeline |
