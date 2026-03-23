"""
Inspect task: Build a health check endpoint for a FastAPI service.

A straightforward feature task for baseline comparison across variants.
Verification is deterministic — checks for required code structures,
not LLM-judged text quality.
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import Score, Target, scorer, mean, CORRECT, INCORRECT
from inspect_ai.solver import TaskState, generate, system_message


@scorer(metrics=[mean()])
def deterministic_endpoint_check():
    """Verify the health endpoint was built correctly — deterministic checks.

    Checks: route decorator, required fields, test function, type hints.
    """
    async def score(state: TaskState, target: Target) -> Score:
        output = state.output.completion if state.output else ""

        if not output.strip():
            return Score(value=INCORRECT, explanation="No output generated")

        checks = {
            "has_route": '@router.get("/health")' in output or '@app.get("/health")' in output or "get(\"/health\")" in output,
            "has_status_field": '"status"' in output and '"healthy"' in output,
            "has_version_field": '"version"' in output,
            "has_timestamp": "timestamp" in output and ("datetime" in output or "utcnow" in output or "now(" in output),
            "has_uptime": "uptime" in output,
            "has_test": "def test_" in output or "async def test_" in output,
            "has_type_hints": "->" in output,
        }

        passed = sum(checks.values())
        total = len(checks)
        ratio = passed / total

        explanation_parts = []
        for name, ok in checks.items():
            explanation_parts.append(f"{'PASS' if ok else 'FAIL'}: {name}")

        return Score(
            value=CORRECT if ratio >= 0.7 else INCORRECT,
            explanation=f"{passed}/{total} checks passed: " + ", ".join(explanation_parts),
        )

    return score


TASK_PROMPT = """\
Create a health check endpoint for a FastAPI application.

Requirements:
1. GET /health returns {"status": "healthy", "version": "1.0.0"}
2. Include a timestamp field with the current UTC time in ISO format
3. Include an "uptime_seconds" field showing seconds since server start
4. Return 200 for healthy, 503 if any critical dependency is down
5. Add a simple test that verifies the endpoint returns 200 with correct schema

Create two files:
- api/health.py (the endpoint router)
- tests/test_health.py (the test)

Use FastAPI best practices. Type hints on all functions.
Show the complete file contents.
"""


@task
def build_health_endpoint() -> Task:
    return Task(
        dataset=[
            Sample(
                input=TASK_PROMPT,
                target="FastAPI router with GET /health returning status, version, timestamp, uptime_seconds. Pytest test verifying 200 with correct fields.",
            )
        ],
        solver=[
            system_message(
                "You are a software engineer. Implement the feature described. "
                "Write clean, typed Python code. Show complete file contents."
            ),
            generate(),
        ],
        scorer=deterministic_endpoint_check(),
    )
