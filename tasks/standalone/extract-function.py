"""
Inspect task: Extract a repeated pattern into a reusable function.

Standalone task — no project repo dependency. All code is inline.
Tests the agent's ability to identify duplication and extract a helper
while preserving behavior.
"""

import textwrap

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import Score, Target, scorer, mean, CORRECT, INCORRECT
from inspect_ai.solver import TaskState, generate, system_message


DUPLICATED_CODE = textwrap.dedent("""\
    import re

    def validate_email(email: str) -> bool:
        \"\"\"Check if email is valid.\"\"\"
        if not email or not isinstance(email, str):
            return False
        email = email.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def validate_emails_in_list(emails: list[str]) -> list[str]:
        \"\"\"Return only valid emails from a list.\"\"\"
        valid = []
        for email in emails:
            if not email or not isinstance(email, str):
                continue
            email = email.strip().lower()
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
            if re.match(pattern, email):
                valid.append(email)
        return valid

    def find_email_domain(email: str) -> str | None:
        \"\"\"Extract domain from a valid email, or None if invalid.\"\"\"
        if not email or not isinstance(email, str):
            return None
        email = email.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return None
        return email.split('@')[1]
""")


@scorer(metrics=[mean()])
def extract_function_check():
    """Verify the extraction was done correctly."""
    async def score(state: TaskState, target: Target) -> Score:
        output = state.output.completion if state.output else ""
        if not output.strip():
            return Score(value=INCORRECT, explanation="No output generated")

        # The refactored code should:
        # 1. Define a helper function (normalize, clean, sanitize, or similar)
        # 2. Reduce duplication of the validation pattern
        # 3. Keep all three public functions
        has_helper = any(
            f"def {name}" in output
            for name in [
                "_normalize_email", "_clean_email", "_sanitize_email",
                "_prepare_email", "_validate_email_format", "normalize_email",
                "clean_email", "_is_valid_email",
            ]
        )

        # Alternative: they might just call validate_email from the other functions
        reuses_validate = (
            "validate_email(" in output
            and "validate_emails_in_list" in output
            and "find_email_domain" in output
        )

        keeps_all_functions = (
            "def validate_email" in output
            and "def validate_emails_in_list" in output
            and "def find_email_domain" in output
        )

        if not keeps_all_functions:
            return Score(
                value=INCORRECT,
                explanation="Missing one or more of the three public functions",
            )

        if has_helper or reuses_validate:
            return Score(
                value=CORRECT,
                explanation="Extracts shared logic into helper or reuses validate_email",
            )

        return Score(
            value=INCORRECT,
            explanation="Doesn't extract the duplicated validation/normalization logic",
        )

    return score


TASK_PROMPT = f"""\
You are refactoring a Python module. The code below has duplicated email
validation and normalization logic across three functions.

The module (`email_utils.py`):

```python
{DUPLICATED_CODE}
```

The same pattern is repeated three times:
1. Null/type check
2. strip().lower() normalization
3. Regex validation

Extract the shared logic into a helper function and refactor all three
functions to use it. Preserve the exact same behavior — same inputs produce
same outputs. Show the complete refactored module.
"""


@task
def extract_function() -> Task:
    return Task(
        dataset=[
            Sample(
                input=TASK_PROMPT,
                target="Extract shared email normalization and validation into a helper function.",
            )
        ],
        solver=[
            system_message(
                "You are a software engineer. Refactor the code as described. "
                "Preserve all existing behavior. Show the complete refactored module."
            ),
            generate(),
        ],
        scorer=extract_function_check(),
    )
