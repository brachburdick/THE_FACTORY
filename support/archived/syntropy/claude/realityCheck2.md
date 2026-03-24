# Reality Check #2: Use the Real Pipeline as the Experiment Subject

**Date:** 2026-03-23
**Reviewer:** Claude Opus 4.6 (fresh context, reviewed full SYNTROPY/claude/ document set)

---

## Context

The user's actual goal is an EDM arrangement analysis tool: audio file → arrangement formula (section pattern + kick/snare/drums pattern + midbass pattern + vocals + etc). Experiment-001 tests decomposition on section boundary detection alone — stage 1 of that pipeline.

---

## Finding: The Experiment Tests the Wrong Complexity Band

Section boundary detection is a single-function, single-domain, known-algorithm task. Librosa has built-in boundary detection. A frontier model will almost certainly nail L0, producing the result: "decomposition isn't needed for tasks an LLM can one-shot." That's true but already obvious.

The arrangement formula tool has the decomposition challenges SYNTROPY was designed to address:

### 1. Stage interdependence
Section boundaries inform where to look for kick patterns. Kick patterns help disambiguate section types (a drop has a different kick pattern than a breakdown). The stages aren't cleanly sequential — they have feedback loops. This is where naive decomposition breaks down.

### 2. Heterogeneous algorithms
- Section detection: spectral novelty / agglomerative clustering
- Kick isolation: onset detection + frequency filtering (or source separation)
- Vocal detection: source separation (demucs)
- Bass pattern: pitch tracking on separated stem
- Each stage uses different libraries, has different failure modes, and needs different verification

### 3. Recombination is the hard part
Getting timestamps for sections, kicks, and bass individually is achievable. Aligning them into a coherent arrangement formula — where the kick pattern *within* each section is identified, and transitions between patterns are labeled — is where agents will actually struggle. This is where interface contracts and compositionality gates earn their keep (or don't).

---

## Recommendation: Two-Tier Experiment Design

### Tier 1 — Minimum viable multi-stage pipeline (the decomposition test)

Pick the simplest two-stage slice that has real decomposition challenges:

1. **Source separation** (audio → stems via demucs)
2. **Kick pattern extraction** (drum stem → kick onset timestamps → pattern formula)

Why this pair:
- The interface between stages has a concrete contract (stem audio format, sample rate, channel layout)
- The stages use different libraries (demucs vs librosa/madmom)
- Verification is different per stage (listen to stem vs check onset accuracy)
- The recombination (kick timestamps → pattern string like `K--K--K-`) requires aligning to a beat grid
- It's small enough to run the L0-L3 ladder on, but complex enough that decomposition might actually matter

Suggested acceptance criteria for this task:
- AC-1: Accepts wav/mp3/flac input
- AC-2: Produces separated drum stem (listenable, recognizably drums)
- AC-3: Detects kick onsets within ±20ms of audible kicks
- AC-4: Outputs kick pattern as beat-grid-aligned string per bar
- AC-5: Runs in <2 minutes on a 5-minute track
- AC-6: Has automated tests for the interface contract between stages

AC-6 is the critical one. It directly tests whether the agent naturally defines and enforces the stage boundary — the core SYNTROPY hypothesis.

### Tier 2 — Progressive pipeline extension (the scaling test)

Once tier 1 works, add stages incrementally:
1. Add section boundary detection → kick patterns become per-section
2. Add snare extraction → combining two drum patterns
3. Add bass pattern → pitch tracking on a separated stem
4. Add the arrangement formatter → recombination into the final formula

Each addition tests whether the decomposition process scales:
- Does adding a third stage break the contracts from stages 1-2?
- Does the agent correctly identify feedback relationships (not purely sequential)?
- Does the recombination cost grow linearly or explosively?

---

## What This Changes About the Experiment

The L0-L3 ladder, adaptive climbing, results template, and decision tree from experiment-001 are all good — keep the methodology. The change is the task under test.

| Aspect | Current (experiment-001) | Proposed |
|---|---|---|
| Task | Section boundary detection | 2-stage: source separation → kick pattern extraction |
| Complexity | Single function, one library | Multi-stage, multi-library, interface contracts |
| Where decomposition matters | Doesn't, really | Stage boundary, contract, recombination |
| Failure mode tested | Agent can't write librosa code | Agent can't compose stages correctly |
| What L0 failure teaches | Nothing useful | Where pipeline composition breaks |
| What L0 success teaches | Task is too easy | Decomposition isn't needed at 2-stage scale |

---

## Cost Accounting (Missing from Current Design)

The results template should include cost-per-successful-run:

```
Cost efficiency = success_rate / (token_cost × wall_clock)
```

Without this, you can't answer: "is the decomposition overhead worth the improvement?" If L2 catches one more bug than L1 but costs 3x the tokens, is that a win?

---

## The Existential Question (Still Unanswered)

Neither the current experiment nor this proposal tests whether agents can *self-decompose*. Both test whether human-provided decomposition helps agents execute better. That's useful but different from the long-term SYNTROPY vision.

A future experiment (003?) should compare:
- Human-decomposed + agent-implemented (what experiment-001 tests)
- Agent-decomposed + agent-implemented (what SYNTROPY ultimately needs)

This is the make-or-break question for SYNTROPY as an automated system.

---

## Summary

The arrangement formula tool is the right problem for SYNTROPY. Use it as the experiment subject, not a trivial subtask of it. Start with the simplest multi-stage slice (separation → kick extraction), run the existing ladder methodology on it, and add stages incrementally to find where decomposition starts earning its keep.
