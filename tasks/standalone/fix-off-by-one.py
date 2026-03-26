"""
Inspect task: Fix an off-by-one error in a pagination function.

Standalone task — no project repo dependency. All code is inline.
Tests experiment framework without requiring portfolio repos.

The bug: page_items() uses 0-based offset but the page parameter is 1-based,
so page=1 returns items starting at index page_size instead of 0.
"""

import textwrap

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import Score, Target, scorer, mean, CORRECT, INCORRECT
from inspect_ai.solver import TaskState, generate, system_message


BUGGY_CODE = textwrap.dedent("""\
    def page_items(items: list, page: int, page_size: int = 10) -> list:
        \"\"\"Return a page of items. Pages are 1-based.\"\"\"
        start = page * page_size
        end = start + page_size
        return items[start:end]
""")

TEST_CODE = textwrap.dedent("""\
    def test_first_page():
        items = list(range(25))
        result = page_items(items, page=1, page_size=10)
        assert result == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_second_page():
        items = list(range(25))
        result = page_items(items, page=2, page_size=10)
        assert result == [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
""")


@scorer(metrics=[mean()])
def pagination_fix_check():
    """Verify the off-by-one fix deterministically."""
    async def score(state: TaskState, target: Target) -> Score:
        output = state.output.completion if state.output else ""
        if not output.strip():
            return Score(value=INCORRECT, explanation="No output generated")

        # The fix must change `page * page_size` to `(page - 1) * page_size`
        if "(page - 1)" in output or "(page-1)" in output:
            return Score(
                value=CORRECT,
                explanation="Correctly fixes offset to (page - 1) * page_size",
            )

        return Score(
            value=INCORRECT,
            explanation="Output doesn't fix the 1-based to 0-based offset conversion",
        )

    return score


TASK_PROMPT = f"""\
You are working on a Python utility module. There's a bug in the pagination function.

The function (`utils.py`):

```python
{BUGGY_CODE}
```

The failing tests (`test_utils.py`):

```python
{TEST_CODE}
```

The tests fail because page=1 returns items [10..19] instead of [0..9].
Fix the pagination function so that page=1 returns the first page.
Show the exact code change needed. Make the minimal fix.
"""


@task
def fix_off_by_one() -> Task:
    return Task(
        dataset=[
            Sample(
                input=TASK_PROMPT,
                target="Change start = page * page_size to start = (page - 1) * page_size",
            )
        ],
        solver=[
            system_message(
                "You are a software engineer. Fix the bug described. "
                "Make the minimal change needed. Show the exact code change."
            ),
            generate(),
        ],
        scorer=pagination_fix_check(),
    )
