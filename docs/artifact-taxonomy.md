# Artifact Taxonomy

> Every artifact type in THE_FACTORY pipeline, its schema, who produces and consumes it,
> and how it is validated.

## Task Queue

| Field | Value |
|-------|-------|
| **File** | `.agent/tasks.jsonl` |
| **Schema** | `.agent/schemas/task.schema.json` |
| **Format** | Append-only JSONL (last entry per ID wins) |
| **Producer** | Operator (initial), agent (status updates) |
| **Consumer** | Agent (work dispatch), assess.py (metrics), hooks (risk/section lookup) |
| **Validation** | `evals/test_handoffs.py::TestJsonlSchemaValidation::test_tasks_match_schema` |
| **Lifecycle** | Created when work is identified → updated through flow phases → closed on completion |

## Run Records

| Field | Value |
|-------|-------|
| **File** | `.agent/runs.jsonl` |
| **Schema** | `.agent/schemas/run.schema.json` |
| **Format** | Append-only JSONL |
| **Producer** | Agent (at task close, Phase 5/Verify) |
| **Consumer** | assess.py (SLOs, flakiness), operator (review), calibration loop |
| **Validation** | `evals/test_handoffs.py::TestJsonlSchemaValidation::test_runs_match_schema` |
| **Lifecycle** | Created once per task completion. Immutable after creation. |

## Incident Log

| Field | Value |
|-------|-------|
| **File** | `.agent/incidents.jsonl` |
| **Schema** | `.agent/schemas/incident.schema.json` |
| **Format** | Append-only JSONL |
| **Producer** | Agent (on failure, blocked state, or repeated errors) |
| **Consumer** | Operator (review), assess.py (failure analysis) |
| **Validation** | `evals/test_handoffs.py::TestJsonlSchemaValidation::test_incidents_match_schema` |
| **Lifecycle** | Created on failure → reviewed by operator → may spawn follow-up tasks |

## Trigger Misses

| Field | Value |
|-------|-------|
| **File** | `.agent/trigger-misses.jsonl` |
| **Schema** | `.agent/schemas/trigger-miss.schema.json` |
| **Format** | Append-only JSONL |
| **Producer** | Agent (when no trigger table entry matches) |
| **Consumer** | Future LLM fallback classifier (P6), operator (audit) |
| **Validation** | `evals/test_handoffs.py::TestJsonlSchemaValidation::test_trigger_misses_match_schema` |
| **Lifecycle** | Created on miss → `correct_skill` backfilled by operator → feeds classifier training |

## State Snapshot

| Field | Value |
|-------|-------|
| **File** | `.agent/state-snapshot.json` |
| **Schema** | None (ad-hoc, stable structure) |
| **Format** | Single JSON object, overwritten each session |
| **Producer** | `state-snapshot.py` hook (SessionEnd event) |
| **Consumer** | Agent (session start — prior context), operator (debugging) |
| **Validation** | Implicitly validated by JSON parsing; no schema test yet |
| **Lifecycle** | Overwritten at end of each session. Not append-only. |

## Specs

| Field | Value |
|-------|-------|
| **File** | `{project}/specs/feat-{name}/spec.md` or inline |
| **Schema** | `templates/spec.md` (template, not JSON schema) |
| **Format** | Markdown with YAML frontmatter |
| **Producer** | Agent (feature-flow Phase 1) |
| **Consumer** | Agent (implementation, verification), operator (approval) |
| **Validation** | Manual review; frontmatter checked by agent |
| **Lifecycle** | Draft → Approved (operator) → Updated if spec changes during impl → Archived |

## Plans

| Field | Value |
|-------|-------|
| **File** | `.claude/plans/{name}.md` |
| **Schema** | `templates/plan.md` (template) |
| **Format** | Markdown |
| **Producer** | Agent (EnterPlanMode), operator (manual) |
| **Consumer** | Agent (implementation guidance), risk-classifier hook (plan-gate) |
| **Validation** | Existence checked by risk-classifier for high-risk tasks |
| **Lifecycle** | Created in plan phase → consumed during implement → stale after completion |

## Section Contracts

| Field | Value |
|-------|-------|
| **File** | `{project}/sections/{section}.md` |
| **Schema** | `templates/section-contract.md` (template) |
| **Format** | Markdown with structured headings (Owned Paths, Invariants, etc.) |
| **Producer** | Operator or agent (section review) |
| **Consumer** | blast-radius.sh hook, section-review skill, agent (pre-flight checks) |
| **Validation** | `evals/test_conventions.py` (section boundary enforcement) |
| **Lifecycle** | Created when section is defined → updated on boundary changes → merged/split as project evolves |

## Handoff Packets

| Field | Value |
|-------|-------|
| **File** | Ad-hoc (inline or `{project}/handoffs/`) |
| **Schema** | `templates/handoff-packet.md` (template) |
| **Format** | Markdown with JSON Schema envelope |
| **Producer** | Agent (cross-domain handoffs) |
| **Consumer** | Receiving agent or operator |
| **Validation** | Manual; schema envelope checked by handoff skill |
| **Lifecycle** | Created at domain boundary → consumed by receiver → archived |

## Skills

| Field | Value |
|-------|-------|
| **File** | `skills/{name}/SKILL.md` or `.claude/skills/{name}/SKILL.md` |
| **Schema** | YAML frontmatter (name, description) |
| **Format** | Markdown with YAML frontmatter |
| **Producer** | Operator or agent (skill creation) |
| **Consumer** | Agent (loaded on trigger match) |
| **Validation** | `evals/test_conventions.py::TestAllSkillsHaveFrontmatter` |
| **Lifecycle** | Created → loaded on demand → updated as patterns evolve |

## Hook State

| Field | Value |
|-------|-------|
| **File** | `.claude/hooks/fix-attempt-tracker.state` |
| **Schema** | 4-line text (fix_count, total_count, test_cycles, modified_files) |
| **Format** | Plain text, gitignored |
| **Producer** | fix-attempt-tracker.sh hook |
| **Consumer** | fix-attempt-tracker.sh hook (self), operator (debugging) |
| **Validation** | `evals/test_flows.py::TestFixAttemptTrackerHook` (indirect) |
| **Lifecycle** | Created on first source mutation → updated per tool call → cleared on budget-reset or session end |
