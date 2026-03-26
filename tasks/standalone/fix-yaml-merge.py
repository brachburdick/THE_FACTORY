"""
Inspect task: Fix a YAML config merge that drops nested keys.

Standalone task — no project repo dependency. All code is inline.
Tests the agent's ability to fix a dict merge bug where update()
overwrites nested dicts instead of deep-merging them.
"""

import textwrap

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import Score, Target, scorer, mean, CORRECT, INCORRECT
from inspect_ai.solver import TaskState, generate, system_message


BUGGY_CODE = textwrap.dedent("""\
    def merge_configs(base: dict, override: dict) -> dict:
        \"\"\"Deep-merge override into base config. Override values win.\"\"\"
        result = base.copy()
        result.update(override)
        return result
""")

TEST_CODE = textwrap.dedent("""\
    def test_deep_merge_preserves_nested():
        base = {"db": {"host": "localhost", "port": 5432}, "debug": False}
        override = {"db": {"host": "prod-db"}, "debug": True}
        result = merge_configs(base, override)
        assert result == {
            "db": {"host": "prod-db", "port": 5432},
            "debug": True,
        }

    def test_shallow_keys_work():
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = merge_configs(base, override)
        assert result == {"a": 1, "b": 3, "c": 4}
""")


@scorer(metrics=[mean()])
def yaml_merge_fix_check():
    """Verify the deep merge fix deterministically."""
    async def score(state: TaskState, target: Target) -> Score:
        output = state.output.completion if state.output else ""
        if not output.strip():
            return Score(value=INCORRECT, explanation="No output generated")

        # The fix must implement recursive/deep merge for nested dicts
        has_recursion = (
            "merge_configs" in output
            and "isinstance" in output
            and "dict" in output
        )
        has_deep_merge = has_recursion or "deep" in output.lower()

        if has_deep_merge:
            return Score(
                value=CORRECT,
                explanation="Implements recursive deep merge for nested dicts",
            )

        return Score(
            value=INCORRECT,
            explanation="Output doesn't implement deep merge for nested dict keys",
        )

    return score


TASK_PROMPT = f"""\
You are working on a Python config management module. The merge function
has a bug — it drops nested keys when merging configs.

The function (`config.py`):

```python
{BUGGY_CODE}
```

The failing test (`test_config.py`):

```python
{TEST_CODE}
```

The first test fails because `result["db"]` only has `{{"host": "prod-db"}}`
— the `"port": 5432` from base is lost. `dict.update()` replaces the entire
nested dict instead of deep-merging it.

Fix merge_configs to recursively merge nested dicts while letting override
values win for leaf keys. Show the exact code change needed.
"""


@task
def fix_yaml_merge() -> Task:
    return Task(
        dataset=[
            Sample(
                input=TASK_PROMPT,
                target="Implement recursive merge: if both base and override have a dict for the same key, merge them recursively.",
            )
        ],
        solver=[
            system_message(
                "You are a software engineer. Fix the bug described. "
                "Make the minimal change needed. Show the exact code change."
            ),
            generate(),
        ],
        scorer=yaml_merge_fix_check(),
    )
