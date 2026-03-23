"""
Inspect solver: CRUCIBLE sandboxed execution.

Wraps CRUCIBLE's sandbox runner as an Inspect solver.
CRUCIBLE provides: E2B sandboxing, semantic loop detection,
token budget middleware, convergent teardown.

NOTE: This solver requires CRUCIBLE to be installed and configured
with E2B API keys. It calls CRUCIBLE as a subprocess.
"""

import json
import subprocess
from pathlib import Path

from inspect_ai.solver import solver, TaskState, Generate


CRUCIBLE_ROOT = Path(__file__).resolve().parent.parent / "projects" / "CRUCIBLE"


@solver
def crucible(
    variant: str = "baseline",
    budget: int = 100_000,
    ttl: int = 300,
):
    """Run a task in a CRUCIBLE E2B sandbox.

    Args:
        variant: Variant config name
        budget: Token budget for the run
        ttl: Time-to-live in seconds
    """

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        task_input = state.input_text if hasattr(state, 'input_text') else str(state.messages[-1])

        # Check if CRUCIBLE is available
        crucible_cli = CRUCIBLE_ROOT / "dist" / "cli.js"
        if not crucible_cli.exists():
            state.output = type(state.output)(
                completion="CRUCIBLE not built. Run `npm run build` in projects/CRUCIBLE/ first.",
                model="crucible-sandbox",
            ) if state.output else None
            return state

        try:
            result = subprocess.run(
                [
                    "node", str(crucible_cli),
                    "run",
                    "--task", task_input,
                    "--variant", variant,
                    "--budget", str(budget),
                    "--ttl", str(ttl),
                    "--output", "json",
                ],
                capture_output=True,
                text=True,
                timeout=ttl + 60,  # buffer beyond TTL
                cwd=str(CRUCIBLE_ROOT),
            )

            if result.returncode == 0:
                run_result = json.loads(result.stdout)
                state.metadata["crucible_result"] = run_result
                state.output = type(state.output)(
                    completion=json.dumps(run_result.get("artifacts", {}), indent=2),
                    model="crucible-sandbox",
                ) if state.output else None
            else:
                state.metadata["crucible_error"] = result.stderr
                state.output = type(state.output)(
                    completion=f"CRUCIBLE error: {result.stderr[:500]}",
                    model="crucible-sandbox",
                ) if state.output else None

        except subprocess.TimeoutExpired:
            state.metadata["crucible_error"] = "TTL exceeded"
            state.output = type(state.output)(
                completion="CRUCIBLE run exceeded time limit",
                model="crucible-sandbox",
            ) if state.output else None

        return state

    return solve
