# Forge — Pipeline Self-Improvement Infrastructure

> The factory makes products. The forge makes the factory's tools.

This directory contains the **process definitions** — prompts, rubrics, protocols,
and scripts — that the pipeline uses to evaluate and improve itself. It is a
project in the same sense that SCUE or CRUCIBLE are projects: it has its own
development lifecycle, its own quality concerns, and its own scope.

## What belongs here vs. elsewhere

| Content | Location | Why |
|---------|----------|-----|
| Process definitions (prompts, rubrics, protocols) | `forge/` | Active infrastructure |
| Process outputs (extracted convos, assessments, scores) | `.agent/` | Execution state |
| Research findings, prior art, papers | `support/research/` | Cold reference |
| Version migration docs, architecture plans | `support/v1.10/` | Historical record |
| Operational skills (loaded during work sessions) | `skills/` | Runtime, not meta |

## Subprocess Index

| Subprocess | Directory | Purpose |
|------------|-----------|---------|
| Conversation Extraction | `conversation-extraction/` | Scripts + format docs for capturing session transcripts |
| Conversation Analysis | `conversation-analysis/` | Lens prompts, synthesis prompt, batch protocol |
| Project Assessment | `project-assessment/` | Rubrics, multi-model assessment protocol, bias mitigation |
| Self-Assessment | `self-assessment/` | Session-end classification prompt (project + pipeline split) |
| Scoring | `scoring/` | Git metrics, pipeline scorecard, trend tracking |

## Model Selection Guide

### Principles

1. **Match model to task shape, not prestige.** A $0.25/M-token model extracting
   structured data from a transcript is not doing worse work than an $15/M-token
   model — it's doing different work. The expensive model adds value only when
   the task requires judgment, synthesis, or reasoning over ambiguous evidence.

2. **Cross-family diversity matters more than model tier for assessment.**
   Two Opus-class models from the same family will share blind spots. One Opus +
   one GPT-5 + one Gemini Pro catches more than three Opus instances.

3. **Use the cheapest model that doesn't lose signal.** If a Haiku-class model
   produces the same structured extraction as Opus on 10 test cases, use Haiku.
   Test before assuming you need the bigger model.

4. **Budget for the full cycle, not individual steps.** A 20-session analysis
   cycle costs ~$30-80 depending on model choices. The ROI comes from catching
   issues that would cost 10x more in rework.

### Per-Task Model Recommendations

| Task | Recommended Tier | Specific Models (Mar 2026) | Rationale |
|------|-----------------|---------------------------|-----------|
| **Conversation extraction** (script) | N/A — deterministic | Python script | No LLM needed. Pure parsing. |
| **Lens A: Process Efficiency** | Mid-tier | Gemini 2.5 Flash, Claude Haiku 4.5, GPT-4.1-mini | Pattern matching + counting. Structured output. Low judgment requirement. |
| **Lens B: Quality & Correctness** | Upper-mid | Claude Sonnet 4.5, GPT-4.1 | Needs code comprehension to identify bugs and convention violations. Mid-tier misses subtle issues. |
| **Lens C: Learning & Knowledge** | Upper-mid | Claude Sonnet 4.5, Gemini 3.1 Pro | Needs cross-session pattern recognition. Benefits from long context. |
| **Lens synthesis (per-batch)** | Upper-mid | Claude Sonnet 4.5 | Combining 3 structured reports. Moderate reasoning. |
| **Final synthesis (cross-batch)** | Frontier | Claude Opus 4.6 | Highest-judgment step: ranking, cross-cutting patterns, strategic recommendations. Worth the premium. |
| **Project assessment (independent scoring)** | Frontier × 2-3 families | Claude Opus 4.6, GPT-5.3, Gemini 3.1 Pro | Must be cross-family. Each reads entire codebase and scores rubric. Judgment-intensive. |
| **Assessment synthesis** | Frontier | Claude Opus 4.6 or GPT-5.3 | Must identify genuine disagreements vs. noise. High reasoning. |
| **Position-swap tiebreaker** | Frontier (different family) | Whichever family wasn't used in synthesis | Bias mitigation requires a fresh perspective. |
| **Self-assessment (session-end)** | Whatever model ran the session | Same model | Zero marginal cost — model is already loaded. Classification, not generation. |
| **Eval case generation** | Mid-tier | Claude Sonnet 4.5 | Structured output (grep commands, assertions). Straightforward. |
| **Implementation prompt generation** | Upper-mid | Claude Sonnet 4.5 | Needs to understand both rubric targets and current codebase state. |
| **Implementation execution** | Frontier | Claude Opus 4.6 | Writing/modifying code. Standard feature-flow or refactor-flow. |

### Cost Estimates per Full Cycle (20 sessions)

| Model Strategy | Lens Agents (12 runs) | Synthesis (5 runs) | Assessment (3 runs) | Total |
|---------------|----------------------|--------------------|--------------------|-------|
| All frontier | ~$60-80 | ~$25-35 | ~$40-60 | ~$125-175 |
| **Tiered (recommended)** | ~$15-25 | ~$15-20 | ~$40-60 | ~$70-105 |
| All mid-tier | ~$8-12 | ~$8-12 | ~$20-30 | ~$36-54 |

The tiered approach saves ~40% vs. all-frontier while preserving quality on the
high-judgment steps (final synthesis, assessment scoring) where frontier models
measurably outperform.

### Future: Non-Claude Models & Specialty Models

> **Status:** Note for future implementation. Not blocking v1.10.

**Non-Claude models for assessment diversity:**
- GPT-5.3 and Gemini 3.1 Pro are strong independent scorers. Cross-family
  assessment is already specified in the protocol but requires API keys and
  SDK setup for each provider.
- DeepSeek-V3 shows strong code reasoning at low cost — worth evaluating as
  a lens agent.
- MiniMax M2.5 at $0.30/$1.20 could replace Flash-tier models for extraction.

**Specialty models (when available):**
- Code-specific models (Codex successors, StarCoder variants) for Lens B
  (quality/correctness) — they catch code smells that general models miss.
- Long-context specialists (Gemini with 1M+ context) for cross-session pattern
  analysis when session count exceeds what fits in a single context window.

**Implementation path:**
1. Start with Claude-only (v1.10 launch — already works with Claude Code)
2. Add one non-Claude scorer for project assessment (Step 5 of execution plan)
3. Evaluate whether cross-family scoring changes outcomes vs. single-family
4. Add specialty models only when a specific lens consistently underperforms

## How to Run a Full Improvement Cycle

See `support/v1.10/v1.10-execution-instructions.md` for the step-by-step procedure.

Quick reference:
1. Extract conversations → `scripts/extract-conversations.py`
2. Select & batch 20 sessions → `conversation-analysis/` prompts
3. Run 3 lens agents per batch (parallel) → structured reports
4. Synthesize per-batch → synthesis prompt
5. Final synthesis → ranked improvements
6. Triage (human) → ACCEPT / DEFER / REJECT
7. Create eval cases → `.agent/evals/`
8. Generate implementation prompts → `.agent/improvement-prompts/`
9. Execute implementations → standard flow skills
10. Verify → re-run evals, re-assess, compare to baseline

## Version
- **Introduced:** v1.10 (2026-03-22)
- **Research basis:** `support/research/agent-pipeline-improvement-research.md`,
  `support/research/pipeline-scoring-research.md`
