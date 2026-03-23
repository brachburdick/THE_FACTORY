"""
Code quality scorer for Inspect experiments.

Evaluates generated code on multiple dimensions using an LLM judge.
Used to compare agent variants on code output quality.
"""

from inspect_ai.scorer import (
    Score,
    Target,
    metric,
    scorer,
    CORRECT,
    INCORRECT,
    mean,
)
from inspect_ai.solver import TaskState


QUALITY_RUBRIC = """\
Evaluate the code output on these dimensions (1-5 each):

1. **Correctness**: Does the code solve the stated problem? Are edge cases handled?
2. **Type Safety**: Are type hints present and accurate? Any `any` types?
3. **Minimal Change**: Is the solution focused, or does it include unnecessary changes?
4. **Convention Adherence**: Does it follow the patterns established in the codebase?
5. **Test Coverage**: Are tests included? Do they cover the main case and edge cases?

Respond with a JSON object:
{
  "correctness": <1-5>,
  "type_safety": <1-5>,
  "minimal_change": <1-5>,
  "convention_adherence": <1-5>,
  "test_coverage": <1-5>,
  "overall": <1-5>,
  "explanation": "<brief explanation>"
}
"""


@scorer(metrics=[mean()])
def code_quality():
    """Score code quality using LLM-as-judge with structured rubric."""

    async def score(state: TaskState, target: Target) -> Score:
        # This scorer works with model_graded_fact as a wrapper.
        # For standalone use, implement the LLM call here.
        # For now, return based on whether the output contains key signals.
        output = state.output.completion if state.output else ""

        if not output.strip():
            return Score(value=INCORRECT, explanation="No output generated")

        # Basic heuristic scoring (upgrade to LLM judge when running real experiments)
        signals = {
            "has_code": "def " in output or "function " in output or "class " in output,
            "has_types": "-> " in output or ": str" in output or ": int" in output,
            "has_test": "test_" in output or "def test" in output,
            "is_minimal": len(output) < 5000,  # not overengineered
        }

        score_val = sum(signals.values()) / len(signals)
        return Score(
            value=CORRECT if score_val >= 0.5 else INCORRECT,
            explanation=f"Quality signals: {signals}",
        )

    return score
