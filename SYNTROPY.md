# SYNTROPY — Principles for Structured Decomposition

> Acceptance-criteria-preserving hierarchical problem decomposition for software engineering.
> Distilled from cross-model research (Claude + GPT + Codex) across 26 documents.
> Full research archive: `support/archived/syntropy/`

## The 8 Convergent Principles

These arrived at independently by two models with different research biases. They are structural properties of the problem, not artifacts of training data.

1. **Decompose by decisions, not steps.** (Parnas, 1972) Organize around what might change, not the order of processing.
2. **External verification before propagation.** (DeepMind ICLR 2024) Self-reflection is not verification. Check outputs at every boundary with an external signal (tests, types, a different agent).
3. **Replanning from goals, not retry from failure.** (BDI, Rao & Georgeff) When a subtask fails, re-decompose from the goal level with failure evidence. Don't retry the same broken plan.
4. **Single agent + verification beats naive multi-agent.** (Google/MIT 2024) Don't parallelize sequential work. Parallel dispatch only for genuinely independent sections.
5. **Contracts at every boundary.** (Meyer, 1992) If data crosses a boundary, the boundary has typed pre/postconditions that are tested.
6. **Empirical calibration over doctrine.** Measure whether a process helps. If it doesn't, drop it. No process survives contact with data unchanged.
7. **100% coverage.** (WBS, PMI) Every file, every acceptance criterion, must be claimed by exactly one section. No orphans.
8. **Handle ambiguity before decomposing.** (Cynefin, Snowden) If you can't specify the problem, don't decompose it. Probe first, then decompose.

## The L2 Spirit

From the minimum-viable-pass experiments: preserve intent, keep plans short (3 steps max), verify externally after each change, replan when needed, and avoid generating extra framework unless the task actually needs it.

## Applied Form

These principles are implemented in THE_FACTORY as:
- **Section contracts** (`sections/<name>.md`) — per-project boundary definitions
- **Three-pass review** (`skills/section-review/SKILL.md`) — section → boundary → integration
- **Boundary enforcement evals** — import rules, type contracts, file coverage checks
- **Coupling maps** — explicit marking of which sections can be reviewed in parallel

## What This Is Not

- Not a 6-phase framework. Not a Cynefin classification protocol. Not a decision inventory template.
- Not a replacement for flow skills (debug/feature/refactor). Those handle task execution; this handles project structure.
- Not a research program. The research is done. The principles are distilled. What matters now is using them.
