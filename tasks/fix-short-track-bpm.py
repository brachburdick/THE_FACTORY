"""
Inspect task: Fix the short-track BPM edge case in SCUE.

This is a real bug that was found and fixed during v2 migration.
It serves as the first experiment task to validate the framework.

The bug: librosa returns BPM 0.0 for tracks under 2 seconds,
but the assertion expected either None or > 0.
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import model_graded_fact
from inspect_ai.solver import generate, system_message


TASK_PROMPT = """\
In the SCUE project (a DJ lighting automation tool), there's a failing test
in `tests/test_layer1/test_analysis_edge_cases.py`. The test
`TestVeryShortTrack::test_2_second_sine` fails with:

```
assert result.bpm is None or result.bpm > 0
```

The actual value is `result.bpm = 0.0`. librosa's beat detection returns 0.0
for audio files that are too short to detect beats.

Fix this test so it passes. The fix should be minimal — update the assertion
to handle the edge case correctly. Do not change the analysis engine itself.

Files to look at:
- tests/test_layer1/test_analysis_edge_cases.py (the failing test)
- scue/layer1/analysis.py (the analysis function, for context only)
"""


@task
def fix_short_track_bpm() -> Task:
    return Task(
        dataset=[
            Sample(
                input=TASK_PROMPT,
                target="Change the assertion from `result.bpm > 0` to `result.bpm >= 0` to allow 0.0 as a valid result for very short tracks.",
            )
        ],
        solver=[
            system_message(
                "You are a software engineer. Fix the bug described. "
                "Make the minimal change needed."
            ),
            generate(),
        ],
        scorer=model_graded_fact(),
    )
