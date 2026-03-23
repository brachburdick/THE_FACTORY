"""
Code quality scorer for Inspect experiments.

Primary scoring uses concrete, deterministic signals:
- Code structure detection (functions, classes, types)
- Test presence and structure
- Diff size / minimality
- Import hygiene

LLM judging is available as optional secondary scoring via code_quality_llm().
"""

from inspect_ai.scorer import (
    Score,
    Target,
    scorer,
    CORRECT,
    INCORRECT,
    mean,
)
from inspect_ai.solver import TaskState


@scorer(metrics=[mean()])
def code_quality():
    """Score code quality using deterministic structural checks.

    Signals checked:
    - has_code: Contains function/class definitions
    - has_types: Contains type hints (-> or : type)
    - has_test: Contains test functions
    - is_minimal: Output is focused (< 5000 chars)
    - no_any: No explicit 'any' type annotations
    - has_imports: Proper import statements
    """
    async def score(state: TaskState, target: Target) -> Score:
        output = state.output.completion if state.output else ""

        if not output.strip():
            return Score(value=INCORRECT, explanation="No output generated")

        signals = {
            "has_code": "def " in output or "function " in output or "class " in output,
            "has_types": "-> " in output or ": str" in output or ": int" in output or ": float" in output or ": bool" in output or ": list" in output or ": dict" in output,
            "has_test": "test_" in output or "def test" in output or "it(" in output or "describe(" in output,
            "is_minimal": len(output) < 5000,
            "no_any": ": any" not in output.lower() and ": Any" not in output,
            "has_imports": "import " in output or "from " in output or "require(" in output,
        }

        passed = sum(signals.values())
        total = len(signals)
        ratio = passed / total

        explanation_parts = [f"{'PASS' if v else 'FAIL'}: {k}" for k, v in signals.items()]

        return Score(
            value=CORRECT if ratio >= 0.6 else INCORRECT,
            explanation=f"{passed}/{total} signals: " + ", ".join(explanation_parts),
        )

    return score


@scorer(metrics=[mean()])
def code_quality_llm():
    """Optional secondary scorer: LLM-as-judge for nuanced quality assessment.

    Use alongside code_quality() for richer evaluation, not as the primary signal.
    """
    from inspect_ai.scorer import model_graded_fact
    return model_graded_fact()
