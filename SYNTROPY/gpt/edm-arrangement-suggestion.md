# Domain Suggestion: EDM Arrangement Benchmark Ladder

**Date:** 2026-03-23
**Author:** Codex
**Status:** Draft
**Purpose:** Suggest one concrete improvement to the current SYNTROPY materials based on the target domain: EDM track analysis into an arrangement formula.

---

## The Suggestion

Replace `slugify` as the main practical floor with a **domain-native benchmark ladder** for arrangement extraction.

In plain terms:

> make "audio track -> arrangement formula" the benchmark family, and make section-boundary detection the first canonical case inside that family.

This is the single best improvement because it fixes the biggest gap in the current package:

- the theory is about preserving intent on real tasks
- but the GPT-side experiment floor is still a generic toy programming task

For your actual domain, the benchmark should start where your product starts.

---

## Why This Improves What Is Already There

The current GPT package is strong on framing and self-critique, but weak on domain-grounded evidence.

There is already a useful clue elsewhere in the workspace:

- `SYNTROPY/claude/experiment-001-section-boundaries.md`

That experiment is much closer to your real problem than `case-001-slugify` because section boundaries are:

- domain-relevant
- easy to verify by ear
- structurally important
- naturally decomposable

So the improvement is not "invent a whole new direction."

It is:

> promote the arrangement-analysis path into the main benchmark story and treat the generic toy case as a scaffolding artifact, not the meaningful proof point.

---

## What The Ladder Should Look Like

Define one benchmark family called something like `arrangement-formula`.

Then stage it like this:

### Case A: Section pattern only

Input:

- one EDM track audio file

Output:

- section boundaries
- section labels where possible

Example output shape:

```json
{
  "sections": [
    { "label": "intro", "start": 0.0, "end": 32.0, "confidence": 0.91 },
    { "label": "buildup", "start": 32.0, "end": 64.0, "confidence": 0.83 },
    { "label": "drop", "start": 64.0, "end": 112.0, "confidence": 0.95 }
  ]
}
```

Why first:

- it is the skeleton everything else hangs off
- it is easy to inspect manually
- it gives you a real, domain-native floor

### Case B: Drum presence and simple pattern summary

Input:

- same track
- optionally same section map

Output:

- kick/snare/hat presence by section
- very coarse pattern description per section

Example:

- `drop 1: four-on-the-floor kick, snare/clap on 2 and 4, open hats on offbeats`

Why second:

- still verifiable by ear
- more demanding than section boundaries
- begins to test whether decomposition helps

### Case C: Midbass and vocal presence

Output:

- bass activity by section
- vocal presence or absence
- rough role labels like `lead vocal`, `vocal chop`, `spoken tag`, `none`

Why third:

- introduces fuzzier labels
- forces better handling of ambiguity and confidence

### Case D: Full arrangement formula

Output:

- section pattern
- drum summary
- bass summary
- vocal summary
- optional energy/tension notes

Example:

```json
{
  "formula": [
    {
      "section": "intro",
      "bars": 16,
      "drums": "filtered kick pulses, no snare",
      "bass": "none",
      "vocals": "none"
    },
    {
      "section": "drop1",
      "bars": 32,
      "drums": "four-on-the-floor kick, clap on 2 and 4, closed hats driving 8ths",
      "bass": "syncopated midbass riff",
      "vocals": "short vocal chops"
    }
  ]
}
```

Why fourth:

- this is the actual product-shaped deliverable
- by this point the benchmark cases below it give you failure localization

---

## The Key Design Change

The missing artifact is not more theory.

It is a **canonical arrangement-formula schema**.

Right now SYNTROPY talks about decomposition quality in the abstract.

For this domain, the central object should be explicit:

1. what the tool must output
2. which fields are hard requirements
3. which fields may be uncertain
4. which checks are automatic vs human-audible

That schema becomes:

- the acceptance criteria anchor
- the decomposition target
- the evaluation contract

Without that, the project risks decomposing toward vague musical summaries instead of a real product object.

---

## Why This Fits My Earlier Critique

My earlier review said the strongest next move was compression plus a stronger benchmark bridge.

This suggestion does both:

- it compresses the target into one concrete domain artifact
- it replaces a generic toy proof with a product-relevant benchmark ladder
- it creates a cleaner path from theory -> experiment -> actual tool

Most importantly, it gives SYNTROPY a task family where the hard parts are real:

- ambiguity
- hierarchical structure
- partial observability
- mixed objective and subjective verification
- staged decomposition

That is much closer to what the framework claims to help with.

---

## Recommended Next Step

Create one new canonical file under `SYNTROPY/` or `SYNTROPY/gpt/`:

- `arrangement-formula-benchmark.md`

That file should define:

- the arrangement-formula JSON schema
- the benchmark ladder from section boundaries to full formula
- the verifier for each stage
- what counts as pass/fail
- what parts require human ear checks

If you do only one thing next, I would do that.
