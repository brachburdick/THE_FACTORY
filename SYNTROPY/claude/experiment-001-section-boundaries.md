# Experiment 001: Section Boundary Detection

**Date:** 2026-03-23
**Goal:** Find the minimum viable decomposition process that improves agent success on a trivial audio analysis task.

---

## The Task

**Build a CLI tool that takes an EDM audio file and outputs a JSON file of structural section boundaries.**

### Acceptance Criteria

- AC-1: Accepts wav, mp3, or flac input via CLI argument
- AC-2: Outputs JSON to stdout or file with structure: `{ "boundaries": [{ "time_seconds": float, "confidence": float }] }`
- AC-3: Detects major structural transitions (intro→buildup→drop→breakdown→outro) — verified by ear against a known test track
- AC-4: Tolerates ±2 seconds from audible transition points
- AC-5: Runs in <30 seconds on a 5-minute track
- AC-6: Has at least one automated test

### Test Track

Use any EDM track you have on disk, or a freely available one. The experiment needs at least one track where you know the transitions by ear so you can verify AC-3/AC-4.

---

## The Ladder

Each level adds one concept from SYNTROPY theory. The experiment tests which level produces the best outcome-to-overhead ratio.

### L0: Baseline (no decomposition process)

Prompt: "Build a Python CLI tool that takes an audio file path and outputs JSON with detected section boundaries. Use librosa. Include a test."

That's it. No decomposition guidance. This is what a competent developer would type into an agent today.

**Measure:** Does it work? How many interventions? How many tokens?

### L1: Explicit subtask decomposition

Same task, but the agent is given an explicit decomposition with defined inputs/outputs:

```
Subtask 1: Audio loading
  Input: file path (str)
  Output: audio samples (np.ndarray), sample rate (int)

Subtask 2: Feature extraction
  Input: audio samples, sample rate
  Output: feature curve (np.ndarray of frame-level values)

Subtask 3: Boundary detection
  Input: feature curve
  Output: list of boundary frame indices

Subtask 4: Output formatting
  Input: boundary indices, sample rate
  Output: JSON matching the output schema

Subtask 5: CLI wrapper
  Input: sys.argv
  Output: calls subtasks 1-4, writes result
```

**Measure:** Same metrics. Compare to L0.

### L2: L1 + verify after each subtask

Same decomposition as L1, but after each subtask the agent must run a concrete check before proceeding:

```
After Subtask 1: assert audio.shape[0] > 0 and sr > 0
After Subtask 2: assert feature_curve.shape[0] > 0, plot feature curve to /tmp for visual inspection
After Subtask 3: assert len(boundaries) >= 2 (at least intro and outro), assert all indices within bounds
After Subtask 4: validate output against JSON schema
After Subtask 5: run the CLI on a test file, check exit code 0 and valid JSON output
```

**Measure:** Same metrics. Does per-step verification catch errors earlier? Does it cost more tokens than it saves?

### L3: L2 + pre/postcondition contracts

Same as L2, but each subtask has explicit contracts:

```
Subtask 2: Feature extraction
  Preconditions:
    - audio is mono float32, normalized to [-1, 1]
    - sr > 0
  Postconditions:
    - feature_curve is 1D float array
    - feature_curve.shape[0] == expected_frames(audio.shape[0], sr, hop_length)
    - no NaN or Inf values
  Invariant:
    - hop_length is consistent across all feature extraction
```

**Measure:** Same metrics. Do contracts catch errors that L2 verification misses? Is the overhead worth it?

### L4: L3 + decision-based boundaries (Parnas)

Instead of decomposing by processing steps (load→extract→detect→format), decompose by uncertain decisions:

```
Decision 1: Which audio representation? (mono? stereo? resampled?)
  → Subtask: audio normalization (hides the representation decision)

Decision 2: Which feature for boundary detection? (spectral flux? MFCCs? chroma? onset strength? novelty curve?)
  → Subtask: feature strategy (hides the feature choice)

Decision 3: How to find boundaries in the feature curve? (peak picking? change point detection? threshold?)
  → Subtask: segmentation strategy (hides the algorithm choice)

Decision 4: Output format details? (JSON schema, confidence calculation)
  → Subtask: serialization (hides the format decision)
```

**Measure:** Same metrics. Does reorganizing around decisions produce different (better?) code structure? Is the decomposition itself better or just different?

### L5: Full framework (Cynefin + compositionality + re-planning)

Full SYNTROPY framework as described in 02-decomposition-framework.md. Classification, decision inventory with uncertainty ratings, interface compositionality gates, separate-context verification, re-planning protocol.

**Measure:** Same metrics. Is the overhead justified for a trivial task? (Hypothesis: no. But it establishes the ceiling.)

---

## Metrics

For each level, record:

| Metric | How to measure |
|---|---|
| Success | Binary: does the tool satisfy all 6 ACs? |
| Interventions | Count of times a human had to correct, clarify, or unblock the agent |
| Total tokens | Input + output tokens for the full task |
| Wall clock | Start to finish |
| Files produced | Count and LOC |
| Bugs caught during process | Errors found by verification/contracts before they propagated |
| Bugs found at end | Errors found only in final testing |

---

## Experiment Plan

### Phase 1: Establish L0 baseline
- Run the L0 prompt as a fresh agent session
- Record all metrics
- Note where the agent struggles or succeeds

### Phase 2: Run L1
- Fresh session, same task, L1 decomposition provided
- Record metrics, compare to L0

### Phase 3: Run L2 if L1 shows improvement
- If L1 = L0, skip to L4 (decomposition without verification isn't the lever)
- If L1 > L0, test whether L2 adds further improvement

### Phase 4: Run L3 if L2 shows improvement
- Same logic: stop climbing when improvement flattens

### Phase 5: Decide
- Identify the knee of the curve
- That level becomes the "good enough" starting model
- Use it to tackle a slightly harder task (e.g., kick pattern extraction)

---

## Rules

- Each level runs in a fresh agent session with no memory of prior runs
- The test track must be the same across all levels
- Human interventions are allowed but counted
- If a level fails entirely (agent cannot complete the task), record that as a data point
- Do not optimize prompts between runs — the point is to test the PROCESS, not prompt engineering

---

## Expected Outcome

For a trivial task like this, I expect:
- L0 probably works (frontier models can do this in one shot)
- L1-L2 might be marginal improvement or no improvement
- L3+ is likely overhead-negative for this complexity level

If L0 works perfectly, that's informative: it means the decomposition framework adds value only above a certain complexity threshold, and we need a harder task to find that threshold.

If L0 fails, that's also informative: it tells us where the agent struggles and which intervention (decomposition, verification, contracts) fixes it.

Either way, we learn something concrete.
