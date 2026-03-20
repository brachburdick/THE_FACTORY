# Meta-Infrastructure v1.9.1: Task-Type Routing & Flow Skills

## Preamble

You are applying the second phase of the meta-infrastructure migration. Phase 1 (v1.9) has already been completed. The following are now in place:

- One default operator agent (no standing roles)
- CLAUDE.md ≤200 lines with constitution + trigger table
- Progressive-disclosure skills replacing old agent preambles
- Structured task state (JSONL/SQLite/Beads) replacing session markdown
- One JSON Schema-validated handoff envelope
- Eval scaffold at `.agent/evals/`
- Hot/warm/cold memory tiering
- v1.8 archived at tag `v1.8-final`, branch `archive/meta-infra-v1.8`

This phase (v1.9.1) adds:

- Task-type classification and routing via flow skills
- Predefined step sequences per task type (eliminating agent re-planning)
- Token profiling protocol for measuring infrastructure efficiency
- Domain skill ↔ flow skill integration
- Updated scoring and version tracking

---

## Phase 1: Build the Initial Flow Skills (Start With Three)

Do NOT build all eight task categories at once. Start with the three that cover ~80% of daily work: **bug fix**, **new feature**, and **refactor**. The remaining categories (migration, test generation, documentation, investigation, configuration/infra) will be added incrementally after these three are validated.

### 1.1 — Create the Debug Flow Skill

Create `.claude/skills/debug-flow/SKILL.md`:

```markdown
---
name: debug-flow
description: >
  Use when the task involves fixing a bug, error, regression, failing test,
  unexpected behavior, or production incident. Signals: "fix", "broken",
  "failing", "error", "regression", "not working", "crash", "timeout".
---

# Debug Flow: Reproduce → Isolate → Diagnose → Fix → Verify

## Phase 1: Reproduce
**Goal:** Confirm the bug exists and create a minimal reproduction.
**Steps:**
1. Read the bug report or failing test. Identify the expected vs. actual behavior.
2. If a test exists that demonstrates the failure, run it. Confirm it fails.
3. If no test exists, write one that captures the reported behavior. Run it. Confirm failure.
4. Record the reproduction in the task tracker: `status: reproducing`, attach test file path.

**Gate:** A failing test exists that demonstrates the bug. Do NOT proceed without this.

## Phase 2: Isolate
**Goal:** Narrow the failure to the smallest possible surface area.
**Steps:**
1. Identify which files, modules, or services are involved.
2. For cross-project issues (federated GraphQL, shared packages): determine which subgraph
   or service owns the failure. Check if the issue crosses a subgraph boundary.
3. For async/event-driven issues: check Redis pub/sub, MongoDB change streams, or
   WebSocket handlers for timing or ordering problems.
4. Read only the files in the failure path. Do NOT read unrelated code.

**Gate:** You can name the specific function, handler, or query where the bug originates.

## Phase 3: Diagnose
**Goal:** Understand the root cause, not just the symptom.
**Steps:**
1. Explain the root cause in 1-2 sentences. Write it down before coding.
2. Check: is this a recurrence of a known pattern? Search `.agent/evals/` and
   the CLAUDE.md gotchas section for related failures.
3. If three fix attempts have failed, STOP. Escalate to the human with a diagnostic
   summary. Do not continue iterating blindly.

**Gate:** Root cause is documented. Fix approach is stated before implementation begins.

## Phase 4: Fix
**Goal:** Minimal change that addresses the root cause.
**Steps:**
1. Make the smallest change that fixes the root cause. Do NOT refactor surrounding code.
2. Run the reproduction test. Confirm it passes.
3. Run the broader test suite for the affected module. Confirm no regressions.

**Gate:** Reproduction test passes. No new test failures.

## Phase 5: Verify & Close
**Steps:**
1. Update task tracker: `status: complete`, attach fix summary.
2. If this bug pattern is likely to recur, file an eval case in `.agent/evals/`.
3. If the fix reveals a broader architectural issue, file a separate investigation task.
   Do NOT scope-creep the current fix.

**Anti-patterns to avoid:**
- Do NOT refactor while fixing. Refactoring is a separate task type.
- Do NOT add features while fixing. Feature work is a separate task type.
- Do NOT write more than one reproduction test initially. One is enough to gate Phase 1.
```

### 1.2 — Create the Feature Flow Skill

Create `.claude/skills/feature-flow/SKILL.md`:

```markdown
---
name: feature-flow
description: >
  Use when the task involves building new functionality, adding a capability,
  implementing a user story, creating a new endpoint/resolver/component, or
  extending existing behavior. Signals: "implement", "add", "create", "new",
  "build", "feature", "endpoint", "resolver", "component".
---

# Feature Flow: Spec → Plan → Implement → Test → Verify

## Phase 1: Spec
**Goal:** Define what will be built, clearly enough that implementation is mechanical.
**Steps:**
1. Read the task description and any linked requirements.
2. If the feature touches a domain with a domain skill (audio analysis, DMX/lighting,
   GraphQL federation, AWS infra), load that skill now for domain-specific constraints.
3. Write a spec (or confirm one exists) that includes:
   - What the feature does (behavior, not implementation)
   - Inputs and outputs (API contracts, component props, data shapes)
   - Edge cases and error handling
   - What is explicitly OUT of scope
4. If the spec is ambiguous or missing critical details, ask the human. Do NOT assume.

**Gate:** Spec exists with defined inputs, outputs, edge cases, and scope boundaries.
Human confirmation required before proceeding.

## Phase 2: Plan
**Goal:** Break the spec into ordered implementation steps.
**Steps:**
1. Identify which files need to be created or modified.
2. List implementation steps in dependency order (e.g., schema first, then resolver,
   then tests).
3. Estimate whether this is a single-session task or needs to be broken into sub-tasks
   in the task tracker.
4. If the feature requires changes across multiple projects in the portfolio, identify
   which projects are affected and in what order changes must land.

**Gate:** Implementation plan exists with ordered steps and file list.

## Phase 3: Implement
**Goal:** Build the feature according to the plan.
**Steps:**
1. Follow the plan step by step. Do NOT skip ahead or reorder without updating the plan.
2. After each significant step, run any relevant existing tests to catch regressions early.
3. If you discover the plan is wrong or incomplete, STOP implementation. Update the plan
   first, then resume.

**Gate:** All planned implementation steps are complete.

## Phase 4: Test
**Goal:** Verify the feature works and doesn't break existing functionality.
**Steps:**
1. Write tests that cover the spec's defined behavior, edge cases, and error handling.
2. Run the new tests. All must pass.
3. Run the full test suite for the affected module(s). No regressions.
4. If the feature has a UI component, describe what manual verification the human
   should perform.

**Gate:** All new tests pass. No regressions in existing tests.

## Phase 5: Verify & Close
**Steps:**
1. Update task tracker: `status: complete`, attach summary of what was built.
2. If the feature introduced a new pattern that future features should follow,
   note it in the relevant domain skill's `references/` directory.
3. If the spec changed during implementation, update the spec to match reality.

**Anti-patterns to avoid:**
- Do NOT start implementing before the spec is confirmed by the human.
- Do NOT combine feature work with refactoring. If you spot code that should be
  refactored, file a separate refactor task.
- Do NOT write tests before implementation unless explicitly doing TDD (in which
  case, the plan should state this).
```

### 1.3 — Create the Refactor Flow Skill

Create `.claude/skills/refactor-flow/SKILL.md`:

```markdown
---
name: refactor-flow
description: >
  Use when the task involves restructuring code without changing behavior.
  Signals: "refactor", "extract", "consolidate", "clean up", "simplify",
  "reorganize", "dedup", "reduce complexity", "split", "merge module".
---

# Refactor Flow: Scope → Snapshot → Transform → Verify

## Phase 1: Scope
**Goal:** Define exactly what will change and what must be preserved.
**Steps:**
1. Read the refactor request. Identify the target code.
2. Read ALL files in the affected area. Understand the current structure before changing it.
3. Define the refactor boundary:
   - What files/modules are in scope?
   - What behavior must be preserved? (List specific tests or observable behaviors.)
   - What is explicitly out of scope?
4. If the refactor crosses project boundaries, identify all affected projects.

**Gate:** Scope boundary is defined. Preservation criteria are stated.

## Phase 2: Snapshot
**Goal:** Establish a behavioral baseline before any changes.
**Steps:**
1. Run the existing test suite for the affected area. Record results.
2. If test coverage is insufficient to verify behavior preservation, write
   characterization tests FIRST that capture current behavior.
3. Commit the characterization tests separately (they are not part of the refactor).

**Gate:** Test suite passes. You have sufficient coverage to detect behavioral changes.

## Phase 3: Transform
**Goal:** Restructure the code while preserving all behavior.
**Steps:**
1. Make structural changes incrementally. After each significant change, run tests.
2. Do NOT change behavior. If you find a bug while refactoring, file a separate
   bug fix task. Do NOT fix it as part of the refactor.
3. Do NOT add new features. If the refactored structure enables a new capability,
   file a separate feature task.

**Gate:** All structural changes are complete. Tests still pass.

## Phase 4: Verify & Close
**Steps:**
1. Run the full test suite. Compare results to the Phase 2 snapshot.
   Results must be identical (same passes, same failures — no new failures,
   no mysteriously fixed tests).
2. Update task tracker: `status: complete`, attach summary of structural changes.
3. If the refactor established a new pattern (e.g., extracted a component library,
   established a service boundary), document it in the relevant domain skill or
   project CLAUDE.md gotchas section.

**Anti-patterns to avoid:**
- Do NOT change behavior during a refactor. This is the cardinal rule.
- Do NOT skip the snapshot phase. Without a baseline, you can't verify preservation.
- Do NOT refactor and add features simultaneously. Ever.
```

---

## Phase 2: Update the CLAUDE.md Trigger Table

Add the task-type routing section to the existing CLAUDE.md. This goes in the trigger table alongside the domain skill triggers already in place from v1.9.

```markdown
## Task-Type Flow Routing

Before starting any task, classify it and load the appropriate flow skill.
If a task spans multiple types, choose the PRIMARY type and note the secondary.
Do NOT blend flows — complete one flow, then start the next if needed.

| Signal in task description | Flow to load | Posture |
|---|---|---|
| fix, bug, error, broken, regression, failing, crash, timeout | debug-flow/ | Minimal change. Reproduce first. |
| implement, add, create, new, build, feature, endpoint, resolver | feature-flow/ | Spec first. Human confirms before coding. |
| refactor, extract, consolidate, clean up, simplify, reorganize | refactor-flow/ | Read first. No behavior change. |
| migrate, upgrade, convert, move from X to Y, change module system | (future: migration-flow/) | Currently: use feature-flow with extra caution. |
| write tests, test coverage, add tests for | (future: test-gen-flow/) | Currently: use feature-flow Phase 4 expanded. |
| investigate, research, understand, analyze, why does, trace | (future: investigation-flow/) | Currently: read-only, report to human. |
| document, JSDoc, README, spec a contract | (future: doc-flow/) | Currently: treat as feature-flow with no test phase. |
| env vars, config, Lambda, infra, deployment | (future: config-flow/) | Currently: use debug-flow with blast-radius check. |

### Flow + Domain Skill Interaction
Flow skills define the SEQUENCE (what steps to follow).
Domain skills define the KNOWLEDGE (what patterns and constraints apply).
Both may be loaded simultaneously. The flow drives the steps; the domain informs decisions within each step.

Example: "Add rekordbox metadata parsing to the audio analysis pipeline"
→ Flow: feature-flow/ (it's a new capability)
→ Domain: scue-audio-analysis/ (it needs rekordbox-specific knowledge)
```

---

## Phase 3: Integrate Flow Skills with Existing Infrastructure

### 3.1 — Update the Handoff Schema

Add a `taskType` field to the existing handoff JSON Schema:

```json
{
  "taskType": {
    "type": "string",
    "enum": ["debug", "feature", "refactor", "migration", "test-gen",
             "investigation", "documentation", "config-infra"],
    "description": "Determines which flow skill the receiving agent loads"
  }
}
```

This field goes in the `required` array. The receiving agent uses it to load the correct flow skill without re-classifying.

### 3.2 — Update the Task Tracker Schema

Add task type and flow phase tracking to your structured task state:

```json
{
  "id": "task-042",
  "taskType": "debug",
  "flowPhase": "isolate",
  "status": "in-progress",
  "summary": "Fix timeout in user-profile resolver under high concurrency",
  "gateStatus": {
    "reproduce": "passed",
    "isolate": "in-progress",
    "diagnose": "pending",
    "fix": "pending",
    "verify": "pending"
  },
  "domainSkill": "graphql-federation",
  "blockers": [],
  "updated": "2026-03-20T14:00:00Z"
}
```

The `gateStatus` object tracks progress through the flow phases. This replaces the need for session artifact files — a single task entry shows exactly where the work stands.

### 3.3 — Update the Eval Scaffold

Add flow-level evals that verify the routing and gate behavior:

```
.agent/evals/
├── flows/
│   ├── debug-flow-routes-correctly.eval.md
│   ├── feature-flow-requires-spec-gate.eval.md
│   ├── refactor-flow-no-behavior-change.eval.md
│   └── flow-escalation-on-repeated-failure.eval.md
├── conventions/   (existing from v1.9)
├── handoffs/      (existing from v1.9)
└── skills/        (existing from v1.9)
```

Example eval — `debug-flow-routes-correctly.eval.md`:

```markdown
# Eval: Debug flow routes correctly

## Should: Route bug-like tasks to debug-flow
- Input: "The user-profile resolver is timing out under load"
- Expected: Agent loads debug-flow/ skill, begins Phase 1 (Reproduce)
- Fail if: Agent starts implementing a fix without reproducing first

## Should: Route error investigation to debug-flow
- Input: "Tests in auth module are failing after the last merge"
- Expected: Agent loads debug-flow/ skill
- Fail if: Agent loads feature-flow/ or refactor-flow/

## Should NOT: Route feature requests to debug-flow
- Input: "Add rate limiting to the GraphQL gateway"
- Expected: Agent loads feature-flow/ skill
- Fail if: Agent loads debug-flow/
```

Example eval — `refactor-flow-no-behavior-change.eval.md`:

```markdown
# Eval: Refactor flow preserves behavior

## Should: Establish baseline before changes
- Input: "Extract the auth middleware into a shared package"
- Expected: Agent runs existing tests BEFORE making any code changes
- Fail if: Agent begins modifying files before running the test suite

## Should NOT: Fix bugs during refactor
- Input: "Clean up the error handling in the payment service"
  (where a bug exists in error handling)
- Expected: Agent files a separate bug task, continues refactor without fixing the bug
- Fail if: Agent changes error handling behavior as part of the refactor
```

---

## Phase 4: Token Profiling Protocol

### 4.1 — Establish Baselines

Before running any tasks through the new flow system, capture baseline measurements:

**Infrastructure overhead baseline:**
```
For 5 representative sessions across different projects:
1. Start a new Claude Code session in the project
2. Wait for CLAUDE.md and system prompt to load
3. Run /context immediately (before any task work)
4. Record:
   - Total context consumed (tokens and percentage)
   - Breakdown by category (system prompt, CLAUDE.md, MCP tools, skills metadata)
   - Free space remaining
5. Store results in .agent/metrics/baseline-v1.9.1.jsonl
```

**Per-task measurement protocol:**
```
For each task completed using a flow skill:
1. Record /context output at these checkpoints:
   a. After flow skill loads (before Phase 1 starts)
   b. After each phase gate passes
   c. At session end (before land-the-plane)
2. Record:
   - Task ID, task type, flow used, domain skill(s) loaded
   - Context percentage at each checkpoint
   - Number of phases completed
   - Whether the task required escalation or flow switching
   - Total session tokens (from /cost if available)
3. Append to .agent/metrics/task-profiles-v1.9.1.jsonl
```

### 4.2 — Metrics to Track

Create `.agent/metrics/README.md`:

```markdown
# Token Profiling Metrics

## Infrastructure Overhead Ratio
Formula: (context at task start - system prompt floor) / total context window
Target: <8% (down from estimated 15-25% in v1.8)
Measures: How much context your meta-infrastructure consumes before work begins.

## Flow Efficiency Ratio
Formula: (context consumed by productive work) / (total context consumed in session)
Target: >80%
Measures: What fraction of your context budget goes to actual problem-solving
vs. infrastructure, planning, and flow navigation.

## Phase Completion Rate
Formula: (tasks that complete all flow phases without escalation) / (total tasks)
Target: >70% for debug, >60% for feature, >80% for refactor
Measures: Whether the predefined flows actually match how tasks unfold in practice.

## Flow Accuracy
Formula: (tasks where initial classification was correct) / (total tasks)
Target: >90%
Measures: Whether the trigger table routes tasks to the right flow.
If this drops below 85%, the trigger table needs refinement.

## Gate Violation Rate
Formula: (times an agent skipped a gate or proceeded without meeting gate criteria) / (total gate transitions)
Target: <5%
Measures: Whether agents actually follow the flow or bypass it.
High rates mean the flow instructions need strengthening or the gates
need automated enforcement (hooks/scripts).
```

### 4.3 — Comparison Protocol

After 2 weeks of using the flow system, run this comparison:

```markdown
## v1.8 → v1.9 → v1.9.1 Comparison

### Infrastructure Overhead
| Version | Context at task start | System prompt floor | Infrastructure tax |
|---|---|---|---|
| v1.8 | (from archive measurements) | ~14K | (start - 14K) |
| v1.9 | (from v1.9 baselines) | ~14K | (start - 14K) |
| v1.9.1 | (from v1.9.1 baselines) | ~14K | (start - 14K) |

### Task Efficiency
| Version | Avg tokens per bug fix | Avg tokens per feature | Avg tokens per refactor |
|---|---|---|---|
| v1.8 | (estimate from session artifacts) | — | — |
| v1.9 | (from first 2 weeks) | — | — |
| v1.9.1 | (from first 2 weeks with flows) | — | — |

### Quality
| Version | Tasks requiring re-work | Gate violations | Flow misroutes |
|---|---|---|---|
| v1.9 | — | N/A | N/A |
| v1.9.1 | — | — | — |
```

---

## Phase 5: Apply to Projects

### 5.1 — Portfolio-Wide Application

For each of the 12 projects:

1. **Verify v1.9 is in place.** Confirm: CLAUDE.md ≤200 lines, domain skills created, structured task tracker active, old session artifacts deleted. If v1.9 is not complete for a project, complete it before proceeding.

2. **Add flow skills to the project.** The flow skills live at the portfolio level (shared across projects). Each project's CLAUDE.md should reference them via the trigger table. If a project has project-specific flow modifications (e.g., SCUE's debug flow should always check DMX output state), add those as notes in the project-level CLAUDE.md, not by forking the flow skill.

3. **Tag existing tasks in the tracker.** For every in-progress or queued task, add the `taskType` field. If a task doesn't fit any of the three active categories, leave it untyped for now — it will be categorized when the remaining flow skills are built.

4. **Run one task of each type through the flow system.** For each project, select:
   - One known bug to run through debug-flow
   - One planned feature to run through feature-flow
   - One identified refactor candidate to run through refactor-flow
   
   Capture token profiles for all three. This is your per-project baseline.

### 5.2 — SCUE-Specific Application

SCUE has the most complex domain interactions. Specific instructions:

1. **Flow + domain integration test.** Run a feature task that requires both the feature-flow and the scue-audio-analysis domain skill. Verify that the flow drives the steps while the domain skill informs decisions. Example task: "Add BPM confidence scoring to the analysis output."

2. **Cross-domain task test.** Run a task that crosses SCUE's domain boundaries. Example: "The DMX output is not responding to beatgrid changes from the audio analysis pipeline." This is a debug task that requires both the scue-audio-analysis and scue-dmx-output domain skills. Verify that debug-flow handles this correctly (the isolate phase should identify which domain owns the failure).

3. **RAMIFY boundary.** If RAMIFY planning is active, ensure that any SCUE tasks that touch audio reverse-engineering territory are flagged. A task like "decompose a track into component-level elements" should NOT be routed through SCUE's flows — it's a RAMIFY concern. Add a note to the trigger table or SCUE's CLAUDE.md clarifying this boundary.

### 5.3 — Backend Migration Project Application

The TypeScript/Node.js backend migration has a specific task type (migration) that doesn't have a full flow skill yet. For now:

1. Route migration tasks through feature-flow with an additional pre-phase: **Risk Assessment.** Before the spec phase, the agent must identify what could break, what tests cover the migration surface, and what the rollback plan is.

2. Add this note to the project's CLAUDE.md:
   ```
   ## Migration Tasks
   Until migration-flow/ is built, use feature-flow/ with this pre-phase:
   Phase 0 (Risk Assessment): Before writing a spec, identify blast radius,
   existing test coverage of affected code, and rollback strategy.
   The NodeNext module resolution decision is an ADR (already recorded).
   The ESM runtime flip is deferred to Phase 5 — do not implement it in
   earlier migration tasks.
   ```

---

## Phase 6: Version Tracking

### 6.1 — Update VERSION.md

Add the v1.9.1 entry:

```markdown
## v1.9.1 (2026-03-XX) — Task-Type Routing & Flow Skills
- **Architecture:** Task classification → flow skill routing → predefined step sequences
- **Flow skills:** debug-flow, feature-flow, refactor-flow (3 of 8 planned)
- **Routing:** Trigger table in CLAUDE.md, zero-cost classification (no separate model call)
- **Task tracking:** taskType and gateStatus fields added to structured task state
- **Metrics:** Token profiling protocol established, infrastructure/flow/gate metrics defined
- **Evals:** Flow routing and gate compliance evals added
- **Builds on:** v1.9 (tiered memory, progressive disclosure, structured state)
- **Git ref:** tag v1.9.1
```

### 6.2 — Score v1.9.1

Re-run the scoring rubric from v1.9 with updated scores. Expected improvements over v1.9:

| Dimension | v1.8 | v1.9 (est) | v1.9.1 (est) | Why |
|---|---|---|---|---|
| Context Efficiency | 1 | 3 | 4 | Flow skills load on demand; no re-planning overhead |
| Session Bootstrap | 1 | 4 | 4 | Unchanged from v1.9 (already fast) |
| Anti-Drift | 1 | 3 | 4 | Flow gate evals + routing evals added |
| Doc Freshness | 2 | 4 | 4 | Unchanged (keep/delete filter already applied) |
| Session Hygiene | 1 | 4 | 5 | gateStatus in tracker eliminates all session artifacts |
| Handoff Reliability | 2 | 4 | 5 | taskType field + flow skill = unambiguous handoff |
| Scalability | 2 | 4 | 4 | New projects inherit flow skills automatically |

---

## Execution Order

1. **Create the three flow skills** (Phase 1). These are the foundation everything else depends on.
2. **Update CLAUDE.md trigger table** (Phase 2). Connect routing to the new skills.
3. **Update handoff schema and task tracker** (Phase 3.1, 3.2). Add taskType and gateStatus fields.
4. **Add flow evals** (Phase 3.3). Verify routing and gate behavior.
5. **Capture token baselines** (Phase 4.1). Measure before running tasks through flows.
6. **Apply to all projects** (Phase 5.1). Verify v1.9, add flow references, tag existing tasks.
7. **Run pilot tasks** (Phase 5.1 step 4). One of each type per project, with token profiling.
8. **SCUE-specific tests** (Phase 5.2). Cross-domain and flow+domain integration.
9. **Backend migration notes** (Phase 5.3). Interim migration handling.
10. **Update VERSION.md and score** (Phase 6). Record the new state.

## Future Work (NOT in this phase)

These are deferred to v1.9.2 or later, after the initial three flows are validated:

- **migration-flow/** — Will be built when the backend migration reaches its next phase
- **test-gen-flow/** — Will be built when test coverage becomes a focused initiative  
- **investigation-flow/** — Will be built when research/analysis tasks become frequent enough to justify a dedicated flow
- **doc-flow/** — Lowest priority; documentation tasks are infrequent
- **config-flow/** — Will be built if config/infra tasks show repeated patterns
- **Automated gate enforcement** — Hooks or scripts that prevent phase transitions without meeting gate criteria. Currently gates are instruction-based (the flow tells the agent to stop); automated enforcement is a v1.9.2+ concern.
- **Flow analytics dashboard** — Visualization of token profiles, gate pass rates, and flow accuracy over time. Currently tracked as JSONL; a dashboard is a nice-to-have.
