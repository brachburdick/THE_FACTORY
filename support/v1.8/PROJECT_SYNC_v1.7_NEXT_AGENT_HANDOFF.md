# Handoff Packet: TASK-CRUCIBLE-V17-SYNC

> Status: APPROVED
> Project Root: /Users/brach/Documents/THE_FACTORY/CRUCIBLE
> Revision Of: none
> Supersedes: none
> Superseded By: none

## Dispatch
- Mode: DIRECT DISPATCH
- Output path: /Users/brach/Documents/THE_FACTORY/CRUCIBLE/specs/feat-protocol-sync-v1.7/sessions/session-001-developer.md
- Parallel wave: none

## Objective
Sync `CRUCIBLE` to the root `OPERATOR_PROTOCOL.md` v1.7 standard without touching product code, and leave a session summary that records any residual drift or follow-up work.

## Role
Developer

## Working Directory
- Run from: /Users/brach/Documents/THE_FACTORY
- Related feature/milestone: feat-protocol-sync-v1.7

## Scope Boundary
- Files this agent MAY read:
  - `/Users/brach/Documents/THE_FACTORY/OPERATOR_PROTOCOL.md`
  - `/Users/brach/Documents/THE_FACTORY/IMPLEMENTATION_PROMPT.md`
  - `/Users/brach/Documents/THE_FACTORY/PROJECT_SYNC_v1.7_ASSESSMENT.md`
  - `/Users/brach/Documents/THE_FACTORY/templates/*`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/AGENT_BOOTSTRAP.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/preambles/*.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/templates/*.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/docs/agents/orchestrator-state.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/docs/agents/startup-prompts/*.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/specs/feat-mvp-sandbox/plan.md`
- Files this agent MAY create/modify:
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/docs/interfaces.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/templates/plan.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/templates/handoff-packet.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/templates/session-summary.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/templates/validator-verdict.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/templates/orchestrator-state.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/preambles/COMMON_RULES.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/preambles/ORCHESTRATOR.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/preambles/ARCHITECT.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/preambles/DEVELOPER.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/preambles/VALIDATOR.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/preambles/QA_TESTER.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/docs/agents/startup-prompts/orchestrator.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/docs/agents/startup-prompts/kickstart.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/AGENT_BOOTSTRAP.md`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/specs/feat-protocol-sync-v1.7/sessions/session-001-developer.md`
- Files this agent must NOT touch:
  - `/Users/brach/Documents/THE_FACTORY/DjTools/scue/**`
  - `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/src/**`
  - `/Users/brach/Documents/THE_FACTORY/OPERATOR_PROTOCOL.md`
  - `/Users/brach/Documents/THE_FACTORY/IMPLEMENTATION_PROMPT.md`
  - `/Users/brach/Documents/THE_FACTORY/PROTOCOL_IMPROVEMENTS.md`

## Context Files
- `/Users/brach/Documents/THE_FACTORY/PROJECT_SYNC_v1.7_ASSESSMENT.md`
- `/Users/brach/Documents/THE_FACTORY/IMPLEMENTATION_PROMPT.md`
- `/Users/brach/Documents/THE_FACTORY/OPERATOR_PROTOCOL.md`
- `/Users/brach/Documents/THE_FACTORY/templates/handoff-packet.md`
- `/Users/brach/Documents/THE_FACTORY/templates/session-summary.md`
- `/Users/brach/Documents/THE_FACTORY/templates/validator-verdict.md`
- `/Users/brach/Documents/THE_FACTORY/templates/orchestrator-state.md`
- `/Users/brach/Documents/THE_FACTORY/templates/plan.md`
- `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/AGENT_BOOTSTRAP.md`
- `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/preambles/COMMON_RULES.md`
- `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/preambles/ORCHESTRATOR.md`
- `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/preambles/ARCHITECT.md`
- `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/preambles/DEVELOPER.md`
- `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/preambles/VALIDATOR.md`
- `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/preambles/QA_TESTER.md`
- `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/templates/handoff-packet.md`
- `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/templates/session-summary.md`
- `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/templates/validator-verdict.md`
- `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/templates/orchestrator-state.md`
- `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/docs/agents/startup-prompts/orchestrator.md`

## Interface Contracts
- This is a protocol-sync task, not application runtime work. There is no product-code interface change in scope.
- Root v1.7 docs and root `templates/` are the source of truth for schema and workflow rules.
- Preserve CRUCIBLE-specific domain language and project-specific pitfalls when they do not conflict with root v1.7.
- Create `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/docs/interfaces.md`, but do not invent missing architecture or constraints content if source material is absent. Leave a minimal, honest scaffold and capture any follow-up in the session summary.

## Required Output
- Write: `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/specs/feat-protocol-sync-v1.7/sessions/session-001-developer.md`
- If you create a new feature directory for this sync task, keep it limited to what is needed for the output artifact path above.
- If you leave any residual drift for a later pass, record it in `## Follow-Up Items` of the session summary.

## Constraints
- Use `/Users/brach/Documents/THE_FACTORY/IMPLEMENTATION_PROMPT.md` and the root `templates/` directory as the v1.7 master source. Do not sync from memory.
- Sync `CRUCIBLE` only in this session. Do not begin the `DjTools/scue` migration.
- Preserve CRUCIBLE-specific layer language and existing project pitfalls where still relevant.
- Do not fabricate missing project docs such as architecture or constraints content. Flag them as follow-up instead.
- Run a path/reference consistency sweep before ending the session so updated CRUCIBLE files do not point at nonexistent protocol artifacts.

## Acceptance Criteria
- [ ] `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/docs/interfaces.md` exists.
- [ ] `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/templates/plan.md` exists.
- [ ] `/Users/brach/Documents/THE_FACTORY/CRUCIBLE/docs/agents/startup-prompts/kickstart.md` exists.
- [ ] Updated CRUCIBLE templates and preambles align with the root v1.7 schema and path conventions for the targeted files in scope.
- [ ] `CRUCIBLE/AGENT_BOOTSTRAP.md` and the updated startup prompt(s) reference real, project-correct paths.
- [ ] CRUCIBLE-specific guidance is preserved where it still adds value.
- [ ] Session summary written to the exact output path above, including residual drift and follow-up items.
- [ ] Consistency sweep completed; no executable tests apply to this doc-only sync task.

## Dependencies
- Requires completion of: none
- Blocks: TASK-SCUE-V17-MIGRATION

## Suggested Order
1. Read the root master docs and templates listed above.
2. Read the current CRUCIBLE files in scope and note any project-specific guidance that must survive the merge.
3. Create the missing files first: `docs/interfaces.md`, `templates/plan.md`, `docs/agents/startup-prompts/kickstart.md`.
4. Upgrade the targeted templates and preambles.
5. Update `CRUCIBLE/AGENT_BOOTSTRAP.md` and the startup prompt(s) to match the synced structure.
6. Run a path/reference consistency sweep across the touched files.
7. Write the session summary to the required output path.

## Prior Session Notes
- Root protocol rollout is already complete. `OPERATOR_PROTOCOL.md`, `IMPLEMENTATION_PROMPT.md`, root `templates/`, `PROTOCOL_REVIEW_PROMPT.md`, `PROTOCOL_IMPROVEMENTS.md`, and `INIT_PROMPT.md` were already updated to v1.7.
- `/Users/brach/Documents/THE_FACTORY/PROJECT_SYNC_v1.7_ASSESSMENT.md` already concludes that `CRUCIBLE` should be synced before `DjTools/scue`.
- `DjTools/scue` is intentionally deferred because it needs a migration-aware pass for path drift and `CONTRACTS.md` to `interfaces.md` reconciliation.

## Open Questions
- none

> This handoff is intentionally scoped to `CRUCIBLE` only. Do not broaden the task in-session.
