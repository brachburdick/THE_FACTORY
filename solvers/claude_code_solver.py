"""
Inspect solvers for THE_FACTORY experiments.

Two solvers:
1. claude_code_with_skills — Uses Claude with flow skills and domain knowledge
   as system prompt context. This is the "real" THE_FACTORY workflow.
2. bare_prompt — Minimal system prompt, the control group.

For live pipeline mode (tf-008), claude_code_with_skills injects the actual
SKILL.md content, simulating what happens in a real Claude Code session.
"""

from pathlib import Path

from inspect_ai.solver import solver, TaskState, Generate

ROOT = Path(__file__).resolve().parent.parent


def _load_skill(skill_path: str) -> str:
    """Load a skill file's content for use as system prompt context."""
    full_path = ROOT / skill_path
    if full_path.exists():
        return full_path.read_text()
    return ""


@solver
def claude_code_with_skills(
    flow: str = "debug-flow",
    domain_skills: list[str] | None = None,
):
    """Solver that uses Claude with THE_FACTORY's skill system.

    Injects flow skill + domain skills as system prompt context,
    simulating a real Claude Code session with loaded skills.

    Args:
        flow: Which flow skill to load (debug-flow, feature-flow, refactor-flow)
        domain_skills: Additional domain skill paths to load
    """
    parts = []

    # Load root constitution
    claude_md = _load_skill("CLAUDE.md")
    if claude_md:
        parts.append(f"# Pipeline Constitution\n\n{claude_md}")

    # Load flow skill
    flow_content = _load_skill(f".claude/skills/{flow}/SKILL.md")
    if flow_content:
        parts.append(f"# Active Flow: {flow}\n\n{flow_content}")

    # Load domain skills
    for skill_path in domain_skills or []:
        content = _load_skill(skill_path)
        if content:
            parts.append(content)

    combined_prompt = "\n\n---\n\n".join(parts)

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        if combined_prompt:
            state.messages.insert(0, {
                "role": "system",
                "content": combined_prompt,
            })
        return await generate(state)

    return solve


@solver
def bare_prompt():
    """Solver with minimal system prompt — the control group."""
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        state.messages.insert(0, {
            "role": "system",
            "content": "You are a software engineer. Complete the task.",
        })
        return await generate(state)

    return solve
