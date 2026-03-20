# Operator Protocol

> **Version:** 1.9.2
> **Last reviewed:** 2026-03-20
> **Improvements backlog:** See `PROTOCOL_IMPROVEMENTS.md`

> **What this is:** Governance layer for THE_FACTORY. Defines artifact schemas,
> review cadence, logging requirements, rollout policy, and quality gates.
> Runtime rules live in `CLAUDE.md`. This file owns everything else.

---

## 1. Governance Model

### 1.1 Operating Architecture

THE_FACTORY uses one default operator agent with specialist behavior via skills.

- `CLAUDE.md` — hot runtime constitution (always loaded, ≤200 lines)
- Flow skills — predefined step sequences loaded by task type
- Domain skills — project-specific knowledge loaded by trigger table
- Structured state — `.agent/tasks.jsonl`, `.agent/runs.jsonl`, `.agent/incidents.jsonl`

### 1.2 The Human Operator's Job

You do three things:

- **Route**: Classify tasks, load the right flow skill, deliver artifacts between sessions.
- **Decide**: Resolve `[DECISION NEEDED]` tags, approve specs, accept or reject verdicts.
- **Curate**: Distill findings into skill files, prune stale docs, keep the knowledge base clean.

### 1.3 Specialization Model

Keep specialization trigger-based:
- Skills, modes, and temporary passes are allowed.
- New standing roles require eval evidence showing measurable gain.
- Default to the smallest change that closes a failure:
  1. Fix the artifact schema or checklist first.
  2. Add a mode, tag, or skill file second.
  3. Add a new workflow phase only after repeated failure or clear eval improvement.

---

## 2. Artifact Schemas

Every artifact exchanged between agents must follow its schema. If a required field is missing, the artifact is incomplete — send it back.

### 2.0 Artifact Metadata

All durable artifacts use YAML frontmatter for metadata:

```yaml
---
status: [DRAFT | APPROVED | IN_PROGRESS | COMPLETE | SUPERSEDED | ARCHIVED]
project_root: [/absolute/path/to/project]
revision_of: [artifact path or "none"]
supersedes: [artifact path(s) or "none"]
superseded_by: [artifact path(s) or "none"]
---
```

Rules:
- If an artifact is replaced, mark the old one `SUPERSEDED`.
- Status is part of the contract. Never infer currency from timestamps alone.
- YAML frontmatter is machine-parseable. Do not use blockquote metadata.

### 2.1 Handoff Packet

See `templates/handoff-packet.md` for full schema.

Required sections: Dispatch, Objective, Scope Boundary, Context Files, Interface Contracts, Required Output, Constraints, Acceptance Criteria, Dependencies, Replan Triggers, Verification Procedure, Evidence Required, Assumptions In Force, Dispatch Status.

### 2.2 Project Definition Record

See `templates/project-definition-record.md`.

Durable intent artifact with two sections:
- **Frozen Core** — operator-authored, agent-read-only: problem, users, outcomes, non-goals, constraints, quality priorities, UX intent, decision rights.
- **Mutable Clarifications** — agent-appended, timestamped, traceable: discovered requirements, assumptions, unknowns, architectural decisions.

### 2.3 Evidence Review Packet

See `templates/evidence-review-packet.md`.

Event-driven learning artifact capturing: what changed, evidence observed, assumptions invalidated/strengthened, new questions, proposed changes, deferred items, next-slice recommendation, dispatch status.

### 2.4 Spec, Plan, Tasks

See `templates/spec.md`, `templates/plan.md`, `templates/tasks.md`.

Specs reference upstream Project Definition Record items and Evidence Review Packets. Changes must cite the upstream artifact that caused the change.

---

## 3. Dispatch Protocol

### 3.1 Dispatch Readiness Gate

Execution cannot start unless the next slice has:
- Explicit user/stakeholder
- Explicit problem statement
- Explicit desired outcome
- Explicit non-goals
- Explicit hard constraints
- Testable acceptance criteria
- Explicit assumptions (if dispatching with uncertainty)

### 3.2 Dispatch Status

Every handoff carries a dispatch status:
- `READY` — all intent fields complete, no open questions
- `READY WITH EXPLICIT ASSUMPTIONS` — dispatching with stated uncertainty
- `NOT READY` — missing required intent fields, do not dispatch

### 3.3 Iteration Caps

Hard loop caps prevent silent retry spirals:
- **Doer/verifier retry loop:** max 3 attempts
- **Review/refinement loop:** max 2 rounds

When a cap is hit:
1. Log an incident in `.agent/incidents.jsonl`
2. Escalate to the human operator
3. Do NOT silently continue retrying

---

## 4. Observability

### 4.1 Run Ledger

Every completed task writes a record to `.agent/runs.jsonl`.
Schema: see `.agent/schemas/run-record.json`.

### 4.2 Incident Log

Failures, false passes, escaped defects, and cap breaches write to `.agent/incidents.jsonl`.
Schema: see `.agent/schemas/incident-record.json`.

### 4.3 Review Scorecards

Experiential review captured in `.agent/reviews/scorecards.jsonl`.
Dimensions: clarity, confidence, friction, surprise, taste alignment (1-5 with evidence for outliers).

### 4.4 Metrics

Four metric families tracked in `.agent/metrics/README.md`:
- **Outcome:** first-pass success rate, escaped defect rate, rework rate, validator false pass/fail rate, operator override rate
- **Efficiency:** cycle time, handoff count, blocked rate, operator minutes per task
- **Cost:** tokens, tool calls, cost per successful task
- **Qualitative:** clarity, confidence, friction, surprise

---

## 5. Review Cadence

### 5.1 Signal-Driven Reviews

| Trigger | Action |
|---------|--------|
| Per task | Append run record to `.agent/runs.jsonl` |
| Event-driven | Issue Evidence Review Packet after: prototype, first e2e slice, operator discomfort, architectural surprise, repeated failures, 2-5 uncertain tasks, before large batch |
| Weekly | Ops review: rates, incidents, costs from structured data |
| Monthly | Protocol review: durable changes backed by evidence |
| Quarterly | Structural review: skill additions/removals, flow changes |

### 5.2 Three Review Layers

**(A) Task Validation** — contract checks against acceptance criteria, scope compliance.

**(B) Experiential Review** — operator scorecard: clarity, confidence, surprise, friction, taste alignment. Scored 1-5 with evidence for outliers.

**(C) Pipeline Review** — weekly/monthly cadence using run records + incident logs. Drives protocol changes.

These layers are operationally distinct. Do not collapse them.

### 5.3 Protocol Review Requirements

Protocol changes require:
1. Root-cause classification: `SPECIFICATION_OR_SYSTEM_DESIGN`, `HANDOFF_OR_ALIGNMENT`, or `VERIFICATION_OR_TERMINATION`
2. Evidence inputs (run records, incident logs, eval results) — not just backlog items
3. Scaffold-first bias: evaluate schema → hook → checklist → eval → dispatch-quality before proposing model-selection changes
4. See `PROTOCOL_REVIEW_PROMPT.md` for the full review process

---

## 6. Rollout Policy

### 6.1 Change Promotion

Before promoting a material workflow change:
1. Version the prompt/skill/flow explicitly
2. Record version lineage in `.agent/evals/manifest.md`
3. Run a representative eval set old-vs-new
4. Remove or simplify any artifact or rule that does not improve agreed metrics

### 6.2 ADR Threshold

Write an ADR only when the decision:
- Affects >1 project
- Changes a shared interface
- Would take >1 day to reverse

ADRs live in the repo they affect, not centrally. Use MADR lightweight template.

---

## 7. Logging

### 7.1 Protocol Improvements

Observations go in `PROTOCOL_IMPROVEMENTS.md` (root). Format:

```
[TYPE] Description. (Optional: which artifact/skill is affected)
Types: BUG | GAP | FRICTION | IDEA
```

Do not fix the protocol in the moment. Capture the observation. Process in batch via `PROTOCOL_REVIEW_PROMPT.md`.

### 7.2 Task State

Each project tracks tasks in `.agent/tasks.jsonl`. Query with `scripts/tasks.sh ready|blocked|all`.

Fields: `id`, `taskType`, `flowPhase`, `status`, `summary`, `blockers`, `updated`, `plan_checkpoints`.

---

## 8. Version

- **Current:** v1.9.2 (2026-03-20)
- **Canonical model:** `CLAUDE.md`
- **Previous:** v1.9.1 → v1.9 → v1.8 (archived at `support/v1.8/`)
