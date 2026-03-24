# Experiment 001: Execution Plan

**Date:** 2026-03-23

---

## Prerequisites

### 1. Pick a test track
Choose one EDM track where you know the structure by ear. Write down the expected section boundaries before you start — this is your ground truth.

```
Example ground truth for a track:
  0:00  intro
  0:32  buildup
  1:04  drop 1
  1:52  breakdown
  2:24  buildup 2
  2:56  drop 2
  3:44  outro

Boundaries (what the tool should find):
  [0, 32, 64, 112, 144, 176, 224]  (seconds, ±2s tolerance)
```

Save this as `SYNTROPY/experiment-001/ground-truth.json`:
```json
{
  "track": "filename.mp3",
  "bpm": 128,
  "boundaries_seconds": [0, 32, 64, 112, 144, 176, 224],
  "labels": ["intro", "buildup", "drop1", "breakdown", "buildup2", "drop2", "outro"],
  "tolerance_seconds": 2
}
```

### 2. Set up the experiment directory
```
mkdir -p SYNTROPY/experiment-001/runs
cp /path/to/your/track.mp3 SYNTROPY/experiment-001/test-track.mp3
```

### 3. Ensure Python environment has librosa
```
pip install librosa soundfile click
```

---

## Run Protocol

For each level, follow these steps exactly.

### Before each run
- Open a **fresh Claude Code session** (no conversation history)
- Start a timer
- Have `SYNTROPY/experiment-001/` as working directory

### During each run
- Paste the level-specific prompt (below)
- Let the agent work
- Count every time you intervene (correct, clarify, unblock, reject a tool call)
- Do NOT volunteer information the prompt doesn't include
- If the agent asks a clarifying question, answer it (counts as 1 intervention)
- If the agent gets stuck in a loop, stop it (counts as 1 intervention + note the failure)

### After each run
- Run the produced tool against the test track
- Compare output to your ground truth
- Record metrics in the results template (below)
- Save the produced code to `runs/L{N}/`

---

## Level Prompts

### L0 Prompt
```
Build a Python CLI tool that takes an audio file path as an argument and outputs
JSON with detected section boundaries (major structural transitions in the song).
Use librosa. Include at least one test.

Output format: { "boundaries": [{ "time_seconds": float, "confidence": float }] }

Put the code in SYNTROPY/experiment-001/runs/L0/
```

### L1 Prompt
```
Build a Python CLI tool that takes an audio file path and outputs JSON with
detected section boundaries. Use librosa.

Implement it as these subtasks in order:

Subtask 1 - Audio loading:
  Input: file path (str)
  Output: audio samples (np.ndarray), sample rate (int)

Subtask 2 - Feature extraction:
  Input: audio samples, sample rate
  Output: feature curve (np.ndarray of frame-level energy/spectral values)

Subtask 3 - Boundary detection:
  Input: feature curve
  Output: list of boundary frame indices

Subtask 4 - Output formatting:
  Input: boundary indices, sample rate
  Output: JSON string matching schema { "boundaries": [{ "time_seconds": float, "confidence": float }] }

Subtask 5 - CLI wrapper:
  Input: command line args
  Output: calls subtasks 1-4, prints JSON to stdout

Include at least one test.
Put the code in SYNTROPY/experiment-001/runs/L1/
```

### L2 Prompt
```
Build a Python CLI tool that takes an audio file path and outputs JSON with
detected section boundaries. Use librosa.

Implement these subtasks in order, and verify each one before moving to the next:

Subtask 1 - Audio loading:
  Input: file path (str)
  Output: audio samples (np.ndarray), sample rate (int)
  Verify: assert audio.shape[0] > 0 and sr > 0, print duration

Subtask 2 - Feature extraction:
  Input: audio samples, sample rate
  Output: feature curve (np.ndarray of frame-level values)
  Verify: assert feature_curve.shape[0] > 0, assert no NaN values

Subtask 3 - Boundary detection:
  Input: feature curve
  Output: list of boundary frame indices
  Verify: assert len(boundaries) >= 2, assert all indices are within feature_curve bounds

Subtask 4 - Output formatting:
  Input: boundary indices, sample rate
  Output: JSON string matching schema { "boundaries": [{ "time_seconds": float, "confidence": float }] }
  Verify: parse the JSON output, validate it has the right keys and types

Subtask 5 - CLI wrapper + integration test:
  Input: command line args
  Output: calls subtasks 1-4, prints JSON to stdout
  Verify: run the CLI on a real audio file, confirm exit code 0 and valid JSON output

After ALL subtasks pass verification, run the full tool on a test file and
confirm the output looks reasonable.

Put the code in SYNTROPY/experiment-001/runs/L2/
```

### L3 Prompt
```
Build a Python CLI tool that takes an audio file path and outputs JSON with
detected section boundaries. Use librosa.

Implement these subtasks. Each has a contract (preconditions and postconditions).
Verify each contract before and after each subtask.

Subtask 1 - Audio loading:
  Input: file path (str)
  Pre: file exists, extension is .wav/.mp3/.flac
  Post: audio is 1D float32 ndarray normalized to [-1,1], sr > 0
  Post: duration = audio.shape[0] / sr is between 30s and 600s

Subtask 2 - Feature extraction:
  Input: audio (1D float32 [-1,1]), sr (int)
  Pre: audio is 1D float32 normalized to [-1,1], sr > 0
  Post: feature_curve is 1D float ndarray, no NaN/Inf
  Post: len(feature_curve) == ceil(len(audio) / hop_length)

Subtask 3 - Boundary detection:
  Input: feature_curve (1D float ndarray)
  Pre: feature_curve is 1D float, no NaN/Inf, len > 0
  Post: boundaries is sorted list of ints, all in [0, len(feature_curve))
  Post: len(boundaries) >= 2
  Post: no two boundaries within 5 seconds of each other

Subtask 4 - Output formatting:
  Input: boundaries (list[int]), sr (int), hop_length (int)
  Pre: boundaries is sorted list of non-negative ints, sr > 0, hop_length > 0
  Post: output is valid JSON matching { "boundaries": [{ "time_seconds": float, "confidence": float }] }
  Post: time_seconds values are sorted and non-negative
  Post: confidence values are in [0, 1]

Subtask 5 - CLI wrapper:
  Pre: sys.argv[1] is a valid file path
  Post: stdout contains valid JSON, exit code 0

Include at least one automated test. After completion, run on a real audio file.
Put the code in SYNTROPY/experiment-001/runs/L3/
```

### L4 and L5
Only run these if L3 shows improvement over L2. Prompts are longer — draft them based on the experiment design doc sections for L4/L5 if you get there.

---

## Results Template

After each run, copy this and fill it in. Save to `SYNTROPY/experiment-001/runs/L{N}/results.md`.

```markdown
# L{N} Results

**Date:**
**Model used:**
**Track:** (filename, duration, BPM)

## Metrics
- Success (all ACs pass): yes/no
- AC-1 (accepts wav/mp3/flac): pass/fail
- AC-2 (correct JSON schema): pass/fail
- AC-3 (detects major transitions): pass/fail — found X of Y expected boundaries
- AC-4 (±2s tolerance): pass/fail — worst offset was Xs
- AC-5 (<30s runtime): pass/fail — actual: Xs
- AC-6 (has automated test): pass/fail
- Human interventions: N
  - Intervention 1: (what and why)
- Wall clock: Xm
- Files produced: N files, ~N LOC total
- Bugs caught during process: N
  - Bug 1: (what, when caught)
- Bugs found only at end: N
  - Bug 1: (what)

## Boundaries found vs expected
| Expected (s) | Found (s) | Offset (s) | Hit? |
|---|---|---|---|
| ... | ... | ... | ... |

## Notes
(Anything surprising, where the agent struggled, what worked well)
```

---

## Decision Points

After L0:
- If all ACs pass with 0 interventions → L0 is sufficient for this complexity.
  Record that, then design a harder task (experiment-002).
- If some ACs fail → run L1 to see if decomposition helps.

After L1:
- If no improvement over L0 → skip L2, try L4 (maybe the issue is boundary quality, not granularity).
- If improvement → run L2 to test whether verification adds more.

After L2:
- If no improvement over L1 → verification isn't the lever at this complexity. Stop.
- If improvement → run L3 to test contracts.

After L3:
- If improvement → you've found that contracts matter even at low complexity.
  This is a strong signal for SYNTROPY. Write it up.
- If no improvement → L2 is your "good enough" model. Write it up.

General:
- If all levels produce the same result → the task is too easy. Design experiment-002 with a harder task.
- If a level introduces MORE failures → that's a signal the overhead is actively harmful. Important finding.

---

## After the experiment

Write `SYNTROPY/claude/experiment-001-findings.md` with:
1. Which level won and why
2. The "good enough" starting model
3. What the next experiment should be (harder task? different dimension?)
4. Any surprises
