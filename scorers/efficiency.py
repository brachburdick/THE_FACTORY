"""
Efficiency scorer for Inspect experiments.

Measures token usage and response characteristics.
Based on mining baselines: 25% waste, 15-30 reads before first edit.
"""

from inspect_ai.scorer import (
    Score,
    Target,
    scorer,
    mean,
    CORRECT,
    INCORRECT,
)
from inspect_ai.solver import TaskState


@scorer(metrics=[mean()])
def token_efficiency():
    """Score based on output token count relative to task complexity."""

    async def score(state: TaskState, target: Target) -> Score:
        output = state.output.completion if state.output else ""

        if not output.strip():
            return Score(value=INCORRECT, explanation="No output")

        # Token efficiency: penalize very long outputs for simple tasks
        char_count = len(output)

        if char_count < 10000:
            return Score(value=CORRECT, explanation=f"Efficient: {char_count} chars")
        elif char_count < 30000:
            return Score(
                value=CORRECT,
                explanation=f"Acceptable: {char_count} chars",
            )
        else:
            return Score(
                value=INCORRECT,
                explanation=f"Verbose: {char_count} chars — possible overengineering",
            )

    return score
