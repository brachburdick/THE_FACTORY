# Experiment 001: Context & Reasoning Chain

**Date:** 2026-03-23

---

## Why this experiment exists

SYNTROPY started as a research question: can principled problem decomposition improve agent reliability on non-trivial SWE tasks? Two independent analyses (Claude + GPT) produced ~2,500 lines of theory drawing from 15+ canonical sources.

A reality check identified the core risk: **the theory-to-experiment ratio is dangerously high.** The theory is directionally sound but untested. Specific concerns:

1. The overhead of formal decomposition may exceed its benefit
2. The existing flow skills already implement ~80% of what SYNTROPY proposes, informally
3. Current frontier models may handle trivial tasks without any decomposition process
4. The decomposition process itself may be too hard for agents to execute reliably

## What we're testing

The SYNTROPY theory proposes a stack of interventions, from simple (decompose into subtasks) to elaborate (Cynefin classification, compositionality gates, contract verification, re-planning). This experiment tests them **incrementally** to find the knee of the curve — the point where adding more process stops helping.

## Why section boundary detection

The user is building an EDM arrangement analysis tool (track → section pattern + drum pattern + bass pattern + vocals + etc). Section boundary detection is the first stage of that pipeline — the skeleton everything else hangs off. It's:

- **Trivially verifiable** — play the track, check the timestamps
- **Well-scoped** — one input (audio), one output (timestamp list)
- **Decomposable** — has natural subtasks (load, extract features, detect boundaries, format output)
- **Domain-relevant** — a real building block, not a toy problem

## What we expect to learn

- If L0 works: the complexity threshold for needing formal decomposition is higher than this task. Next step: try a harder task (kick pattern extraction, multi-stage pipeline).
- If L0 fails: we learn WHERE the agent struggles and can test which specific intervention (L1-L4) fixes it.
- The knee of the curve tells us the "good enough" starting model for SYNTROPY — the minimum viable process worth applying.

## Decision: adaptive climbing

We don't run all 6 levels. We climb until improvement flattens, then stop. This respects the user's stated goal: find a good starting point, solve a trivial case, then iterate.

## Relationship to SYNTROPY documents

| Document | Role |
|---|---|
| 01-research-findings.md | Theory base (not directly used in experiment) |
| 02-decomposition-framework.md | Source for L3-L5 process definitions |
| 04-problem-statement.md | Hypotheses being tested (H3, H5 most directly) |
| realityCheck1.md | Motivation for running experiments instead of writing more theory |
| experiment-001-section-boundaries.md | The experiment design |
| This file | Why we made the choices we made |
