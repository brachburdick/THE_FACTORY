# v1.7 Project Sync Assessment

Assessment date: 2026-03-19
Protocol target: `OPERATOR_PROTOCOL.md` v1.7

This document identifies:
- which project files the Protocol Enforcer should update first
- what missing infrastructure must be created before a clean sync is possible
- where the highest-risk merge points are

---

## Summary

| Project | Readiness | First Priority | Highest-Risk Diff |
|---|---|---|---|
| `CRUCIBLE` | Medium-high | Fill missing protocol artifacts and upgrade schemas | Missing `docs/interfaces.md` and missing v1.7 template/preamble fields |
| `DjTools/scue` | Medium-low | Resolve path-layout drift and contract-doc migration first | `docs/agents/preambles/` vs `preambles/`, plus `docs/CONTRACTS.md` vs `docs/interfaces.md` |

---

## CRUCIBLE

### Update First

1. Create `CRUCIBLE/docs/interfaces.md`
2. Create `CRUCIBLE/templates/plan.md`
3. Create `CRUCIBLE/docs/agents/startup-prompts/kickstart.md`
4. Update `CRUCIBLE/templates/handoff-packet.md`
5. Update `CRUCIBLE/templates/session-summary.md`
6. Update `CRUCIBLE/templates/validator-verdict.md`
7. Update `CRUCIBLE/templates/orchestrator-state.md`
8. Update `CRUCIBLE/preambles/COMMON_RULES.md`
9. Update `CRUCIBLE/preambles/ORCHESTRATOR.md`
10. Update `CRUCIBLE/preambles/ARCHITECT.md`
11. Update `CRUCIBLE/preambles/DEVELOPER.md`
12. Update `CRUCIBLE/preambles/VALIDATOR.md`
13. Update `CRUCIBLE/preambles/QA_TESTER.md`
14. Update `CRUCIBLE/docs/agents/startup-prompts/orchestrator.md`
15. Update `CRUCIBLE/AGENT_BOOTSTRAP.md`

### Why These Go First

- The project layout is already close to canonical v1.7: it already uses `preambles/`, `templates/`, `AGENT_BOOTSTRAP.md`, and `docs/agents/startup-prompts/`.
- The main gaps are missing files and outdated schemas, not structural drift.
- Once the missing files exist, a Protocol Enforcer can sync the rest with relatively low migration risk.

### Highest-Risk Sync Diffs

1. `CRUCIBLE/docs/interfaces.md` does not exist.
   The new handoff and planning flow expects a canonical cross-layer contract file.
   Risk: upgraded handoffs will reference a file that is not there.

2. The handoff and session-summary templates are still pre-v1.7.
   Current files:
   - `CRUCIBLE/templates/handoff-packet.md`
   - `CRUCIBLE/templates/session-summary.md`

   They are missing:
   - durable-artifact metadata
   - exact output path
   - working directory / project root
   - interface-contract section
   - routing recommendation
   - exit checklist
   - follow-up items
   - self-assessment

3. `CRUCIBLE/preambles/COMMON_RULES.md` lacks the universal exit sequence.
   Current file has strong basics, but v1.7 now relies on explicit end-of-session sequencing to prevent artifact omission.

4. `CRUCIBLE/preambles/ORCHESTRATOR.md` is close, but still missing the new v1.7 rails:
   - read-before-assert
   - dispatch-readiness checklist
   - follow-up backlog promotion
   - fresh-Orchestrator self-assessment when context confidence drops
   - re-atomization after design or validation changes task shape

5. `CRUCIBLE/preambles/ARCHITECT.md` still treats plans as ad hoc markdown instead of `templates/plan.md`.
   Risk: once the root sync lands, the project may still produce plans that do not match the master schema.

6. Startup prompts are missing `kickstart.md`.
   The project already has role prompts, so this is an additive, low-drama fix.

### Merge Notes

- Preserve CRUCIBLE-specific layer language in `ARCHITECT.md`:
  sandbox, middleware, telemetry, CLI, types.
- Preserve CRUCIBLE-specific pitfalls in `AGENT_BOOTSTRAP.md`.
- Do not ask the Enforcer to invent `docs/architecture.md` or `docs/constraints.md` content. Those are still Architect/operator-owned. If they are missing, the Enforcer should flag them as required follow-up.

### Concrete Evidence

- `CRUCIBLE/AGENT_BOOTSTRAP.md` uses canonical `preambles/` paths already, but does not mention `docs/interfaces.md`.
- `CRUCIBLE/templates/handoff-packet.md` is missing the v1.7 metadata and dispatch fields.
- `CRUCIBLE/templates/session-summary.md` is missing the v1.7 exit/routing/follow-up sections.
- `CRUCIBLE/docs/agents/startup-prompts/` exists but has no `kickstart.md`.

---

## DjTools/scue

### Update First

1. Decide path strategy for role preambles:
   - canonicalize to `DjTools/scue/preambles/`, or
   - explicitly declare a project-local exception and update `AGENT_BOOTSTRAP.md` plus all prompts/templates to match

2. Create `DjTools/scue/docs/interfaces.md` and reconcile it with `DjTools/scue/docs/CONTRACTS.md`

3. Create `DjTools/scue/templates/plan.md`

4. Create `DjTools/scue/docs/agents/startup-prompts/kickstart.md`

5. Update `DjTools/scue/AGENT_BOOTSTRAP.md`

6. Update `DjTools/scue/templates/handoff-packet.md`
7. Update `DjTools/scue/templates/session-summary.md`
8. Update `DjTools/scue/templates/validator-verdict.md`
9. Update `DjTools/scue/templates/orchestrator-state.md`

10. Carefully merge:
    - `DjTools/scue/docs/agents/preambles/COMMON_RULES.md`
    - `DjTools/scue/docs/agents/preambles/ORCHESTRATOR.md`
    - `DjTools/scue/docs/agents/preambles/ARCHITECT.md`
    - `DjTools/scue/docs/agents/preambles/DEVELOPER.md`
    - `DjTools/scue/docs/agents/preambles/VALIDATOR.md`
    - `DjTools/scue/docs/agents/preambles/QA_TESTER.md`
    - `DjTools/scue/docs/agents/preambles/DESIGNER.md`
    - `DjTools/scue/docs/agents/preambles/RESEARCHER.md`

11. Update `DjTools/scue/docs/agents/startup-prompts/orchestrator.md` and sibling prompts

12. Review overlapping legacy docs for supersession or pointer treatment:
    - `DjTools/scue/docs/agents/ORCHESTRATOR_PROMPT.md`
    - `DjTools/scue/docs/agents/HANDOFF_CONTRACTS.md`
    - `DjTools/scue/docs/agents/AGENT_ROSTER.md`
    - `DjTools/scue/docs/agents/README.md`

### Why These Go First

- SCUE is not just schema-drifted; it is path-drifted.
- A generic v1.7 handoff or startup prompt will point at `preambles/...`, but SCUE still points at `docs/agents/preambles/...`.
- The project also has a mature, customized contract model in `docs/CONTRACTS.md`, so a naïve root sync could either break references or erase useful project-specific guidance.

### Highest-Risk Sync Diffs

1. Preamble path migration.
   Current bootstrap and prompts still point to:
   - `docs/agents/preambles/COMMON_RULES.md`
   - `docs/agents/preambles/[ROLE].md`

   If the root templates are copied in blindly, new handoffs will reference nonexistent `preambles/*` files.

2. `docs/CONTRACTS.md` versus `docs/interfaces.md`.
   SCUE is deeply invested in `docs/CONTRACTS.md`.
   v1.7 assumes `docs/interfaces.md`.

   Recommended safe migration:
   - create `docs/interfaces.md`
   - migrate current contract content into it
   - leave `docs/CONTRACTS.md` as a pointer or explicitly superseded compatibility document
   - then update preambles, templates, and prompts to reference `docs/interfaces.md`

3. SCUE’s `COMMON_RULES.md` contains project-specific behavioral rails that should not be flattened:
   - FE state behavior is operator-owned
   - confirm-understanding gate
   - LEARNINGS append requirement
   - a rich project-doc index

   Risk: a generic sync could accidentally delete useful SCUE-specific safeguards while adding v1.7 global ones.

4. SCUE’s `handoff-packet.md` includes a custom `## State Behavior` section for FE tasks.
   This is valuable local discipline.
   Risk: the root template does not have that exact section, so overwriting blindly would lose useful UI-state guidance.

5. SCUE has overlapping workflow docs beyond the preambles and startup prompts.
   Risk: even after sync, operators may keep reading stale files like `docs/agents/ORCHESTRATOR_PROMPT.md` or `docs/agents/HANDOFF_CONTRACTS.md` unless they are marked superseded or turned into pointers.

### Merge Notes

- Preserve SCUE’s custom `templates/ui-state-behavior.md`. There is no root master replacement for it.
- Preserve project-specific QA guidance hooks in `QA_TESTER.md` if they exist.
- Preserve FE-specific operator-decision safeguards in `COMMON_RULES.md`.
- Preserve custom agent roster material if it still drives task-assignment conventions.

### Recommended Safe Migration Order

1. Path decision
2. Contract-doc migration (`CONTRACTS.md` → `interfaces.md`)
3. Template schema upgrade
4. Preamble merge
5. Startup-prompt rewrite
6. Bootstrap rewrite
7. Legacy-doc supersession pass

Do not reverse this order. If handoffs are upgraded before path and contract references are reconciled, the project will generate formally correct but operationally broken packets.

### Concrete Evidence

- `DjTools/scue/AGENT_BOOTSTRAP.md` still points to `docs/agents/preambles/...`
- `DjTools/scue/docs/agents/preambles/COMMON_RULES.md` hard-codes `docs/CONTRACTS.md` and `docs/agents/preambles/...`
- `DjTools/scue/docs/agents/preambles/ARCHITECT.md` still requires updates to `docs/CONTRACTS.md`
- `DjTools/scue/templates/handoff-packet.md` still embeds old preamble paths and lacks v1.7 metadata/dispatch/output fields
- `DjTools/scue/docs/agents/startup-prompts/` exists but has no `kickstart.md`

---

## Recommended Enforcer Strategy

When syncing either project, the Protocol Enforcer should:

1. Read the root `templates/` master files first
2. Read the project’s existing preambles and startup prompts
3. Identify local rules worth preserving before generating replacements
4. Create missing files before rewriting dependent files
5. Mark or isolate superseded workflow docs rather than leaving parallel “active” instructions around

For `CRUCIBLE`, this is mostly a schema-upgrade pass.
For `DjTools/scue`, this is a migration-plus-schema-upgrade pass.
