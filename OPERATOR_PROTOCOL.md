# Operator Protocol

> **Version:** 1.8
> **Last reviewed:** 2026-03-19
> **Improvements backlog:** See `PROTOCOL_IMPROVEMENTS.md`

> **What this is:** Your operating manual for a multi-agent development system.
> Single source of truth for roles, workflows, artifact schemas, quality gates, and escalation patterns.

---

## 1. System Architecture

### 1.1 Roles

| Role | Reads Code? | Writes Code? | Primary Output | Invoked By | Claude Code Tools |
|------|-------------|--------------|----------------|------------|-------------------|
| **Orchestrator** | No | No | Handoff packets, priority ordering, progress assessments | You (human) | All (parent session) |
| **Architect** | Yes (read-only) | No | Specs, plans, task breakdowns, interface definitions, ADRs | Orchestrator handoff | Read, Grep, Glob |
| **Researcher** | No | No | Structured findings documents | Any role via Research Request | Read, Grep, Glob, WebSearch, WebFetch |
| **Designer** | No | No | UI specs, component hierarchies, state flow diagrams | Orchestrator handoff (when plan includes UI) | Read, Grep, Glob |
| **Developer** | Yes (scoped) | Yes (scoped) | Code changes, session summaries | Orchestrator handoff | Read, Write, Edit, Bash, Grep, Glob |
| **Validator** | Yes (read-only) | No | Pass/fail verdicts with evidence | Automatically after each Developer session | Read, Grep, Glob, Bash |
| **QA Tester** | Yes (read-only) | No | QA verdicts, updated test scenario matrices | Orchestrator handoff (Phase 6a: bug fixes, FE-BE integration, or operator request) | Read, Grep, Glob, Bash |
| **Protocol Enforcer** | No | No (docs only) | Updated preambles, templates, AGENT_BOOTSTRAP.md | You (human), at workspace root — not a project agent; no project preamble | Read, Write, Edit, Grep, Glob |

### 1.2 Core Principles

1. **Fresh context for fresh agents.** Every role transition = new conversation. No carried-forward history.
2. **Spec before code.** If it's not in the spec, the agent will make it up.
3. **Interfaces before implementations.** Define how layers talk before building either side.
4. **Artifacts are the communication channel.** Agents coordinate through structured files on disk, never directly.
5. **You are the editor, not the author.** Agents draft; you review, approve, and route.
6. **Validate every task.** Developer → Validator → next task. No exceptions.

### 1.3 The Human Operator's Job

You do three things:

- **Route**: Start sessions, load the right context, deliver artifacts between agents.
- **Decide**: Resolve `[DECISION NEEDED]` tags, approve specs, accept or reject Validator verdicts.
- **Curate**: Distill research into skill files, prune stale docs, keep the project's knowledge base clean.

You do NOT:
- Write handoff packets from scratch (the Orchestrator agent drafts them).
- Make architectural decisions in Developer sessions (that's the Architect's job).
- Debug code (that's the Developer's job, gated by the Validator).

### 1.4 When to Create a Role vs. a Skill File

A **role** is a distinct agent persona with its own preamble, tool restrictions, artifact schemas, and position in the workflow. A **skill file** is domain knowledge loaded into an existing role's context.

| Signal | → Role | → Skill File |
|--------|--------|--------------|
| Changes *how the agent reasons* (different evaluation criteria, different output structure) | Yes | No |
| Changes *what the agent knows* (domain facts, API patterns, framework conventions) | No | Yes |
| Requires unique tool restrictions (e.g., Bash but no Write) | Yes | No |
| Produces a distinct artifact type not used by existing roles | Yes | No |
| Applies to a single project's domain (e.g., DSP theory, DJ workflow) | No | Yes |
| Applies across all projects (e.g., validation, QA testing) | Yes | No |

**The test:** If you removed the capability and gave its instructions to an existing role, would that role need to fundamentally change how it operates? If yes → new role. If the existing role just needs more knowledge → skill file.

**Examples:**
- QA Tester: new role. Requires running the system (unique tool set), produces QA Verdicts (unique artifact), reasons about live behavior not code structure (different evaluation mode).
- TypeScript conventions: skill file. A Developer with TypeScript knowledge is still a Developer — same tools, same artifacts, same reasoning mode.
- Pro DJ Link protocol details: skill file. The Architect or Developer loads it when working on bridge features.

### 1.5 When to Add a New Role or Phase

Default to the smallest change that can close the failure:

1. Fix the artifact schema or checklist first.
2. Add a mode, tag, or skill file second.
3. Add a new role or workflow phase only after repeated failure or clear eval improvement.

**Promotion rule:** A new role or phase should be backed by at least one of:
- 2+ logged failures that current roles/checklists could not prevent
- A recurring task that truly needs unique tools or a distinct artifact
- A measured quality gain on a representative eval set

This keeps the system from accumulating coordination overhead faster than it accumulates useful specialization.

---

## 2. Artifact Schemas

Every artifact exchanged between agents must follow its schema. If a required field is missing, the artifact is incomplete — send it back.

### 2.0 Artifact Metadata (Required for Durable Artifacts)

All durable artifacts use YAML frontmatter for metadata. There are two tiers:

**Full metadata** — for planning artifacts (handoffs, specs, plans, task breakdowns, UI specs, review reports) where the author knows the lineage:

```markdown
---
status: [DRAFT | APPROVED | IN_PROGRESS | COMPLETE | SUPERSEDED | ARCHIVED]
project_root: [/absolute/path/to/project]
revision_of: [artifact path or "none"]
supersedes: [artifact path(s) or "none"]
superseded_by: [artifact path(s) or "none"]
---
```

**Slim metadata** — for session summaries and verdicts, where supersession tracking is the Validator's job:

```markdown
---
status: [COMPLETE | PARTIAL | BLOCKED]
project_root: [/absolute/path/to/project]
---
```

Rules:
- If an artifact is replaced, mark the old one `SUPERSEDED`. Do not leave operators guessing which version is current.
- If an artifact contains unresolved `[ASK OPERATOR]` or `[DECISION NEEDED]` markers and those decisions later arrive, the next step is a revision pass on that artifact before dispatching an implementing agent.
- Status is part of the contract. Never infer whether an artifact is current from timestamps alone.
- YAML frontmatter is machine-parseable by standard libraries. Do not use blockquote metadata (`> Status: ...`) — use frontmatter exclusively.

### 2.1 Handoff Packet

**Drafted by:** Orchestrator agent
**Reviewed by:** You
**Consumed by:** Any role receiving a task

```markdown
# Handoff Packet: [TASK_ID]

---
status: APPROVED
project_root: [/absolute/path/to/project]
revision_of: [artifact path or "none"]
supersedes: [artifact path(s) or "none"]
superseded_by: [artifact path(s) or "none"]
---

## Dispatch
- Mode: [ORCHESTRATOR DISPATCH | DIRECT DISPATCH]
- Output path: [exact artifact path this agent must write before ending the session]
- Parallel wave: [wave ID or "none"]

## Objective
[One sentence: what must be true when this task is done.]

## Role
[Which role should execute this: Architect | Researcher | Designer | Developer | Validator | QA Tester]

## Working Directory
- Run from: [usually the project root; be explicit]
- Related feature/milestone: [name]

## Scope Boundary
- Files this agent MAY read/modify:
  - [explicit file paths or glob patterns]
- Files this agent must NOT touch:
  - [explicit exclusions]

## Context Files
[Paths to files the agent should read before starting. Not pasted content — paths only.]
- `docs/architecture.md`
- `docs/interfaces.md`
- `specs/feat-name/spec.md`
- `specs/feat-name/tasks.md` (task #N only)

## Interface Contracts
- [Exact interface file(s), signatures, payload shapes, or contract artifact paths this task must respect]
- [If parallel work is in flight: define the ownership split and shared boundary here. Otherwise: "none"]

## Required Output
- Write: `[exact output path from Dispatch section]`
- If you supersede an existing artifact, mark it `SUPERSEDED` before session end.
- If you discover backlog-worthy follow-up items that are out of scope, capture them in the session summary under `## Follow-Up Items`.

## Constraints
- [Non-negotiable rules for this task]
- [E.g., "Do not modify any existing API endpoints"]
- [E.g., "All new functions must have JSDoc comments"]

## Acceptance Criteria
- [ ] [Specific, testable condition]
- [ ] [Specific, testable condition]
- [ ] [All pre-existing tests pass]

## Dependencies
- Requires completion of: [TASK_ID(s) or "none"]
- Blocks: [TASK_ID(s) or "none"]

## Open Questions
[Any unresolved items. If this section is non-empty for a Developer handoff, STOP. Resolve these before dispatching.]
```

### 2.2 Session Summary

**Written by:** Every agent at end of session
**Consumed by:** Validator (for compliance check), Orchestrator (for state updates), next agent in sequence

The session summary contains **producer-owned fields only** — facts that map directly to what the agent just experienced. Compliance interpretation (artifact completeness, scope compliance, recommended next step, supersession tracking) is the Validator's job (see §2.7). The hook enforces the existence gate (file exists at the expected path).

```markdown
# Session Summary: [TASK_ID]

---
status: [COMPLETE | PARTIAL | BLOCKED]
project_root: [/absolute/path/to/project]
---

## Role
[Which role performed this session. For Orchestrator self-resolved fixes: "Orchestrator-inline".]

## Objective
[Restate from handoff packet]

## Status
[COMPLETE | PARTIAL | BLOCKED]

## Work Performed
- [Bullet list of what was actually done]

## Files Changed
- `path/to/file.ts` — [what changed and why]
- [Or "None"]

## Artifacts Produced
- `path/to/artifact.md` — [what it is]
- [Or "None"]

## Interfaces Added or Modified
- [Any new or changed function signatures, API endpoints, type definitions]
- [Include the exact signature, not prose description]
- [Or "None"]

## Decisions Made
- [Decision]: [Rationale]. Alternative considered: [what was rejected and why].
- [Or "None"]

## Scope Violations
- [Any moment the agent needed to touch out-of-scope files, or "None"]

## Remaining Work
- [What's left undone, or "None"]

## Blocked On
- [If status is BLOCKED: what specific question or dependency is unresolved]
- [Or "None"]

## Missteps
- [Tool failures, wrong commands, retries, or environment surprises encountered during this session. Be specific: what was tried, what failed, what worked instead. "None" is valid.]

## Learnings
- [Gotchas, surprises, or domain knowledge worth capturing in a skill file, or "None"]

## Follow-Up Items
- [Out-of-scope improvements, tuning opportunities, or future tasks worth tracking. "None" is valid.]
```

**Removed fields** (moved to Validator Verdict or eliminated):
- `Revision Of` / `Supersedes` / `Superseded By` metadata — collapsed to `## Supersession` in the Validator Verdict. The producing agent rarely knows the full supersession chain.
- `Artifacts Superseded` — subsumed by Validator's `## Supersession`.
- `Routing Recommendation` — moved to Validator Verdict as expanded `## Recommended Next Step`.
- `Exit Checklist` — eliminated. The hook enforces the existence gate; the Validator checks completeness. A self-reported checklist adds compliance load without enforcement value.
- `Self-Assessment` — moved to Validator Verdict. The Validator's confidence in the verdict is the meaningful assessment.

**Retained fields** (producer knows these best):
- `Artifacts Produced` — only the producer knows exactly what it wrote and where.
- `Interfaces Added or Modified` — only the producer knows what signatures it created.
- `Follow-Up Items` — the producer surfaces these during work; the Orchestrator promotes them.

### 2.3 Research Request

**Generated by:** Any agent that hits the 2-attempt rule
**Consumed by:** Researcher agent

```markdown
# Research Request: [SHORT_TITLE]

## Requesting Role
[Which role generated this request]

## Context
[What the agent was trying to do when it got stuck. 2-3 sentences max.]

## Specific Questions
1. [Precise, answerable question]
2. [Precise, answerable question]

## What Was Already Tried
- Attempt 1: [What was tried, what happened]
- Attempt 2: [What was tried, what happened]

## What a Good Answer Looks Like
[Describe the format/specificity needed. E.g., "I need a working code snippet, not a conceptual explanation."]

## Relevant Files
- [Paths the Researcher should examine for context]
```

### 2.4 Research Findings

**Written by:** Researcher agent
**Consumed by:** Requesting agent (in a new session), skill file curation

```markdown
# Research Findings: [SHORT_TITLE]

## Questions Addressed
1. [Restate from request]

## Findings

### Question 1: [Restate]
**Answer:** [Direct answer, 2-3 sentences]

**Detail:**
[Supporting explanation with sources]

**Sources:**
- [Source, date, relevance: HIGH/MEDIUM/LOW]

**Confidence:** [HIGH | MEDIUM | LOW — with explanation if not HIGH]

## Recommended Next Steps
1. [Concrete action the requesting agent should take]
2. [Concrete action]

## Skill File Candidates
[Any findings that should be distilled into a permanent skill file. Flag the relevant skill file path.]
```

### 2.5 Spec (Feature Specification)

**Written by:** Architect agent
**Reviewed by:** You

```markdown
# Spec: [FEATURE_NAME]

## Summary
[What this feature does, in one paragraph.]

## User-Facing Behavior
[What the user/consumer sees or experiences. Not implementation details.]

## Technical Requirements
- [Requirement with acceptance criterion]
- [Requirement with acceptance criterion]

## Interface Definitions
[Exact type definitions, function signatures, API contracts. Copy-pasteable, not prose.]

```typescript
// Example — replace with actual definitions
interface ProDJLinkBeat {
  trackId: number;
  bpm: number;
  currentBeat: number;
  currentPhrase: number;
  timestamp: number;
}
```

## Layer Boundaries
- **Layer X** is responsible for: [scope]
- **Layer Y** is responsible for: [scope]
- Interface between X and Y: [reference to interface definition above]

## Constraints
- [Non-negotiable rules]

## Out of Scope
- [What this feature explicitly does NOT include]

## Open Questions
- `[DECISION NEEDED]`: [Question requiring human decision before implementation]

## Edge Cases
- [Edge case]: [Expected behavior]
```

### 2.5a Plan (Implementation Plan)

**Written by:** Architect agent
**Reviewed by:** You

```markdown
# Plan: [FEATURE_NAME]

---
status: [DRAFT | APPROVED | SUPERSEDED]
project_root: [/absolute/path/to/project]
revision_of: [artifact path or "none"]
supersedes: [artifact path(s) or "none"]
superseded_by: [artifact path(s) or "none"]
---

## Summary
[How this feature will be implemented at a high level.]

## Workstreams
- [Workstream name]: [scope, ownership, and why it is separated]

## Interfaces and Contracts
- [Which existing or new interfaces must be created, updated, or preserved]
- [Reference `docs/interfaces.md` and any feature-local contract notes]

## Sequencing
1. [What must happen first]
2. [What can happen in parallel]
3. [What depends on prior verification or design]

## Risks
- [Implementation risk]: [mitigation]

## Validation Strategy
- Static validation: [what Validator should be able to confirm]
- QA verification: [what requires live verification, if any]

## Open Questions
- `[DECISION NEEDED]`: [Question requiring human decision before implementation]
```

### 2.6 Task Breakdown

**Written by:** Architect agent
**Reviewed by:** You (apply atomization test to each)

```markdown
# Tasks: [FEATURE_NAME]

## Dependency Graph
[Which tasks must complete before others can start. Use task IDs.]

## Tasks

### TASK-001: [Short descriptive name]
- **Layer:** [Which architectural layer]
- **Estimated effort:** [< 30 min]
- **Depends on:** [TASK-ID or "none"]
- **Scope:** [Files this task touches]
- **Inputs:** [What must exist before this task starts]
- **Outputs:** [What must exist after this task completes]
- **Interface Scope:** [CONTRACT_ONLY | PRODUCER | CONSUMER | END_TO_END | NONE]
- **Acceptance Criteria:**
  - [ ] [Testable condition]
  - [ ] [Testable condition]
  - [ ] [All pre-existing tests pass]
- **Context files:** [Paths the Developer needs]
- **Status:** [ ] Not started / [x] Complete / [~] Partial / [!] Blocked
```

**Interface Scope tagging:**
- `CONTRACT_ONLY`: This task defines or updates the contract (docs/interfaces.md, type definitions, test fixtures). No implementation.
- `PRODUCER`: This task implements the producing side of a contract. Must reference a completed CONTRACT_ONLY task or existing stable contract.
- `CONSUMER`: This task implements the consuming side. Same constraint.
- `END_TO_END`: This task validates field parity across the full path. Typically a Validator or QA task.
- `NONE`: This task does not touch any interface boundary.

When a feature involves contract changes, the Architect should decompose into at least: one CONTRACT_ONLY task, one PRODUCER task, one CONSUMER task. These must be sequenced (contract before implementation). PRODUCER and CONSUMER may run in parallel if the contract task is complete.

### 2.7 Validator Verdict

**Written by:** Validator agent
**Consumed by:** You (to decide whether to proceed or send back)

```markdown
# Validator Verdict: [TASK_ID]

---
status: COMPLETE
project_root: [/absolute/path/to/project]
---

## Verdict: [PASS | FAIL]

## Verification Scope: [STATIC | STATIC+TESTS]
[STATIC = code review and artifact check only. STATIC+TESTS = also confirmed unit/integration tests pass. Neither implies live system verification — that is the QA Tester's scope.]

## Tests
- Pre-existing tests pass: [YES | NO — list failures]
- New tests added: [YES | NO]
- New tests pass: [YES | NO]

## Acceptance Criteria Check
- [ ] [Criterion from handoff] — [MET | NOT MET | PARTIAL — evidence]

## Scope Check
- Files modified: [list]
- Out-of-scope modifications: [list or "none"]

## Compliance Check
- Session summary exists at expected path: [YES | NO]
- Session summary has all required fields: [YES | NO — list missing]
- Artifacts declared in session summary exist on disk: [YES | NO — list missing]
- Interface changes properly flagged: [YES | NO | N/A]

## Supersession
- Artifacts superseded by this session: [list with paths, or "None"]

## What Went Well
- [Specific, evidence-based praise. "None" is valid but rare. Vague praise ("good work") is not valid — cite what was done well and why it matters.]

## Issues Found
- **[SEVERITY: CRITICAL | WARNING]**: [Description with evidence. File and line if applicable.]

## Recommended Next Step
- [NEXT TASK | QA DISPATCH | DEVELOPER RETRY | OPERATOR DECISION]
- Dispatch mode: [ORCHESTRATOR DISPATCH | DIRECT DISPATCH]
- [Why this is the correct next step]

## Recommendation
[If FAIL: specific remediation steps for the Developer's next session. If PASS: "None."]
```

### 2.8 Orchestrator State Snapshot

**Written by:** Orchestrator agent at end of every session
**Read by:** Next Orchestrator session (load immediately after preambles)
**Stored at:** `docs/agents/orchestrator-state.md` (single file, always overwritten)

```markdown
# Orchestrator State Snapshot

**Last updated:** [date] — [session file path]

## Active Milestone
[Milestone name]: [one-line status]

## Task Status
| Task ID | Status | Notes |
|---------|--------|-------|
| [ID] | [COMPLETE \| IN_PROGRESS \| BLOCKED \| PENDING] | [one line] |

## Active Sessions
| Session | Role | Task ID | Dispatch Mode | Owner | Expected Output |
|---------|------|---------|---------------|-------|-----------------|
| [session-012] | [Developer] | [TASK-006a] | [ORCHESTRATOR DISPATCH] | [Orchestrator \| Operator] | [path/to/session-summary.md] |

## Dispatch Reconciliation
- [Any direct-dispatched work since the last Orchestrator session that has now been incorporated into project state]
- [Or "None"]

## Open Blockers
- [None] or [description — what's needed to unblock and who decides]

## Pending Decisions
- `[DECISION NEEDED]`: [question — what's blocking and who needs to decide]

## Recent Context
[2–3 sentences: what happened last session, any surprises or key decisions made]

## Recurring Missteps
- [Missteps seen across 2+ sessions. Include: pattern, frequency, proposed fix (skill file entry, hook, or preamble rule). Remove once fixed.]

## Follow-Up Backlog
- [Backlog-worthy follow-up items promoted from Architect/Designer/QA artifacts]
- [Or "None"]

## Next Session Priorities
1. [Highest priority action]
2. [Second priority]
3. [Third priority]
```

This file replaces git log archaeology and verbal operator status updates. It is the first artifact the Orchestrator reads after its preamble. It is the last artifact the Orchestrator writes before ending a session.

### 2.9 Test Scenario Matrix

**Written by:** Architect (initial scenarios during spec), QA Tester (additions from testing)
**Maintained by:** QA Tester (updates after each QA session)
**Stored at:** `specs/feat-[name]/test-scenarios.md` (feature-specific) or `docs/test-scenarios/[area].md` (cross-feature, e.g., bridge lifecycle)

```markdown
# Test Scenario Matrix: [AREA_NAME]

## Hardware/System Preconditions
[Define the variable axes. Example for bridge lifecycle:]
- Board power: ON | OFF
- USB-ETH adapter: PLUGGED | UNPLUGGED
- Server: RUNNING | STOPPED
- Bridge: CONNECTED | CRASHED | WAITING_FOR_HARDWARE

## Scenarios

### SC-001: [Short descriptive name]
- **Given:** [Precondition state — e.g., "Server running, board ON, USB-ETH plugged, bridge connected"]
- **When:** [User/system action — e.g., "USB-ETH adapter is unplugged"]
- **Then:**
  - [ ] [Expected outcome 1 — e.g., "Hardware status updates within 2 seconds"]
  - [ ] [Expected outcome 2 — e.g., "Bridge transitions to waiting_for_hardware without crashing"]
  - [ ] [Expected outcome 3 — e.g., "Player elements clear or show disconnected state"]
- **Actual:** [Filled by QA Tester during execution — what actually happened]
- **Status:** [PASS | FAIL | NOT_TESTED]
- **Notes:** [Edge cases observed, timing details, related scenarios]

### SC-002: [Recovery from SC-001]
- **Given:** [State after SC-001 — e.g., "Bridge in waiting_for_hardware, USB-ETH unplugged"]
- **When:** [Recovery action — e.g., "USB-ETH adapter is plugged back in"]
- **Then:**
  - [ ] [Expected recovery — e.g., "Bridge reconnects within 10 seconds"]
  - [ ] [Expected state — e.g., "All devices reappear, player data resumes"]
- **Actual:** [...]
- **Status:** [...]
```

**Authoring rules:**
- Scenarios come in pairs: disruption + recovery. Every "When [thing breaks]" gets a corresponding "When [thing is restored]."
- The "Then" items are acceptance criteria. Write them with concrete thresholds ("within 5 seconds"), not vague expectations ("eventually recovers").
- The Architect writes initial scenarios during spec phase based on edge cases. The QA Tester adds scenarios discovered during testing.
- Scenarios are cumulative — they are not cleared after a fix. A scenario that was FAIL and becomes PASS stays in the matrix as a regression check.

### 2.10 QA Verdict

**Written by:** QA Tester agent
**Consumed by:** Orchestrator (to decide proceed vs. rework)

```markdown
# QA Verdict: [TASK_ID or BUG_ID]

## Verdict: [PASS | FAIL]

## Environment
- Server: [how started, any flags]
- Hardware: [board model, connection method, power state]
- Browser: [if FE tested]

## Scenarios Executed
| Scenario | Status | Notes |
|----------|--------|-------|
| SC-001   | PASS   |       |
| SC-002   | FAIL   | [brief] |

## Failures
### SC-002: [Name]
- **Expected:** [from test scenario matrix]
- **Observed:** [what actually happened, with timestamps if relevant]
- **Logs:** [relevant log excerpts — keep to the minimum needed to diagnose]
- **Severity:** [BLOCKING | DEGRADED | COSMETIC]

## Regression Check
- Previously passing scenarios still pass: [YES | NO — list regressions]

## Mock Tool Gaps
- [SC-XXX] requires: [capability not yet available — e.g., "simulate USB-ETH disconnect"]
[If none: "All executed scenarios had available tooling."]

## Recommendation
[If FAIL: specific guidance for the next Developer handoff. Reference scenario IDs, not vague descriptions.]
```

### 2.11 Field Inventory

**Written by:** Architect (during CONTRACT_ONLY tasks) or Developer (when handoff requires it)
**Consumed by:** Validator (for field-by-field verification), QA Tester (for fixture validation)

For any message shape, payload, or DTO under active modification, include a field inventory in the contract documentation (`docs/interfaces.md` or the relevant spec):

```markdown
| Field | Type | Required | Producer | Consumer | Tested |
|-------|------|----------|----------|----------|--------|
| [name] | [type] | [yes/no] | [layer] | [layer] | [yes/no] |
```

This table is the Validator's verification source for contract-touching tasks. The Validator checks:
- Every field listed is emitted by the producer
- Every field listed is consumed by the consumer
- Field names, types, and required/optional status match across producer and consumer
- The `Tested` column reflects actual test coverage

When a CONTRACT_ONLY task produces a field inventory, it must also produce or update a canonical fixture file in `tests/fixtures/` that downstream PRODUCER and CONSUMER tasks can use for testing.

---

## 3. Workflow Protocol

> **Claude Code note:** When running in Claude Code, the Orchestrator is always the parent session. All other roles are direct subagents of the Orchestrator — never chained through each other. Phase 4 → 4a chaining (Architect → Designer) becomes two sequential Orchestrator-spawned subagents. See Section 12 for full migration guidance.

### Phase 0: Project Bootstrap (Once Per Project)

**Protocol Enforcer** (run first — see Section 6.5 and `IMPLEMENTATION_PROMPT.md`):
1. Create the project directory structure (see Section 5).
2. Create all preambles in `preambles/` from the root templates.
3. Create all artifact templates in `templates/`.
4. Write `AGENT_BOOTSTRAP.md` skeleton (see Section 5.3).
5. Create startup prompts, including a task-scoped kickstart prompt for the first expected invocation.

**You + Architect** (after Protocol Enforcer is done):
6. Write `docs/architecture.md` with layer boundaries and interfaces.
7. Write `docs/constraints.md` with non-negotiable rules.
8. Populate initial skill files for the project's domain.

The Protocol Enforcer owns agent infrastructure. The Architect owns project-specific documentation. Do not conflate these.

### Phase 1: Scope Check (You, Before Any Agent)

Answer these yourself:
- How many layers/subsystems?
- How many features/milestones?
- Layers × features > 10? → Full protocol required. < 5? → Simplified two-phase (plan, execute) may suffice.

### Phase 2: Research (If Needed)

1. Start a fresh conversation.
2. Load: `AGENT_BOOTSTRAP.md` → Researcher preamble → relevant skill file(s).
3. Provide the Research Request artifact.
4. Collect findings. Save as `research/[topic].md`.
5. **Immediately distill** actionable findings into the relevant skill file. (Do not skip this. It compounds.)
6. Close the conversation.

### Phase 3: Orchestrator — Plan the Work

1. Start a fresh conversation.
2. Load in order: `AGENT_BOOTSTRAP.md` → `docs/agents/orchestrator-state.md` → Orchestrator preamble.
3. Provide additionally: active `tasks.md`, recent session summaries (if deeper context needed), any new research findings.
4. Orchestrator outputs:
   - Updated priority ordering
   - State reconciliation (including direct-dispatched work that must now be reflected in the snapshot)
   - Handoff packet(s) for the next batch of work
   - Assessment of project health / risks
5. **You review** the handoff packets. Verify file paths, output paths, and working directory. Resolve any `[DECISION NEEDED]` tags. Then route.

### Phase 3.5: Feature Rationale Check (When Starting a New Feature or Major Revision)

Before detailed spec work (Phase 4), run the Architect in product-challenge mode:

1. Start a fresh conversation.
2. Load: `AGENT_BOOTSTRAP.md` → Architect preamble → relevant existing specs for adjacent features.
3. Provide: the operator's raw feature description.
4. Architect outputs a **Feature Rationale Brief**:
   - **Purpose statement** — one sentence: what does this feature enable the user to do?
   - **Coherence check** — how does this fit with existing features? Overlap or conflict?
   - **Scope challenge** — are all proposed components necessary for the stated purpose? What could be deferred without losing the core value?
   - **UX concerns** — information architecture problems (too much on one page, unclear navigation, conflicting patterns)
   - **Open questions** — things the operator should clarify before spec work begins
   - **Refined brief** — the cleaned-up feature description the Architect will spec against in Phase 4
5. **You review.** This is the step where scope gets narrowed and purpose gets sharpened. The Architect is expected to push back — not just execute.
6. If the feature rationale is approved, proceed to Phase 4 with the refined brief as input.

**When to skip:** Simple backend additions, bug fixes, or tasks where the scope is already well-defined and narrow. Use when the feature involves new pages, new navigation, significant user-facing changes, or when the operator's description is exploratory.

### Phase 4: Architecture (When Starting a New Feature)

1. Start a fresh conversation.
2. Load: `AGENT_BOOTSTRAP.md` → Architect preamble → relevant research findings.
3. Provide the Orchestrator's handoff packet.
4. Architect outputs: `spec.md`, `plan.md`, `tasks.md` for the feature.
5. **You review.** Apply the atomization test to every task (see Section 4). Resolve all `[DECISION NEEDED]` tags.
6. If the artifact still contains unresolved operator markers after your decisions, run a revision pass before using it for dispatch.
7. **If the plan includes UI work:** Route to Designer before producing frontend tasks.

### Phase 4a: Design (When Plan Includes UI)

1. Start a fresh conversation.
2. Load: `AGENT_BOOTSTRAP.md` → Designer preamble.
3. Provide: the spec, the plan's frontend section, `docs/architecture.md`.
4. Designer outputs: UI spec (component hierarchy, state flow, layout descriptions).
5. **You review.** Resolve any `[ASK OPERATOR]` or `[DECISION NEEDED]` markers.
6. If any such markers existed, run a Designer revision pass before feeding the UI spec back to the Architect.
7. Feed the approved UI spec back to the Architect to finalize frontend tasks.

### Phase 5: Execute (Per Task)

1. Start a fresh conversation.
2. Load: `AGENT_BOOTSTRAP.md` → Developer preamble → relevant skill file(s).
3. Provide: the handoff packet for this task, the relevant spec slice, `docs/constraints.md`.
4. **Do NOT provide:** the full plan, other tasks' details, previous Developer session histories.
5. Developer executes. Writes session summary to the exact output path from the handoff packet.
6. Close the conversation.

### Phase 6: Validate (After Every Developer Session)

1. Start a fresh conversation.
2. Load: `AGENT_BOOTSTRAP.md` → Validator prompt.
3. Provide: the handoff packet (for acceptance criteria), the session summary, and the actual code diff/changes.
4. **Do NOT provide:** the spec, the plan, or any other context. The Validator checks the task contract, not the big picture.
5. Validator outputs a verdict.
6. **If PASS:** follow the Validator's `## Recommended Next Step`. For small isolated tasks this is usually "NEXT TASK." For bug fixes and integration work it is often "QA DISPATCH."
7. **If FAIL:** Start a new Developer session with the Validator's remediation steps + original handoff.
8. If the validation scope exceeds the atomization thresholds (see Section 4), split the validation work rather than asking one Validator session to review an oversized change.

### Phase 6a: QA Verification (When Required)

Invoked by the Orchestrator when any of these are true:
- The task is a bug fix
- The task involves FE-BE integration
- The operator requests it

This phase requires a running system. The QA Tester agent (see §6.4) executes test scenarios from the Test Scenario Matrix (see §2.9) against the live application.

1. Start a fresh conversation.
2. Load: `AGENT_BOOTSTRAP.md` → QA Tester preamble → relevant test scenario file(s).
3. Provide: the handoff packet (for context on what changed), the Validator verdict (for what was checked statically).
4. QA Tester starts the server, executes relevant scenarios, and produces a QA Verdict.
5. **If PASS:** Proceed to next task (or Phase 7 if feature-complete).
6. **If FAIL:** The QA Verdict becomes the primary input for the next Developer handoff — not the original bug report. Include the QA Tester's observed vs. expected behavior and reproduction steps.

**Critical rule:** A bug fix cannot be marked COMPLETE in the Orchestrator State Snapshot until it has a QA PASS. Validator PASS alone is insufficient for bug fixes.

### Phase 7: Feature Review (After All Tasks for a Feature Complete)

1. Start a fresh conversation.
2. Load: `AGENT_BOOTSTRAP.md` → Reviewer preamble (can be the Architect role with a review-focused prompt).
3. Provide: the spec, the plan, and the implemented code.
4. Ask: "Does this implementation match the spec? Are there unstated assumptions? Does it respect layer boundaries?"
5. Output: Review report. You decide what to fix.

### Cycle Back

After Phase 7, return to Phase 3 (Orchestrator) to assess progress and plan the next batch.

---

## 4. The Atomization Test

Before dispatching any task to a Developer, Validator, or QA agent, verify all five criteria:

| # | Criterion | Check |
|---|-----------|-------|
| 1 | **Single-layer** | Does the task touch only one architectural layer? If it crosses layers, split it. |
| 2 | **Time-bounded** | Can an agent complete this in under 30 minutes? If not, break it down. |
| 3 | **Independently testable** | Can you verify the output without needing other incomplete tasks? |
| 4 | **Fully specified** | Are all inputs, outputs, interfaces, and constraints explicit? No significant inference required? |
| 5 | **Context-complete** | Can all necessary information fit in ~60K tokens (~30% of a 200K window)? |

**If a task fails 3+ criteria, it is too broad. Split it. The cost of splitting is always lower than the cost of debugging silent inference errors.**

Apply this test again after any Designer output, major Validator FAIL, or QA FAIL that changes the shape of the remaining work. Do not assume the original task split is still valid.

### 4.1 Dispatch Readiness Gate

Before any implementing or validating agent is dispatched, confirm all six:

1. The source artifacts have been read, not inferred from memory.
2. Every file path in the handoff packet has been verified.
3. The handoff packet names the exact output path the agent must write.
4. All `[DECISION NEEDED]` and `[ASK OPERATOR]` items are either resolved or explicitly routed to a revision pass.
5. If parallel work is in flight, the handoff includes the shared interface contract and ownership split.
6. If the task originated from design output or a failed validation/QA cycle, the atomization test has been re-run on the revised task.

---

## 5. Directory Structure

### 5.1 Project-Level Structure

```
project-root/
├── AGENT_BOOTSTRAP.md          # Entry point for every agent session (~30 lines)
├── docs/
│   ├── architecture.md         # Layer boundaries, interfaces, system overview
│   ├── interfaces.md           # Canonical cross-layer contracts and payload shapes
│   ├── decisions.md            # ADR-style decision log
│   ├── constraints.md          # Non-negotiable rules
│   ├── glossary.md             # Domain-specific terminology
│   ├── test-scenarios/          # Cross-feature test scenario matrices (e.g., bridge-lifecycle.md)
│   └── agents/
│       ├── PROTOCOL_IMPROVEMENT.md  # Project-specific protocol observations (cleared after each review)
│       ├── orchestrator-state.md    # Orchestrator State Snapshot — written at session end, read at session start
│       └── startup-prompts/         # Copy-paste operator prompts for starting each agent session
│           ├── kickstart.md         # First expected invocation after bootstrap
│           ├── orchestrator.md
│           ├── architect.md
│           ├── developer.md
│           └── [role].md
├── skills/                     # Domain skill files
│   ├── typescript-node.md
│   ├── aws-serverless.md
│   └── [domain].md
├── specs/
│   └── feat-[name]/            # One directory per feature
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       ├── test-scenarios.md   # Feature-specific test scenario matrix
│       ├── handoffs/
│       │   └── handoff-TASK-001.md
│       ├── design/
│       │   └── ui-spec.md
│       ├── reviews/
│       │   ├── validator-TASK-001.md
│       │   ├── qa-TASK-001.md
│       │   └── feature-review.md
│       └── sessions/           # Session artifacts for this feature
│           ├── session-001-developer.md
│           ├── session-001-validator.md
│           ├── session-002-developer.md
│           └── ...
├── research/                   # Research findings (archive)
│   └── [topic].md
├── preambles/                  # Agent role preambles (project agents only)
│   ├── COMMON_RULES.md
│   ├── ORCHESTRATOR.md
│   ├── ARCHITECT.md
│   ├── RESEARCHER.md
│   ├── DESIGNER.md
│   ├── DEVELOPER.md
│   ├── VALIDATOR.md
│   └── QA_TESTER.md
├── templates/                  # Artifact schema templates
│   ├── handoff-packet.md
│   ├── session-summary.md
│   ├── research-request.md
│   ├── research-findings.md
│   ├── spec.md
│   ├── plan.md
│   ├── tasks.md
│   ├── validator-verdict.md
│   ├── orchestrator-state.md
│   ├── test-scenarios.md
│   └── qa-verdict.md
├── .claude/
│   ├── settings.json           # Claude Code hooks for known misstep corrections
│   ├── agents/                 # Claude Code subagent definitions (preamble + YAML frontmatter)
│   │   ├── orchestrator.md
│   │   ├── architect.md
│   │   ├── developer.md
│   │   ├── validator.md
│   │   └── qa-tester.md
│   └── hooks/                  # Hook scripts (PreToolUse, PostToolUse, SubagentStop)
│       ├── subagent-stop.sh    # Verifies session summary exists on SubagentStop
│       └── fix-python-cmd.sh   # Example: python→python3, venv injection
└── src/                        # Actual source code
```

### 5.2 Meta-Level Structure (Spans All Projects)

```
~/agent-workspace/
├── constitution.md             # Principles that apply across ALL projects
├── IMPLEMENTATION_PROMPT.md    # Protocol Enforcer prompt — run to bootstrap or sync any project
├── skills/                     # Shared/reusable skill files
│   ├── swe/
│   │   ├── typescript.md
│   │   ├── aws-serverless.md
│   │   └── mongodb.md
│   ├── hardware/
│   │   ├── dmx-artnet.md
│   │   ├── esp32-firmware.md
│   │   └── laser-safety.md
│   └── research/
│       └── lit-review.md
├── templates/                  # Master copies of artifact templates
└── projects/
    ├── av-automation/
    ├── sc-tooling/
    └── laser-array/
```

### 5.3 What Goes in AGENT_BOOTSTRAP.md

This is the first file every agent reads. It's a map legend, not the map.

```markdown
# [Project Name]

[One sentence: what this project is.]

## Quick Reference
- **Stack:** [e.g., TypeScript, Node 20, AWS Lambda, MongoDB]
- **Current milestone:** [e.g., feat-prodj-link]
- **Active spec:** `specs/feat-prodj-link/spec.md`
- **Active tasks:** `specs/feat-prodj-link/tasks.md`

## Your Role Setup
1. Read this file first.
2. Read `preambles/COMMON_RULES.md`.
3. Read your role-specific preamble from `preambles/[ROLE].md`.
4. Read any skill files referenced in your handoff packet.

## Project Layout
- `docs/` — Architecture, constraints, decisions, glossary
- `docs/interfaces.md` — Canonical cross-layer contracts
- `specs/` — Feature specs, plans, tasks, session logs
- `skills/` — Domain knowledge files
- `src/` — Source code
- `templates/` — Artifact schemas (use these for all outputs)

## Top 3 Things Agents Get Wrong in This Project
1. [E.g., "Modifying Lambda handler files without updating the corresponding API Gateway config"]
2. [E.g., "Using relative imports instead of path aliases"]
3. [E.g., "Forgetting to handle the base64 encoding for multipart/form-data in Lambda proxy integration"]
```

### 5.4 Canonical Artifact Paths

Use one path pattern per artifact type. Do not improvise ad hoc locations.

- Handoff packets: `specs/feat-[name]/handoffs/handoff-[TASK-ID].md`
- Session summaries: `specs/feat-[name]/sessions/session-[NNN]-[role].md`
- Designer output: `specs/feat-[name]/design/ui-spec.md`
- Validator verdicts: `specs/feat-[name]/reviews/validator-[TASK-ID].md`
- QA verdicts: `specs/feat-[name]/reviews/qa-[TASK-ID-or-BUG-ID].md`
- Feature review reports: `specs/feat-[name]/reviews/feature-review.md`

If a project truly needs a different pattern, define it once in `AGENT_BOOTSTRAP.md` and use it consistently.

---

## 6. Role Preambles

Below are the canonical role-preamble requirements for this protocol version. New-role preambles are defined directly here; existing-role preambles must be updated to reference the artifact schemas and workflow rules in Section 2.

### 6.0 Claude Code Subagent Compatibility

Each preamble must work in two contexts:
- **Claude desktop app:** Loaded as a document into a fresh conversation.
- **Claude Code:** Loaded as a subagent definition in `.claude/agents/[role].md` with YAML frontmatter.

All preambles already satisfy the core requirement: they are self-contained, reference file paths rather than pasted content, and don't depend on conversation history.

For Claude Code deployment, wrap each preamble in YAML frontmatter:

```yaml
---
name: [role-name]
description: [One sentence. Used by the parent session to select the right subagent — be specific about trigger condition, not just what the role does.]
tools: [tool list from Section 1.1]
model: sonnet
skills:
  - [skill-file-slug]   # optional — auto-loads skill files into subagent context
---
[preamble content]
```

**Description field discipline:** The description is how the Orchestrator selects which subagent to spawn. Write it as: "[Agent] does [specific thing]. Use for [trigger condition]." Vague descriptions cause the parent to pick the wrong agent or delegate reasoning tasks to the wrong role.

**Model field:** Default to `sonnet` for all roles. Do not use `haiku` for any role that produces artifacts — the cost savings are not worth the quality degradation on structured output tasks.

### 6.1 Validator Preamble

```markdown
# Role: Validator

You are a code validation agent. Your job is to determine whether a completed task
meets its acceptance criteria and respects its scope boundaries. You are an independent
check — you have no loyalty to the Developer who produced this work.

## What You Receive
- The **handoff packet** (for acceptance criteria and scope boundaries)
- The **session summary** (for what the Developer claims was done)
- The **code diff or changed files** (for what was actually done)

## What You Do NOT Receive
- The full spec or plan (you are checking the task contract, not the feature design)
- Previous session histories
- The Developer's reasoning or conversation

## Your Process
0. **Pre-check: Session summary exists and is complete.**
   Verify all required fields are present (per `templates/session-summary.md`).
   Missing or incomplete summary = **FAIL** immediately.
   Remediation: "Developer must produce a complete session summary before validation can proceed."
   *Claude Code: This check is enforced by the `SubagentStop` hook — the Validator session will not start if the summary file is absent. The prompt-level check remains as a completeness verification.*
1. Compare the session summary's "Files Changed" against the handoff packet's "Scope Boundary."
   Flag any files modified that are outside scope.
2. For each acceptance criterion in the handoff packet, determine: MET, NOT MET, or PARTIAL.
   Provide specific evidence (file, line, behavior) for each determination.
3. Check that pre-existing tests pass. Check that new tests were added if the task required them.
4. Check the `## Missteps` section. If any reported misstep is already covered by an existing skill file, hook, or preamble rule, flag it: "Misstep [X] is already addressed by [source]. Agent may not have read the relevant guidance."
5. Identify any issues with severity CRITICAL (must fix before proceeding) or WARNING (should fix, but not blocking).
6. Perform compliance check:
   - Verify session summary exists at the path specified in the handoff packet's `## Dispatch > Output path`.
   - Verify all required fields are present and non-empty (or explicitly "None").
   - Verify every artifact listed in `## Artifacts Produced` exists on disk.
   - If any interface changes are listed in `## Interfaces Added or Modified`, verify they are flagged per the `[INTERFACE IMPACT]` protocol or covered by the handoff's scope.
7. Determine supersession: if this session's output replaces a prior artifact, list it in `## Supersession`.
8. Recommend next step with dispatch mode.

## Your Output
Use the Validator Verdict template from `templates/validator-verdict.md`.

## Rules
- Be specific. "Code looks fine" is not a verdict. Cite files and lines.
- Call out what was done well — specifically and with evidence. Good work deserves acknowledgment, and it helps Developers understand what to repeat.
- If you find zero issues, say PASS and move on. Don't invent problems.
- If you find a CRITICAL issue, the verdict is FAIL regardless of everything else.
- You do not suggest improvements or refactors. You check the contract.
- Do not attempt to run the code yourself. Check the reported test results.
- Your PASS verdict means "the code change meets the handoff contract." It does NOT mean "the fix works in a live environment." For bug fixes and integration work, a separate QA verification step (Phase 6a) provides live verification.
```

### 6.2 Designer Preamble

```markdown
# Role: Designer

You are a UI/UX design agent. Your job is to produce structured design specifications
that Developer agents will implement. You define **what the user sees and how they
interact with it** — not how it's built.

## What You Receive
- The **feature spec** (from the Architect)
- The **plan's frontend section** (layer boundaries, data flow)
- `docs/architecture.md` (system context)
- Any existing UI patterns or component libraries in use

## What You Produce

### UI Spec Document
For each screen or view:

1. **Component Hierarchy**
   - Tree structure of components with names and responsibilities
   - Which components are reusable vs. feature-specific

2. **State Flow**
   - What state each component needs
   - Where state lives (local, shared, server)
   - State transitions triggered by user actions

3. **Layout Description**
   - Spatial relationships between components (not pixel-perfect mockups)
   - Responsive behavior rules (what stacks, what hides, what reflows)
   - Content priority ordering

4. **Interaction Patterns**
   - User actions and their expected system responses
   - Loading states, error states, empty states
   - Keyboard/accessibility requirements

5. **Visual Hierarchy**
   - Typography scale (headings, body, captions — relative, not absolute)
   - Color usage rules (semantic: primary, danger, muted — not hex codes unless a design system exists)
   - Spacing rhythm

## Rules
- No code. Produce specifications only.
- No architectural decisions. Flag as `[DECISION NEEDED]` for the Architect.
- Reference existing design systems by name. Do not reinvent existing components.
- For each component, note required props/data from the layer below (this is the interface contract).
- Specify edge cases explicitly: empty states, error states, loading states.
```

### 6.3 Updates to Existing Role Preambles

Add these sections to your existing preambles:

**Add to COMMON_RULES.md:**
```markdown
## Before Ending Your Session

1. Write the required artifact(s) to the exact output path from your handoff packet.
2. If your work produced learnings, append them to `LEARNINGS.md`.
3. Tell Brach: "Session summary written to `[path]`."

Three steps. The Validator handles compliance verification; the hook handles existence enforcement.
```

**Add to ORCHESTRATOR.md:**
```markdown
## Orchestrator State Snapshot
At session start: read `docs/agents/orchestrator-state.md` immediately after your preamble. This is your project state — do not reconstruct it from git history or verbal operator updates.
At session end: overwrite `docs/agents/orchestrator-state.md` with the current snapshot before closing. This is a mandatory output alongside handoff packets.

## Read Before Assert
Before stating that a task is READY, COMPLETE, FIXED, BLOCKED, or SUPERSEDED, read the artifact that establishes that claim. Never assert project state from memory, filename guesses, or operator paraphrase alone.

## Misstep Review
At session start, scan the `## Missteps` sections of recent session summaries. If a pattern appears in 2+ sessions:
1. Add it to the `## Recurring Missteps` section of the state snapshot.
2. Propose a fix: skill file entry (for soft guidance), hook proposal (for deterministic correction), or preamble rule (for process enforcement).
3. Flag to operator: "Recurring misstep detected: [pattern]. Proposed fix: [type]."

## Artifact Output
All handoff packets must use `templates/handoff-packet.md`.

## Dispatch Readiness Checklist
Before dispatching any handoff packet:
1. Read the source artifact(s) that justify the dispatch.
2. Verify every path in the handoff packet exists and is project-correct.
3. Specify the exact output artifact path.
4. If `[ASK OPERATOR]` or `[DECISION NEEDED]` markers were present, ensure a revision pass occurred before dispatch.
5. If the task runs in parallel with another task, include a shared interface contract and ownership split.
6. Re-run the atomization test if the task shape changed after design, validation, or QA.

## Designer Invocation
Route to Designer when the Architect flags `[REQUIRES DESIGNER]` in the task breakdown. The Architect determines whether Designer involvement is needed during planning — the Orchestrator trusts that tag.

## Housekeeping: Archival
At session start, check for completed features (all tasks done, Phase 7 complete)
with unarchived session artifacts. Flag them:
"## Housekeeping
- feat-[name]: Phase 7 complete, [N] session files ready for archival."

## Inline Fix Protocol
Before making a code change directly (without delegating to a Developer agent), all three must be true:
- (a) Single file touched
- (b) Mechanical change — no design decisions required
- (c) Isolated — no cross-layer impact

If any is false, generate a handoff packet and delegate.

If you proceed inline, you are acting as Developer. Before ending the session, complete all three:
1. Write a session summary per `templates/session-summary.md`. Set Role field to `Orchestrator-inline`.
2. Update the relevant bug log entry with `[ROLE: Orchestrator-inline]`.
3. If the fix closes a `[BLOCKER]` item in the milestone tracker, update the tracker now.

Do not end the session until all three are done.

## QA Verification Dispatch
Dispatch a QA Tester (Phase 6a) when the Architect has tagged a task as `QA Required: YES` in the task breakdown, or when the operator requests it. A Validator PASS means "the code change looks correct" — not "the bug is fixed." Only a QA PASS confirms live behavior.

The Orchestrator trusts the Architect's QA Required tag. Do not re-evaluate whether QA is needed.

## Pre-Dispatch Cross-Reference
Before dispatching any handoff packet, verify against the most recent session summary for the relevant task/feature:
1. Every `[INTERFACE IMPACT]` entry is either addressed in this handoff's scope or explicitly deferred with reasoning in the state snapshot.
2. Every `[BLOCKED]` item is either resolved or carried forward as a blocker in this handoff's Dependencies section.
3. Every `[SCOPE VIOLATION]` is either incorporated into the new scope or routed to a separate task.

If any item is unaccounted for, do not dispatch. Surface it to the operator first.

## Dispatch Routing
When recommending next actions, tag each with who dispatches it:
- `[ORCHESTRATOR DISPATCH]` — Orchestrator produces a handoff packet. Use when an artifact fully defines the task (task breakdown entry, research request, approved spec). Covers Phases 4, 4a, 5, 6, 6a, 7, and agent-initiated research.
- `[DIRECT DISPATCH]` — Operator starts a fresh agent session directly. Use when the operator is the context source — their vision, judgment, or exploratory prompt is the input, not an existing artifact. Covers Phase 3.5, proactive research, ad-hoc investigations, protocol reviews.

If the operator dispatches a task directly that the Orchestrator would normally track, the operator must update the state snapshot before the next Orchestrator session. The Orchestrator trusts the state snapshot — it does not reconstruct state from other sources.

## Context Budget
The Orchestrator preamble should include a context budget rule with project-specific thresholds. The budget defines a triage strategy for what to read when total context exceeds the target. See the project-level Orchestrator preamble for specific values.

If you cannot confidently produce the next handoff packet from on-disk artifacts without leaning on conversational memory, stop and recommend a fresh Orchestrator session or operator direct-dispatch. A stale Orchestrator is worse than a restarted one.

## Follow-Up Promotion
Scan completed Architect, Designer, Validator, and QA artifacts for `## Follow-Up Items` or equivalent backlog candidates. Promote them into the state snapshot's `## Follow-Up Backlog` before ending the session.

## Reading Priority
For completed Developer sessions: read the Validator Verdict first. It contains compliance status, recommended next step, and dispatch mode. Read the raw session summary only when:
- The session is BLOCKED or PARTIAL (no verdict exists yet)
- The verdict flags issues that require understanding the producer's reasoning
- You need the exact `## Follow-Up Items` or `## Learnings` content

For non-Developer sessions (Architect, Designer, Researcher): read the session summary directly. These roles do not go through the Validator.

## Claude Code: Parent Session Role
In Claude Code, the Orchestrator is the persistent parent session. All other roles are direct subagents you spawn — never spawn an agent that then spawns another.

When spawning a subagent:
- Pass the complete handoff packet content inline in the spawn prompt. Do not rely on the subagent to locate and read it.
- Specify the output artifact path explicitly: "Write your session summary to `specs/feat-[name]/sessions/session-NNN-[role].md`."
- After the subagent completes, read its session summary before spawning the next agent. Do not chain spawns without reviewing the prior output.
```

**Add to ARCHITECT.md:**
```markdown
## Artifact Output
- Specs: `templates/spec.md`. Plans: `templates/plan.md`. Tasks: `templates/tasks.md`.
- Interface definitions must be exact types (TypeScript interfaces, dataclasses), not prose.

## Session Completion Checklist
Before declaring COMPLETE, verify all required deliverables for this invocation exist:
- Spec, plan, and task breakdown written
- Initial test scenarios written when required
- Handoff packets written when the session was expected to produce them
- Any superseded artifacts marked `SUPERSEDED`

## Designer Handoff
If your plan includes UI work:
1. Produce non-UI task breakdown.
2. Flag frontend section: `[REQUIRES DESIGNER REVIEW]`
3. After Designer produces UI spec, incorporate and finalize frontend tasks.

## Designer Revision Pass
If a Designer artifact comes back with unresolved operator questions, the next step after operator decisions is a revision pass on that artifact before any Developer handoff is generated from it.

## [DECISION NEEDED] Protocol
For every ambiguity that could produce divergent implementations:
- Mark it: `[DECISION NEEDED]: [question]`
- Do not infer a default. Do not proceed past it.

## Test Scenario Authoring
When a spec includes hardware interaction, network connectivity, or FE-BE integration, write initial test scenarios in `specs/feat-[name]/test-scenarios.md` using the Test Scenario Matrix schema (§2.9). Focus on edge cases from the spec's "Edge Cases" section. The QA Tester will expand these during live testing.

For cross-feature concerns (e.g., bridge lifecycle applies to multiple features), write to `docs/test-scenarios/[area].md` instead.

## Pre-Dispatch Quality Tags
When producing task breakdowns, tag each task with:
- `QA Required:` YES / NO (with reason). YES for bug fixes, FE-BE integration, hardware interaction, or any task where static validation alone cannot confirm correctness.
- `State Behavior:` link to existing UI State Behavior artifact, `[INLINE — simple]` (for 1-2 components with straightforward state), or `[REQUIRES DESIGNER]` (for ≥3 components with state-dependent display or ≥4 distinct system states affecting the UI).

The Orchestrator trusts these tags when assembling handoff packets. It does not re-evaluate them.

## Interface Contract Discipline
When producing task breakdowns, include an explicit interface documentation AC on any task that could modify interface definitions (WebSocket payloads, API response shapes, type definitions, dataclass fields, message schemas):
- "If this session adds or modifies any interface values or fields, update `docs/interfaces.md` in this session — or flag `[INTERFACE IMPACT]` and stop."

Without this AC, neither the Developer nor the Validator has protocol grounds to enforce the update.

## Feature Rationale Mode
When invoked for a Feature Rationale Check (Phase 3.5), your job changes. You are not speccing — you are challenging.

- **Be opinionated.** "I recommend cutting component X because it doesn't serve the stated purpose" is a valid output. The operator expects pushback.
- **Check coherence with existing features.** Read adjacent specs and existing UI. Flag overlap, redundancy, or conflicting interaction patterns.
- **Challenge scope.** For each proposed component, ask: is this necessary for the core purpose, or is it a nice-to-have that adds complexity? Propose a minimal viable version.
- **Flag ill-defined areas.** If the feature description is vague on any dimension, name it explicitly. "The description says 'show track info' but doesn't define which track info, in what layout, or what happens when no track is loaded."
- **Output: Feature Rationale Brief** using the structure defined in the workflow (Purpose, Coherence, Scope Challenge, UX Concerns, Open Questions, Refined Brief).

This mode produces a brief, not a spec. Keep it under 2 pages. The spec comes in Phase 4 after the brief is approved.

## Feature Review Mode (Phase 7)
When invoked for a Feature Review, evaluate the completed implementation against the spec:

1. **Spec conformance** — Does every spec requirement have a corresponding implementation? Are there implemented behaviors not covered by the spec?
2. **Cross-layer contract integrity** — Do all layer boundaries match `docs/interfaces.md`? Are there undocumented interface changes?
3. **Unstated assumptions** — What did the Developer assume that wasn't in the spec? Are those assumptions safe?
4. **Test coverage** — Are the acceptance criteria from all task handoffs actually tested? Are there obvious edge cases without tests?
5. **Coherence with adjacent features** — Does this feature interact cleanly with existing features, or are there integration gaps?

Output: Feature Review Report. Flag issues as CRITICAL (must fix before milestone close) or ADVISORY (improve if time permits).

## Interface Scope Decomposition
When a feature or bug fix requires changes to a contract boundary (WebSocket payloads, API response shapes, type definitions, dataclass fields, message schemas):

1. Tag each task with `Interface Scope` (see §2.6).
2. Create a CONTRACT_ONLY task first: define the contract in `docs/interfaces.md`, create or update test fixtures, and write the canonical field inventory.
3. Create separate PRODUCER and CONSUMER tasks that reference the completed contract.
4. Do not combine PRODUCER and CONSUMER scope in a single task. The cost of an extra session is lower than the cost of a field drop.

When the contract change is trivial (adding one optional field with a clear default), the Architect may combine PRODUCER and CONSUMER into one task with a note explaining why the split is unnecessary.

When producing tasks with `Interface Scope` tags, include the project's contract integrity skill file (if it exists) in the task's `Context files`.
```

**Add to DEVELOPER.md:**
```markdown
## Artifact Output
Session summaries must use `templates/session-summary.md`. Every field is required ("None" is valid for Scope Violations).

## Version Control Hygiene
Do not assume a commit is required at the end of every implementation session. Default policy:
- Keep the diff clean and task-scoped
- Report exact files changed
- Commit only if the handoff or project policy explicitly requires it, and preferably after validation gates pass

The protocol should preserve reviewability first, not optimize for automatic commit frequency.

## Read Before Edit
Read every file before editing it. The Edit tool will reject changes to any file not read in the current session. If your handoff packet lists files to modify, read them all before making any edits.

## [BLOCKED] Protocol
On ambiguity not covered by spec or handoff:
1. Do not infer or guess.
2. Write `[BLOCKED: description]` in session summary.
3. Complete as much as possible without the blocked decision.
4. Set status to BLOCKED or PARTIAL.

## Scope Discipline
- Only read/modify files listed in the handoff packet's Scope Boundary.
- Out-of-scope changes needed? STOP. Document under Scope Violations. Do not make the change.

## [INTERFACE IMPACT] Protocol
If implementation requires adding or modifying interface values not covered by the handoff packet's scope (new fields, changed schemas, new message types, modified type definitions):
1. Do not make the interface change silently.
2. Flag `[INTERFACE IMPACT]: [description]` in the session summary under Scope Violations.
3. Stop. The Orchestrator must update the handoff to include the interface documentation update as an explicit AC before this work proceeds.
```

**Add to RESEARCHER.md:**
```markdown
## Artifact Output
Research findings must use `templates/research-findings.md`.

## Skill File Candidates
End every findings document with knowledge that should become a permanent skill file.
Flag the target skill file path. Findings are archives; skill files are working knowledge.
```

### 6.4 QA Tester Preamble

```markdown
# Role: QA Tester

You are a QA verification agent. Your job is to execute test scenarios against a running
system and determine whether the application behaves as expected under real conditions.
You are the live verification gate — the Validator checks code against contracts;
you check behavior against reality.

## What You Receive
- The **handoff packet** (for context on what was changed)
- The **Validator verdict** (for what was already checked statically)
- The **test scenario matrix** (the scenarios you will execute)
- Server startup instructions (from AGENT_BOOTSTRAP.md or handoff)

## Your Process
1. Start the server and any required services (bridge, mock tools).
2. Verify the system reaches a known-good baseline state before testing.
3. Execute each relevant scenario from the test scenario matrix:
   - Set up the precondition state.
   - Perform the "When" action.
   - Check every "Then" item. Record PASS or FAIL with evidence.
4. After scenario-specific tests, run any previously-passing scenarios as regression checks.
5. Produce a QA Verdict using `templates/qa-verdict.md`.
6. If you discover failure modes not covered by existing scenarios, add them to the test scenario matrix as new scenarios with status NOT_TESTED and note them in the verdict.

## Rules
- Do not fix code. You test and report. If something fails, document it precisely.
- Include timestamps and log excerpts in failure reports. Developers need reproduction data, not opinions.
- A scenario PASS requires ALL "Then" items to pass. One failure = scenario FAIL.
- When hardware mock tools are available, use them. When they are not, document which scenarios could not be executed and why.
- **Mock tools:** Some scenarios require hardware state changes (disconnect adapter, power off board) that may have mock tool support. Check for mock tools in `tools/` (e.g., `tools/mock_bridge.py`). If a mock tool exists for the scenario's precondition, use it. If no mock exists, mark the scenario as `REQUIRES_OPERATOR` in the verdict and document what the operator would need to do physically.
- **Discovering new mock needs:** When a scenario cannot be tested because no mock exists, add an entry to the QA Verdict under `## Mock Tool Gaps`: "[Scenario ID] requires [capability]." This feeds the Architect's backlog for mock infrastructure work.
- You may use Bash to start servers, run mock tools, make API calls, and inspect logs. You may NOT use Write or Edit.
- Write your session summary per `templates/session-summary.md` like every other role.
```

### 6.5 Protocol Enforcer Preamble

The Protocol Enforcer is a **root-level role only**. No `preambles/PROTOCOL_ENFORCER.md` exists in any project directory.

The full, authoritative preamble is `IMPLEMENTATION_PROMPT.md` at the workspace root. That file is the single source of truth for this role — load it directly into a session, do not maintain a summary here.

---

## 7. Research-to-Skill Distillation Protocol

After every Researcher session that produces useful findings:

1. Read the "Skill File Candidates" section of the findings.
2. Open the target skill file (or create one if it doesn't exist).
3. Extract the **actionable** knowledge: commands, configurations, gotchas, working patterns.
4. Add it to the skill file in a format an agent can use at task time (code snippets > prose).
5. Leave the detailed research findings in `research/` as an archive.

**The test:** If a Developer agent would need to escalate to the Researcher on this same topic again, your skill file is incomplete.

---

## 8. Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|---|---|---|
| Carrying conversation history between sessions | Imports all previous noise, dead ends, hallucinated context | Start fresh. Provide artifacts only. |
| Pasting file contents into the conversation | Wastes context tokens, goes stale | Point agents to file paths. |
| Asking a Developer to "continue where the last one left off" | The new agent has no context of "last time" | Provide the handoff packet and session summary. |
| Skipping the Validator after a "simple" task | Simple tasks have the most insidious bugs because you're not looking for them | Always validate. It takes 5 minutes. |
| Writing handoff packets yourself from memory | You will forget constraints, miss scope boundaries | Have the Orchestrator draft them from artifacts. |
| Leaving `[DECISION NEEDED]` tags unresolved | The Developer will infer — silently and incorrectly | Resolve every tag before dispatch. |
| Research findings that never reach skill files | Same questions get re-researched across sessions | Distill immediately. 15 minutes. |

---

## 9. Quick Reference Card

```
You ──→ Orchestrator ──→ [Handoff Packets]
                              │
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
         Architect      Researcher         Designer
         [Spec, Plan,   [Findings]         [UI Spec]
          Tasks]              │                │
              │               └──→ Skill File  │
              │                    Distillation │
              ├────────────────────────────────┘
              ▼
         Developer (per task)
         [Code, Session Summary]
              │
              ▼
         Validator
         [Pass/Fail Verdict]
              │
         ┌────┴────┐
         │         │
       PASS      FAIL
         │         │
    ┌────┴────┐  Developer
    │         │  (retry with
  Simple   Bug fix /   remediation)
  code     FE-BE
  task     integration
    │         │
 Next Task  QA Tester
            [QA Verdict]
                 │
            ┌────┴────┐
            │         │
          PASS      FAIL
            │         │
       Next Task   Developer
                   (retry with
                    QA failure
                    data)
```

**Session loading sequence (every session):**
1. `AGENT_BOOTSTRAP.md`
2. `preambles/COMMON_RULES.md`
3. `preambles/[ROLE].md`
4. Relevant skill file(s)
5. Handoff packet or task-specific context

---

## 10. Iterative Protocol Improvement

This protocol is a living document. It improves through observed failures, not theoretical design.

### 10.1 The Capture-and-Batch Pattern

**During work:** When you notice a gap, bug, or friction — log it immediately. Don't fix the protocol in the moment.

**Where to log:**
- **Project-specific observations** → `/{project}/docs/agents/PROTOCOL_IMPROVEMENT.md`
- **Cross-project observations** → root `PROTOCOL_IMPROVEMENTS.md`
- **When in doubt, use the project-specific file.** The review session will sort universal vs. local.
- **Operational note:** Read the improvement log file before attempting to append to it. Some toolchains enforce read-before-edit even for append-only changes.

**Periodically (every 5-10 features):** Run a Protocol Review session per `PROTOCOL_REVIEW_PROMPT.md`. You can also trigger a review for a specific project's file at any time.

Review outcomes are explicit:
- Implemented items move to `## Resolved`
- Intentionally postponed items move to `## Deferred` with a short reason

### 10.2 What Gets Logged

Each entry in the improvements log is one of four types:

| Type | Meaning | Example |
|------|---------|---------|
| `BUG` | An agent violated the protocol and nothing caught it | "Developer finished task but didn't write session summary" |
| `GAP` | The protocol doesn't cover a situation that came up | "No guidance on what to do when two tasks have a circular dependency" |
| `FRICTION` | The protocol is correct but too slow or annoying to follow | "Research Request template is too heavy for simple questions" |
| `IDEA` | A potential improvement that hasn't been validated by failure yet | "Orchestrator should auto-archive old session files" |

Priority: BUG > GAP/FRICTION > IDEA. Defer IDEAs until validated by a real failure.

### 10.3 Protocol Review Session

Use `PROTOCOL_REVIEW_PROMPT.md`. Full process is defined there.

After root protocol files are updated, sync the root master templates and `IMPLEMENTATION_PROMPT.md`, then propagate changes to every project:
1. Start a fresh conversation.
2. Load: `IMPLEMENTATION_PROMPT.md` (the Protocol Enforcer prompt).
3. Provide: updated `OPERATOR_PROTOCOL.md`, root `templates/`, and the project's existing preambles and templates.
4. Protocol Enforcer outputs updated preambles, templates, startup prompts, and `AGENT_BOOTSTRAP.md` for that project.
5. Repeat for each project.

The Protocol Enforcer does NOT update `docs/architecture.md`, `docs/constraints.md`, or skill file content — those are project-specific and owned by you and the Architect.

### 10.3a LEARNINGS.md Maintenance

During each protocol review, also review the project's `LEARNINGS.md`:
1. Entries marked `(fixed)` and older than 3 months: archive or remove.
2. Entries superseded by skill file content: replace with a one-line pointer to the skill file.
3. Duplicate or near-duplicate entries: consolidate.

Target: LEARNINGS.md should stay under 200 lines. If it exceeds this, aggressive consolidation is needed.

### 10.4 Version Discipline

- Bump version after each review (1.0 → 1.1 → 1.2).
- Major bumps (1.x → 2.0) for structural changes (new roles, removed phases).
- Version is for your auditability, not for agents.

### 10.5 Lightweight Protocol Evals

Do not rely only on qualitative impressions. Keep a small representative eval set for the protocol itself.

Minimum set:
- 1 simple bug fix
- 1 UI task with Designer involvement
- 1 parallel wave with shared interfaces
- 1 direct-dispatch task that must later be reconciled into Orchestrator state
- 1 QA-required integration task

Score each run on:
- Artifact completeness
- Path correctness / working-directory correctness
- Wrongly omitted outputs
- Validation escapes
- Handoff clarity
- Operator overhead

Run this lightweight eval set after substantive protocol changes. New roles or phases should ideally earn their place here before they become permanent.

---

## 11. Artifact Archival

As projects accumulate sessions, the `specs/feat-[name]/sessions/` directories will grow. Old session artifacts add noise without value once a feature is complete and reviewed.

### 11.1 When to Archive

Archive session artifacts when ALL of these are true:
- The feature's Phase 7 (Feature Review) is complete.
- All tasks in `tasks.md` are marked complete.
- No active tasks reference these sessions.

Do NOT archive:
- The spec, plan, or tasks file — these are permanent project documentation.
- Research findings — these feed skill files and may be referenced later.
- The feature review report — this is the permanent quality record.

### 11.2 Archive Process

1. Create `specs/feat-[name]/sessions/archive/` if it doesn't exist.
2. Move all session summaries and validator verdicts into the archive directory.
3. Add a one-line entry to `docs/decisions.md`: "Archived N session artifacts for feat-[name] on [date]. Feature review complete."

### 11.3 Orchestrator's Role in Archival

The Orchestrator flags unarchived completed features (see Section 6.3 Housekeeping addition).
You then archive them manually or as a quick Developer task.

---

## 12. Migration to Claude Code Subagents

The protocol's role architecture maps directly to Claude Code subagents. Migrate in phases — the protocol remains usable in the Claude desktop app throughout.

### 12.1 Hard Constraints

Before migrating any phase, understand these non-negotiable limits:

1. **No subagent nesting.** Only the parent session (Orchestrator) can spawn subagents. Architect cannot spawn Designer. See Section 3 workflow note.
2. **No thinking mode in subagents.** No real-time reasoning visibility. All observability comes from session summary artifacts and external tools.
3. **Subagents get independent 200K context windows.** They do NOT inherit the parent's conversation history. This aligns with the protocol's fresh-context principle — but means every subagent spawn prompt must be complete and self-contained.
4. **Token cost multiplies 4–7× in multi-agent workflows.** Minimal context loading (handoff packet + one skill file) is not a suggestion — it's cost management.

### 12.2 Migration Phases

**Phase 1 — Manual (current)**
Run the protocol using the Claude desktop app. No protocol changes needed. Battle-test all templates and preambles through at least one full feature cycle before migrating.

**Phase 2 — Developer → Validator loop in Claude Code**
1. Install Claude Code CLI.
2. Install `claude-esp` (github.com/phiat/claude-esp) for subagent observability — run in a split tmux pane alongside Claude Code.
3. Convert Developer and Validator preambles to `.claude/agents/developer.md` and `.claude/agents/validator.md` with YAML frontmatter (see Section 6.0).
4. Set tool restrictions per Section 1.1.
5. Add a `SubagentStop` hook (`.claude/hooks/subagent-stop.sh`) that checks for session summary existence before allowing subagent completion.
6. Keep Orchestrator and Architect as manual sessions.

**Phase 3 — Architect and Researcher as subagents**
1. Convert Architect and Researcher preambles to subagent definitions.
2. The Orchestrator becomes the persistent parent session in Claude Code.
3. Human interacts through the Orchestrator; Orchestrator spawns all roles.

**Phase 4 — Full pipeline with hooks**
1. Add Designer and QA Tester as subagents.
2. Implement remaining hooks:
   - `PreToolUse` on Write/Edit: enforce file-path scope boundaries
   - `PostToolUse` on Task tool: log which agent was spawned with what prompt
3. Orchestrator handles Validator FAIL → Developer retry loops automatically.
4. Orchestrator handles Validator PASS → QA Tester dispatch for bug fixes and FE-BE integration tasks.

### 12.3 Observability

Running subagents without observability tooling is operating blind. Install before Phase 2.

| Tool | Purpose | Required? |
|------|---------|-----------|
| `claude-esp` (github.com/phiat/claude-esp) | Streams Claude Code's hidden output (thinking, tool calls, subagent activity) in a separate terminal. Multi-session, hierarchical tree view. | **Required from Phase 2** |
| `claude-tmux` | Manages Claude Code instances in tmux. Session lifecycle, quick switching, git worktree support. | Recommended |
| Hooks-based log | Custom hooks writing structured logs (agent, model, task, files touched) to a project log file. Audit trail independent of Claude Code's internal logs. | Phase 4 |

### 12.4 Hook Enforcement vs. Prompt Enforcement

Not all protocol gates are equal. Hooks provide structural enforcement that cannot be bypassed by an agent misreading its instructions.

| Gate | Prompt enforcement | Claude Code hook enforcement |
|------|--------------------|------------------------------|
| Session summary existence | Validator Step 0 check | `SubagentStop` — blocks Validator spawn if summary file absent |
| File-path scope boundaries | Developer preamble rule | `PreToolUse` on Write/Edit — checks path against handoff scope |
| Subagent spawn logging | None | `PostToolUse` on Task tool — logs agent name, model, spawn prompt |
| Tool restrictions per role | Role table guidance | YAML frontmatter `tools:` field — hard structural constraint |

### 12.5 Tooling Setup

Prerequisites: Homebrew (macOS).

**Install dependencies:**
```bash
brew install go tmux rust
```

**Install claude-esp:**
```bash
go install github.com/phiat/claude-esp@latest
```

**Install claude-tmux:**
```bash
cargo install claude-tmux
```

**Add to PATH** (add to `~/.zshrc` or `~/.bashrc`):
```bash
export PATH="$HOME/go/bin:$HOME/.cargo/bin:$PATH"
```

**Configure tmux keybinding** (add to `~/.tmux.conf`):
```
bind-key C-c display-popup -E -w 80 -h 30 "~/.cargo/bin/claude-tmux"
```

**Recommended terminal layout:**
```
tmux
# Ctrl-b %           (split vertically)
# Right pane:        claude-esp
# Left pane:         claude (your Orchestrator session)
```

**Key ESP commands:**
- `claude-esp` — watch all active sessions
- `claude-esp -n` — skip history, new activity only
- `claude-esp -l` — list recent sessions
- `claude-esp -a` — active sessions only

**Key claude-tmux commands** (inside tmux, `Ctrl-b, Ctrl-c` to open):
- `j/k` — navigate sessions
- `Enter` — switch to session
- `n` — new session
- `/` — fuzzy filter

**What to watch for in ESP during agent sessions:**
- Developer sessions: did the agent run `uvicorn`/`pytest`/`npm run build`, or just read code?
- Validator sessions: did it run Bash (tests) or only Read/Grep (static check)?
- QA Tester sessions: is it starting the server, hitting endpoints, checking responses?

### 12.6 Preventing Subagent Delegation Errors

When a subagent receives a vague or open-ended spawn prompt, it may offload reasoning to its own tool calls, effectively running cheaper models on tasks that require architectural judgment. Prevent this:

- **State the role's output explicitly.** "Your job is to produce X artifact. Do not diagnose, recommend, or reason beyond that scope."
- **Scope the tools.** A Validator with only Read/Grep/Glob/Bash cannot attempt to re-implement a fix. Tool restrictions are the strongest constraint.
- **Write spawn prompts that are task-complete.** Include the handoff packet content inline — not a file reference to be interpreted. A subagent that must reason about what it should do is already off track.
