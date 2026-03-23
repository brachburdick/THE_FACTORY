# v1.10 Review Process — Full Diagram

## Overview: Three Processes → One Ranked Improvement List

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        v1.10 IMPROVEMENT CYCLE                              │
│                                                                             │
│  ┌──────────────┐   ┌──────────────────┐   ┌────────────────────┐          │
│  │  PROCESS 1   │   │   PROCESS 2      │   │   PROCESS 3        │          │
│  │  Conversation │   │   Project Quality │   │   Human-Sourced    │          │
│  │  Analysis     │   │   Assessment      │   │   Observations     │          │
│  │              │   │                  │   │                    │          │
│  │  Input:      │   │  Input:          │   │  Input:            │          │
│  │  transcripts │   │  codebase        │   │  PROTOCOL_         │          │
│  │              │   │                  │   │  IMPROVEMENTS.md   │          │
│  │  Output:     │   │  Output:         │   │  + project-        │          │
│  │  process     │   │  scored rubric   │   │  observations.md   │          │
│  │  patterns    │   │  per module      │   │                    │          │
│  └──────┬───────┘   └────────┬─────────┘   └─────────┬──────────┘          │
│         │                    │                        │                     │
│         ▼                    ▼                        ▼                     │
│  ┌──────────────────────────────────────────────────────────────┐           │
│  │                    FINAL SYNTHESIS                            │           │
│  │  Combine all three streams into one ranked improvement list  │           │
│  │  Split into: PROJECT improvements vs PIPELINE improvements   │           │
│  └──────────────────────────┬───────────────────────────────────┘           │
│                             │                                               │
│                             ▼                                               │
│  ┌──────────────────────────────────────────────────────────────┐           │
│  │                    OPERATOR TRIAGE                            │           │
│  │  ACCEPT / DEFER / REJECT each suggestion                     │           │
│  │  Record rationale (trains future auto-triage)                │           │
│  └──────────────────────────┬───────────────────────────────────┘           │
│                             │                                               │
│                             ▼                                               │
│  ┌──────────────────────────────────────────────────────────────┐           │
│  │                    EXECUTE                                    │           │
│  │  Eval cases → Implementation prompts → Apply → Verify        │           │
│  └──────────────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Process 1: Conversation Analysis (Detail)

```
EXTRACT                    ANALYZE (parallel)              CONSOLIDATE
─────────                  ──────────────────              ───────────

~/.claude/projects/        Batch 1 (sessions 1-5)
       │                   ┌─────────────────────┐
       │                   │ Lens A (efficiency)  │──┐
       ▼                   │ Lens B (quality)     │──┤ 3 reports
scripts/extract-           │ Lens C (knowledge)   │──┘
  conversations.py         └─────────────────────┘
       │                   Batch 2 (sessions 6-10)
       │                   ┌─────────────────────┐
       ▼                   │ Lens A (efficiency)  │──┐
.agent/conversations/      │ Lens B (quality)     │──┤ 3 reports
  ├── index.jsonl          │ Lens C (knowledge)   │──┘
  ├── timeline.jsonl       └─────────────────────┘
  ├── <session>.md         Batch 3 (sessions 11-15)
  └── <session>.jsonl      ┌─────────────────────┐
                           │ Lens A (efficiency)  │──┐
  Select 20 most           │ Lens B (quality)     │──┤ 3 reports
  recent/richest           │ Lens C (knowledge)   │──┘
       │                   └─────────────────────┘
       │                   Batch 4 (sessions 16-20)
       ▼                   ┌─────────────────────┐
  Group into               │ Lens A (efficiency)  │──┐
  4 batches of 5           │ Lens B (quality)     │──┤ 3 reports
  by time proximity        │ Lens C (knowledge)   │──┘
                           └─────────────────────┘

                      STAGE 2: Per-category consolidation
                      ─────────────────────────────────

                      4× Lens A reports ──► EFFICIENCY REPORT  ──┐
                      4× Lens B reports ──► QUALITY REPORT     ──┤
                      4× Lens C reports ──► KNOWLEDGE REPORT   ──┘
                                                                  │
                      STAGE 3: Cross-category synthesis           │
                      ─────────────────────────────────           │
                                                                  │
                      3 consolidated reports ──────────────────────┘
                              │
                              ▼
                      PROCESS 1 OUTPUT:
                      Ranked process patterns
                      (what's working, what's not,
                       recurring friction, knowledge gaps)
```

### Model assignments for Process 1:

```
┌──────────────────────────────────────────────────────────┐
│ Task                    │ Model Tier    │ Cost/run       │
├──────────────────────────────────────────────────────────┤
│ Extraction              │ Script (free) │ $0             │
│ Lens A (efficiency)     │ Mid           │ ~$0.50-1.00   │
│ Lens B (quality)        │ Upper-mid     │ ~$1.00-2.00   │
│ Lens C (knowledge)      │ Upper-mid     │ ~$1.00-2.00   │
│ Stage 2 consolidation   │ Upper-mid     │ ~$1.00-2.00   │
│ Stage 3 synthesis       │ Frontier      │ ~$3.00-5.00   │
├──────────────────────────────────────────────────────────┤
│ Total (20 sessions)     │               │ ~$20-40       │
└──────────────────────────────────────────────────────────┘
```

---

## Process 2: Project Quality Assessment (Detail)

```
FOR EACH PROJECT (e.g., SCUE):

  DECOMPOSE by stack layer / module
  ────────────────────────────────

  SCUE
   ├── Frontend (React/TypeScript)
   │    ├── Waveform rendering module
   │    ├── Live deck monitor module
   │    ├── WebSocket client / state management
   │    └── UI components / styling
   │
   ├── Backend (Python/FastAPI)
   │    ├── Analysis engine (waveform processing)
   │    ├── API routes / endpoint design
   │    ├── WebSocket server / bridge communication
   │    └── Configuration / startup
   │
   ├── Bridge (Java JAR)
   │    ├── Beat-link integration
   │    ├── Waveform data extraction
   │    └── CDJ status monitoring
   │
   └── Infrastructure
        ├── Build / deploy / dev tooling
        ├── Testing coverage + patterns
        └── Documentation accuracy


  SCORE EACH MODULE independently
  ────────────────────────────────

  For each module:
  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │  Model A (Claude Opus)  ──► Scorecard A                  │
  │  Model B (GPT-5.3)     ──► Scorecard B    (independent,  │
  │  Model C (Gemini Pro)  ──► Scorecard C     no cross-     │
  │                                            contamination) │
  │          │                                               │
  │          ▼                                               │
  │  Synthesis agent ──► Module scorecard                    │
  │  (flag disagreements, preserve them)                     │
  │          │                                               │
  │          ▼ (only if disagreements >1 point)              │
  │  Position-swap tiebreaker ──► Resolved scorecard         │
  │                                                          │
  └──────────────────────────────────────────────────────────┘


  ADDITIONAL ASSESSMENT DIMENSIONS (whole-project, not per-module)
  ────────────────────────────────────────────────────────────────

  ┌────────────────────────────────────────────────────────┐
  │  Pipeline protocol compliance                          │
  │  (Does this project follow the constitution?)          │
  │  ─ Git protocol adherence                              │
  │  ─ Flow skill usage (debug/feature/refactor)           │
  │  ─ Session hygiene (run records, task tracker updates)  │
  │  ─ Skill/hook coverage vs. recurring manual work       │
  ├────────────────────────────────────────────────────────┤
  │  Project protocol compliance                           │
  │  (Does this project follow its own CLAUDE.md?)         │
  │  ─ Conventions stated but not followed                 │
  │  ─ Gotchas section accuracy (still relevant?)          │
  │  ─ Build/test commands accurate                        │
  ├────────────────────────────────────────────────────────┤
  │  Agent role/skill effectiveness                        │
  │  (Are the skills earning their context window?)        │
  │  ─ Which skills were loaded in the last 20 sessions?   │
  │  ─ Which skills were loaded but not used?              │
  │  ─ What recurring patterns lack a skill?               │
  └────────────────────────────────────────────────────────┘

  All module scorecards + protocol assessments
           │
           ▼
  PROCESS 2 OUTPUT:
  Per-project scored assessment with
  module-level granularity + protocol compliance
```

---

## Process 3: Human-Sourced Observations

```
  Accumulated over time between review cycles:

  PROTOCOL_IMPROVEMENTS.md (pipeline observations)
  ├── Self-assessment entries (B1-B6 tags)
  ├── Operator complaints / friction notes
  └── Ad-hoc observations during sessions

  <project>/.agent/project-observations.md (project observations)
  ├── Self-assessment entries (A1-A4 tags)
  └── Code review findings

           │
           ▼
  PROCESS 3 OUTPUT:
  Categorized observation list
  (already structured by A/B taxonomy)
```

---

## Final Synthesis + Execution

```
  Process 1 output ──┐
  (process patterns)  │
                      │
  Process 2 output ──┤──► FINAL SYNTHESIS AGENT (Frontier model)
  (scored rubrics)    │         │
                      │         │
  Process 3 output ──┘         │
  (observations)               ▼

                      ┌─────────────────────────────────┐
                      │  RANKED IMPROVEMENT LIST         │
                      │                                  │
                      │  Each item tagged:               │
                      │  ─ PROJECT or PIPELINE           │
                      │  ─ impact × frequency × ease     │
                      │  ─ evidence (which process,      │
                      │    which sessions, which scores)  │
                      │  ─ suggested implementation type  │
                      │    (skill/hook/refactor/conv/doc) │
                      └────────────────┬────────────────┘
                                       │
                                       ▼
                      ┌─────────────────────────────────┐
                      │  OPERATOR TRIAGE                 │
                      │                                  │
                      │  For each item:                  │
                      │  ✅ ACCEPT → create task         │
                      │  ⏸️  DEFER → next cycle           │
                      │  ❌ REJECT → note why            │
                      │                                  │
                      │  Record rationale for ALL        │
                      │  decisions (trains auto-triage)  │
                      └────────────────┬────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    │                                      │
                    ▼                                      ▼
          PROJECT improvements              PIPELINE improvements
                    │                                      │
                    ▼                                      ▼
          ┌─────────────────┐              ┌──────────────────────┐
          │ For each:       │              │ For each:            │
          │ 1. Write eval   │              │ 1. Write eval case   │
          │    case (FAIL)  │              │    (FAIL)            │
          │ 2. Write impl   │              │ 2. Update protocol   │
          │    prompt       │              │    docs / skills /   │
          │ 3. Execute via  │              │    hooks / CLAUDE.md │
          │    feature-flow │              │ 3. Propagate to      │
          │    or refactor  │              │    affected projects │
          │ 4. Run eval     │              │ 4. Run eval case     │
          │    case (PASS?) │              │    (PASS?)           │
          │ 5. Run full     │              │ 5. Run full evals    │
          │    test suite   │              │                      │
          └────────┬────────┘              └──────────┬───────────┘
                   │                                   │
                   └──────────────┬────────────────────┘
                                  │
                                  ▼
                   ┌──────────────────────────┐
                   │  VERIFY (next cycle)      │
                   │                           │
                   │  Re-run assessment        │
                   │  Compare scores to        │
                   │  pre-improvement baseline │
                   │                           │
                   │  Did scores improve?      │
                   │  Any regressions?         │
                   │  Eval cases still pass?   │
                   └──────────────────────────┘
```

---

## Queue-Ready Formula

For automation, each step is a discrete job with defined inputs/outputs:

```
JOB QUEUE (sequential stages, parallel within stages)
══════════════════════════════════════════════════════

STAGE 0: EXTRACT (1 job, no LLM)
  Input:  ~/.claude/projects/
  Output: .agent/conversations/*.md + index.jsonl
  Run:    python3 scripts/extract-conversations.py

STAGE 1: LENS ANALYSIS (12 jobs, all parallel)
  Input:  5 session markdown files per job
  Output: 1 structured lens report per job
  Run:    batch1-lensA, batch1-lensB, batch1-lensC,
          batch2-lensA, batch2-lensB, batch2-lensC, ...

STAGE 2: PER-CATEGORY CONSOLIDATION (3 jobs, all parallel)
  Input:  4 lens reports of same category
  Output: 1 consolidated category report
  Run:    consolidate-efficiency, consolidate-quality, consolidate-knowledge
  Depends: STAGE 1 complete

STAGE 3: CROSS-CATEGORY SYNTHESIS (1 job)
  Input:  3 consolidated category reports
  Output: Process 1 ranked pattern list
  Depends: STAGE 2 complete

STAGE 4: PROJECT ASSESSMENT (N×3 jobs, parallel per module)
  Input:  codebase module + rubric
  Output: 1 scorecard per model per module
  Run:    scue-frontend-opus, scue-frontend-gpt, scue-frontend-gemini,
          scue-backend-opus, scue-backend-gpt, scue-backend-gemini, ...
  Depends: nothing (can run parallel with stages 1-3)

STAGE 5: ASSESSMENT SYNTHESIS (N jobs, parallel per module)
  Input:  3 scorecards per module
  Output: 1 synthesized module scorecard (with disagreements)
  Depends: STAGE 4 complete

STAGE 6: COLLECT OBSERVATIONS (1 job, no LLM)
  Input:  PROTOCOL_IMPROVEMENTS.md + project-observations.md files
  Output: categorized observation list
  Depends: nothing

STAGE 7: FINAL SYNTHESIS (1 job, frontier model)
  Input:  Process 1 output + Process 2 output + Process 3 output
  Output: ranked improvement list (project + pipeline split)
  Depends: STAGES 3, 5, 6 complete

STAGE 8: TRIAGE (human)
  Input:  ranked improvement list
  Output: accepted/deferred/rejected items with rationale

STAGE 9: EXECUTE (N jobs, sequential per improvement)
  Input:  implementation prompt + eval case
  Output: code/protocol changes + passing eval
  Depends: STAGE 8 complete
```
