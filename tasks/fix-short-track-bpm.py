"""
Inspect task: Fix the short-track BPM edge case in SCUE.

This is a real bug that was found and fixed during v2 migration.
Uses workspace-embedded fixture code — the agent sees the buggy test inline
and must produce the correct fix. Verification is deterministic (string check),
not LLM-judged.

The bug: librosa returns BPM 0.0 for tracks under 2 seconds,
but the assertion expected either None or > 0.
"""

import textwrap

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import Score, Target, scorer, mean, CORRECT, INCORRECT
from inspect_ai.solver import TaskState, generate, system_message


# The buggy test file (pre-fix state)
BUGGY_TEST = textwrap.dedent("""\
    import pytest
    from analysis import analyze_audio

    class TestVeryShortTrack:
        def test_2_second_sine(self, tmp_path):
            \"\"\"BPM detection on a 2-second sine wave.\"\"\"
            import numpy as np
            import soundfile as sf

            sr = 22050
            t = np.linspace(0, 2, sr * 2, endpoint=False)
            audio = np.sin(2 * np.pi * 440 * t).astype(np.float32)
            path = tmp_path / "short.wav"
            sf.write(str(path), audio, sr)

            result = analyze_audio(str(path))
            # BUG: librosa returns 0.0 for very short tracks
            assert result.bpm is None or result.bpm > 0
""")

# The analysis module (context, not to be modified)
ANALYSIS_MODULE = textwrap.dedent("""\
    from dataclasses import dataclass
    from typing import Optional
    import librosa

    @dataclass
    class AnalysisResult:
        bpm: Optional[float]
        duration: float
        key: Optional[str] = None

    def analyze_audio(path: str) -> AnalysisResult:
        y, sr = librosa.load(path, sr=22050)
        duration = librosa.get_duration(y=y, sr=sr)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(tempo) if tempo else None
        return AnalysisResult(bpm=bpm, duration=duration)
""")


@scorer(metrics=[mean()])
def deterministic_fix_check():
    """Verify the fix deterministically — no LLM judge.

    Success: output allows bpm == 0.0 (>= instead of >, or explicit 0.0 handling).
    Fail: output doesn't fix the assertion or modifies analysis.py.
    """
    async def score(state: TaskState, target: Target) -> Score:
        output = state.output.completion if state.output else ""

        if not output.strip():
            return Score(value=INCORRECT, explanation="No output generated")

        # Check that the fix addresses the 0.0 case
        fixes_bpm = (
            ">= 0" in output
            or "== 0" in output
            or "bpm is not None" in output
        )

        if not fixes_bpm:
            return Score(
                value=INCORRECT,
                explanation="Output doesn't fix the assertion to handle bpm == 0.0",
            )

        # Minimality: should NOT edit the analysis module
        edits_analysis = (
            "def analyze_audio" in output
            and ("change" in output.lower() or "edit" in output.lower() or "modify" in output.lower())
            and "analysis.py" in output
        )
        if edits_analysis:
            return Score(
                value=INCORRECT,
                explanation="Fix modifies analysis.py — should only change the test assertion",
            )

        return Score(
            value=CORRECT,
            explanation="Correctly fixes assertion to handle bpm >= 0 with minimal change",
        )

    return score


TASK_PROMPT = f"""\
You are working in a Python project. There's a failing test that needs fixing.

The test file is at `tests/test_analysis_edge_cases.py`:

```python
{BUGGY_TEST}
```

The analysis module it imports (`analysis.py`) is:

```python
{ANALYSIS_MODULE}
```

The test fails with:
```
AssertionError: assert 0.0 is None or 0.0 > 0
```

librosa's beat detection returns 0.0 for audio files that are too short to detect beats.

Fix the test so it passes. The fix should be minimal — update the assertion
to handle the 0.0 edge case correctly. Do not change the analysis engine itself.
Show the exact code change needed.
"""


@task
def fix_short_track_bpm() -> Task:
    return Task(
        dataset=[
            Sample(
                input=TASK_PROMPT,
                target="Change the assertion to allow bpm >= 0 for very short tracks.",
            )
        ],
        solver=[
            system_message(
                "You are a software engineer. Fix the bug described. "
                "Make the minimal change needed. Show the exact code change."
            ),
            generate(),
        ],
        scorer=deterministic_fix_check(),
    )
