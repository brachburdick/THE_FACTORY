"""
Efficiency scorer for Inspect experiments.

Primary scoring uses concrete signals:
- Output length (char count, line count)
- Tool call count (from metadata if available)
- Runtime (from metadata if available)

Based on mining baselines: 25% waste, 15-30 reads before first edit.
LLM judging is not used — all signals are deterministic.
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
    """Score based on output compactness — penalize verbose outputs."""
    async def score(state: TaskState, target: Target) -> Score:
        output = state.output.completion if state.output else ""

        if not output.strip():
            return Score(value=INCORRECT, explanation="No output")

        char_count = len(output)
        line_count = len(output.splitlines())

        if char_count < 10000:
            return Score(value=CORRECT, explanation=f"Efficient: {char_count} chars, {line_count} lines")
        elif char_count < 30000:
            return Score(value=CORRECT, explanation=f"Acceptable: {char_count} chars, {line_count} lines")
        else:
            return Score(value=INCORRECT, explanation=f"Verbose: {char_count} chars, {line_count} lines")

    return score


@scorer(metrics=[mean()])
def tool_efficiency():
    """Score based on tool call count from metadata.

    Expects state.metadata to contain 'tool_calls' (int) and optionally
    'reads_before_edit' (int) from experiment instrumentation.
    """
    async def score(state: TaskState, target: Target) -> Score:
        meta = state.metadata or {}
        tool_calls = meta.get("tool_calls", 0)
        reads_before_edit = meta.get("reads_before_edit", 0)

        if not tool_calls:
            return Score(value=CORRECT, explanation="No tool call data available (API-only run)")

        signals = {
            "low_ramp_up": reads_before_edit < 10,
            "reasonable_tools": tool_calls < 100,
        }

        passed = sum(signals.values())
        total = len(signals)
        explanation_parts = [f"{'PASS' if v else 'FAIL'}: {k}" for k, v in signals.items()]

        return Score(
            value=CORRECT if passed == total else INCORRECT,
            explanation=f"tool_calls={tool_calls}, reads_before_edit={reads_before_edit}. " + ", ".join(explanation_parts),
        )

    return score


@scorer(metrics=[mean()])
def runtime_efficiency():
    """Score based on wall-clock time from metadata.

    Expects state.metadata to contain 'elapsed_seconds' (float).
    """
    async def score(state: TaskState, target: Target) -> Score:
        meta = state.metadata or {}
        elapsed = meta.get("elapsed_seconds", 0)

        if not elapsed:
            return Score(value=CORRECT, explanation="No runtime data available")

        if elapsed < 60:
            return Score(value=CORRECT, explanation=f"Fast: {elapsed:.1f}s")
        elif elapsed < 180:
            return Score(value=CORRECT, explanation=f"Acceptable: {elapsed:.1f}s")
        else:
            return Score(value=INCORRECT, explanation=f"Slow: {elapsed:.1f}s")

    return score
