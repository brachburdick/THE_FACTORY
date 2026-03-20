# Respective Agent/Model Strengths — Implementation Suggestions

Status: Draft
Prepared: March 20, 2026
Source documents: `support/v1.9/Improvement Research/RESPECTIVE-AGENT-STRENGTHS-research-gpt.md`, `support/v1.9/Improvement Research/RESPECTIVE-MODEL-STRENGTHS research-claude`

---

## Core Finding

Both research documents converge on the same conclusion: **the agent scaffold accounts for a 12-22 point performance swing, while model swaps account for ~1 point at the frontier.** The `.agent/` documentation scaffold, context engineering, flow skills, and handoff contract design are a bigger lever than model choice within the top 3.

The v1.9 constitution is already well-aligned with the research. The suggestions below are limited to changes that would certainly improve pipeline quality based on strong consensus across both documents.

---

## Suggestion 1: Externalize Plan State with Checkpoint-Based Re-Planning

**Research basis**: Both documents flag that no model holds plans coherently across many steps. Claude's document specifically states the best practitioners use "externalized plan state with checkpoint-based re-planning, not trusting any model to hold a plan coherently across many steps."

**Current gap**: Flow skills (debug-flow, feature-flow, refactor-flow) define sequences but don't mandate checkpointed plan artifacts that persist between steps. `.agent/tasks.jsonl` tracks tasks but not plan evolution within a task.

**Suggested change**: Add a `plan_checkpoints` field to the task JSONL schema. Each flow skill's phase transitions would write a checkpoint before proceeding. If a session dies or drifts, the next session replans from the last checkpoint rather than from scratch or from stale memory.

**Affected files**: `.agent/schemas/`, flow skill definitions, `scripts/tasks.sh`

**Confidence**: High — both documents agree, and the mechanism is simple.

---

## Suggestion 2: Explicit Verification Step in Separate Context

**Research basis**: Both documents agree Claude is strongest at critique and problem-spotting, and that self-assessment is unreliable without external verification. Claude's document notes: "Claude has the best unprompted self-assessment. GPT has the best prompted self-assessment when given explicit evaluation criteria." Neither should be trusted alone.

**Current gap**: v1.8's OPERATOR_PROTOCOL had a dedicated Validator role. v1.9's "one default operator, specialist via skills" model may have relaxed this into optional behavior.

**Suggested change**: Each flow skill should include an explicit verification step that runs in a separate context — not self-review in the same session. Even dispatching a subagent for review within the same Claude Code session would help. The key constraint is: the context that wrote the code must not be the only context that reviews it.

**Affected files**: Flow skill definitions (`.claude/skills/debug-flow/`, `feature-flow/`, `refactor-flow/`)

**Confidence**: High — strongest consensus recommendation across both documents.

---

## Suggestion 3: Negative Constraints in Flow Skills

**Research basis**: GPT's document notes Claude "can be more initiative-taking than requested." Claude's document confirms: "Can be too cautious, flagging low-probability risks" and "May over-specify, giving subagents less room." Both documents agree Claude responds well to explicit boundaries.

**Current gap**: The constitution's "What NOT To Do" section is effective. Flow skills don't replicate this pattern — they describe what to do but not what to avoid.

**Suggested change**: Add explicit "do NOT do" guardrails to each flow skill, mirroring the constitution's pattern. Examples: debug-flow should say "Do NOT refactor surrounding code while fixing a bug." Feature-flow should say "Do NOT add configurability beyond what the spec requires."

**Affected files**: Flow skill definitions

**Confidence**: High — smallest change, immediate effect, well-supported by both documents.

---

## Suggestion 4: Multi-Model Routing — Defer

**Research basis**: Both documents suggest heterogeneous model routing (Claude orchestrator, GPT terminal executors, Gemini for research). GPT's document recommends Claude as orchestrator with GPT subagents for terminal tasks. Claude's document proposes a five-tier architecture (orchestrator, execution, bulk, verification, deep reasoning).

**Assessment**: For the current setup — a solo operator running Claude Code on local projects — the integration overhead would be significant and the gains marginal relative to scaffold improvements. The research itself says scaffold changes are a 12-22x bigger lever than model swaps.

**When it would matter**: If the pipeline moves to API-driven orchestration (e.g., CRUCIBLE or similar) where different models can be programmatically routed per task type. At that point, the research supports: Claude Opus for orchestration and critique, Sonnet for bulk coding, GPT for terminal-centric execution, Gemini for large-context research ingestion.

**Suggested change**: None now. Revisit when API-driven pipeline work begins.

**Confidence**: High that deferral is correct for the current workflow.

---

## Implementation Priority

1. **Negative constraints in flow skills** — smallest change, immediate effect on over-eagerness
2. **Checkpoint fields in task JSONL** — structural change, improves plan survival across sessions
3. **Verification subagent step in flow skills** — moderate change, biggest quality impact
4. **Multi-model routing** — defer until API-driven pipeline work

---

## Notes

- Both research documents are consistent in their assessments despite being produced by different models (GPT and Claude). This convergence increases confidence in the shared findings.
- The v1.9 constitution's existing design choices — progressive disclosure, structured state over prose, skills over roles, eval-backed rules — are already well-aligned with what the research recommends. These suggestions are incremental improvements, not architectural changes.
