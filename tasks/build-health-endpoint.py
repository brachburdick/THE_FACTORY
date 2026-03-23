"""
Inspect task: Build a health check endpoint for a FastAPI service.

A straightforward feature task that any agent configuration should handle.
Useful for baseline comparison across variants.
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import model_graded_fact
from inspect_ai.solver import generate, system_message


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
"""


@task
def build_health_endpoint() -> Task:
    return Task(
        dataset=[
            Sample(
                input=TASK_PROMPT,
                target="A FastAPI router with GET /health returning status, version, timestamp, and uptime_seconds. A pytest test verifying 200 response with correct fields.",
            )
        ],
        solver=[
            system_message(
                "You are a software engineer. Implement the feature described. "
                "Write clean, typed Python code."
            ),
            generate(),
        ],
        scorer=model_graded_fact(),
    )
