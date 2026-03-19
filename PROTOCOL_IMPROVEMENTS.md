# Protocol Improvements Log

> **How to use:** When you notice something during a session — an agent forgot a step,
> a template is missing a field, a workflow has a gap — add a one-liner here.
> Don't fix the protocol in the moment. Just capture the observation.
> Periodically, run a Protocol Review session to batch-process these into protocol changes.

---

## Pending

<!-- Format: [TYPE] Description. (Optional: which role/artifact is affected) -->
<!-- Types: BUG | GAP | FRICTION | IDEA -->
<!-- BUG = agent violated protocol and nothing caught it -->
<!-- GAP = protocol doesn't cover this situation -->
<!-- FRICTION = protocol is correct but too slow/annoying -->
<!-- IDEA = potential improvement, not yet validated by failure -->

- [GAP] No structured event log for pipeline activity. Pipeline state must be reconstructed from file timestamps, orchestrator-state.md, and session summaries scattered across `specs/` subdirectories. An Orchestrator starting a new session has no single source to answer "what happened since my last session?" without globbing and reading multiple files. A single append-only `docs/agents/events.jsonl` per project (one JSON line per dispatch, completion, verdict, decision) would give both human operators and Orchestrator sessions a reliable, chronological audit trail. (affects: Orchestrator state reconstruction, all roles at session boundaries)

- [BUG] Root master templates `research-findings.md`, `spec.md`, `plan.md`, `test-scenarios.md`, and `qa-verdict.md` use blockquote metadata (`> Status: ...`) instead of YAML frontmatter. Protocol §2.0 explicitly states: "Do not use blockquote metadata — use frontmatter exclusively." Fixed in the Tinyshop project copy; root masters still need updating. (affects: templates/, all roles that produce these artifacts)

- [FRICTION] Agent dispatch requires the operator to find the right startup prompt, copy-paste it, and manually verify the correct files are loaded in the correct order. The startup prompts in `docs/agents/startup-prompts/` contain this information in prose, but the operator must read and interpret them each time. A machine-readable invocation manifest per role (YAML: files to load, load order, first instruction, required artifacts, tool restrictions) would sit alongside the prose prompt and make dispatch verifiable and automatable by any tooling — hooks, scripts, or future UIs. (affects: startup prompts, Protocol Enforcer deliverables, operator workflow)

## Deferred

<!-- Format: [reviewed vX.Y] [TYPE] Description → Why deferred -->

- [reviewed v1.7] [IDEA] User Advocate role: a dedicated end-user-perspective evaluator distinct from Validator or Feature Review. (from: DjTools/scue) → Deferred. This may deserve a role eventually, but v1.7 adds an explicit brake on role proliferation. Validate first as an optional review mode or eval track before promoting it to a permanent role.

- [reviewed v1.7] [FRICTION] Guided question scripts for session consistency. (from: DjTools/scue) → Deferred. Useful, but not yet backed by enough cross-project evidence to justify new shared templates at the root level.

- [reviewed v1.7] [GAP] No git commit step in Developer end-of-session checklist. (from: DjTools/scue 1.6.1) → Deferred. v1.7 intentionally chose reviewable task-scoped diffs over a root-mandated commit policy. Commit rules should stay project-specific unless repeated failures show a universal need.

- [reviewed v1.7] [GAP/FRICTION] QA Tester missing Zustand injection guidance, WebSocket interference guidance, QA brief fixture shapes, `preview_inspect` staleness notes, `preview_eval` IIFE guidance, and QA brief environment requirements. (from: DjTools/scue 1.6.1) → Deferred. These are high-value, but they are tightly coupled to a specific frontend stack and QA toolchain. They belong in project QA docs first, then can be promoted if they recur elsewhere.

- [reviewed v1.7] [IDEA] Spec format should include a DOM-queryable QA checklist. (from: DjTools/scue 1.6.1) → Deferred. Promising, but it introduces a new spec artifact contract. Needs more evidence across projects before being made mandatory.

- [reviewed v1.7] [IDEA] Structured entry IDs for protocol improvement records. (from: DjTools/scue 1.6.1) → Deferred. The entry volume is not yet high enough to justify the overhead.

- [reviewed v1.7] [IDEA] `[SKIP CONFIRM GATE]` operator signal. (from: DjTools/scue 1.6.1) → Deferred. This reduces friction, but it weakens a safety rail and should be tested project-locally before entering the root protocol.

---

## Resolved

<!-- Format: [vX.Y] [TYPE] [description] → [what changed] -->

- [v1.8] [GAP] Artifact metadata header uses blockquote format, not machine-parseable. (§2.0, all templates) → Switched all artifact metadata to YAML frontmatter (`---\nstatus: DRAFT\n---`). Updated §2.0 with two-tier metadata (full 5-field for planning artifacts, slim 2-field for session summaries/verdicts). Updated all root templates. Added frontmatter-only rule to §2.0.

- [v1.8] [BUG/GAP] Session summary overloaded with compliance metadata (routing, self-assessment, exit checklist, supersession tracking) that producing agents routinely skip. (§2.2, §6.1, §6.3, templates) → Split session summary responsibilities into three layers: producer owns factual recap (slimmed to 12 fields), Validator owns compliance interpretation (new §§ Compliance Check, Supersession, expanded Recommended Next Step with dispatch mode), hook owns existence gate. Simplified universal exit sequence to 3 steps. Added Orchestrator reading priority (verdict first, summary second for Developer sessions).

- [v1.8] [BUG] Data fields silently dropped when a single Developer session modifies both producer and consumer sides of a contract boundary. (§2.6, §6.3) → Added Interface Scope task tag (CONTRACT_ONLY | PRODUCER | CONSUMER | END_TO_END | NONE) to task breakdown schema. Added Interface Scope Decomposition rules to Architect preamble: contract-touching work must be split into CONTRACT_ONLY → PRODUCER/CONSUMER tasks. Added §2.11 Field Inventory schema for contract documentation. Added contract integrity skill file guidance to IMPLEMENTATION_PROMPT.md.

- [v1.7] [IDEA] Orchestrator context budget self-assessment for dispatch routing. (from: DjTools/scue session 9) → Added explicit Orchestrator self-assessment language: if it cannot confidently produce the next handoff from on-disk artifacts without leaning on conversational memory, it must recommend a fresh Orchestrator session or operator direct-dispatch.

- [v1.7] [GAP] No protocol for Designer revision passes, and no atomization check for Designer-output-driven tasks. (from: DjTools/scue session 9) → Added revision-pass gates after operator decisions on Architect and Designer artifacts, plus a re-run of the atomization test after design output or failed validation/QA materially changes the remaining work.

- [v1.7] [FRICTION/IDEA] Architect session artifacts were easy to omit, and follow-up items were not promoted into tracked backlog. (from: DjTools/scue session 9) → Added an Architect session completion checklist, `## Follow-Up Items` to the session summary schema, Orchestrator follow-up promotion rules, and `## Follow-Up Backlog` in the state snapshot.

- [v1.7] [BUG/GAP] Developer skipped session summary, Architect skipped required artifacts, and there was no mandatory agent exit protocol. (from: DjTools/scue 1.6.1) → Added a universal exit sequence to `COMMON_RULES.md`, expanded the Session Summary schema with routing, exit checklist, follow-up items, and self-assessment, and required role-specific completion checklists where needed.

- [v1.7] [BUG] Orchestrator asserted work state without reading session artifacts first. (from: DjTools/scue 1.6.1) → Added a strict Read-Before-Assert rule to the Orchestrator preamble and reinforced dispatch/readiness gates around artifact-backed state claims.

- [v1.7] [BUG/GAP] Superseded artifacts were not marked, and artifact status had to be inferred. (from: DjTools/scue 1.6.1) → Added required durable-artifact metadata (`Status`, `Revision Of`, `Supersedes`, `Superseded By`) and explicit supersession rules across the protocol and master templates.

- [v1.7] [GAP/BUG] Handoff packets were missing `project_root`, parallel interface contracts, verified paths, and canonical artifact path patterns. (from: DjTools/scue 1.6.1) → Expanded the Handoff Packet schema with project root, working directory, exact output path, interface-contract sections, and added canonical artifact-path rules plus an Orchestrator dispatch-readiness checklist.

- [v1.7] [GAP] Protocol Enforcer did not produce a task-scoped kickstart prompt after bootstrap. (from: DjTools/scue 1.6.1 — CRUCIBLE bootstrap) → Updated the protocol and Enforcer prompt so bootstrap now includes `docs/agents/startup-prompts/kickstart.md` for the first expected invocation.

- [v1.7] [GAP] No interface contract file in project scaffold. (from: DjTools/scue 1.6.1) → Added `docs/interfaces.md` to the canonical project structure and required Architect/Developer interface-discipline rules to reference it directly.

- [v1.7] [BUG/GAP] Orchestrator state did not reconcile direct-dispatched work and had no active-session tracking. (from: DjTools/scue 1.6.1) → Expanded the Orchestrator State Snapshot with `## Active Sessions`, `## Dispatch Reconciliation`, and routing rules that force direct-dispatch reconciliation back into tracked state.

- [v1.7] [GAP/FRICTION] Validator PASS gave no explicit QA handoff signal, and combined validation could become too large. (from: DjTools/scue 1.6.1) → Added `## Recommended Next Step` to the Validator Verdict schema and extended the atomization test to Validator and QA dispatch so oversized review work must be split.

- [v1.7] [FRICTION] Read-before-write gate on protocol improvement logging was undocumented. (from: DjTools/scue 1.6.1) → Added an operational note to the protocol-improvement workflow: always read the improvements log before attempting an edit, even for append-only writes.

- [v1.6] [FRICTION/GAP] Orchestrator role overload — technical judgment responsibilities (FE State Behavior Check, Designer invocation thresholds, Interface Contract Discipline, QA dispatch decisions) accumulated on the Orchestrator, inflating context requirements to ~60K tokens. (from: DjTools/scue pipeline review) → Redistributed technical judgment to Architect. Architect now tags tasks with `QA Required`, `State Behavior`, `[REQUIRES DESIGNER]`, and interface contract ACs during task breakdown. Orchestrator trusts these tags. Updated §6.3, ORCHESTRATOR.md, ARCHITECT.md, templates/tasks.md.

- [v1.6] [GAP] No upstream feature challenge — nobody challenged whether a feature makes sense, what its purpose is, or how it fits existing features before the Architect specs it. (from: DjTools/scue pipeline review) → Added Phase 3.5: Feature Rationale Check to workflow (§3). Added Feature Rationale Mode to Architect preamble spec (§6.3) and SCUE ARCHITECT.md.

- [v1.6] [FRICTION] No Orchestrator context budget — no triage strategy for what to read when total context exceeds budget. (from: DjTools/scue pipeline review) → Added Context Budget section to SCUE ORCHESTRATOR.md. Added context budget guidance note to §6.3.

- [v1.6] [GAP] UI State Behavior template gave no guidance on state combinations — Designers either ignored compound states or enumerated all permutations. (from: DjTools/scue pipeline review) → Added Compound States section to templates/ui-state-behavior.md.

- [v1.6] [FRICTION] LEARNINGS.md is append-only with no pruning mechanism. (from: DjTools/scue pipeline review) → Added §10.3a: LEARNINGS.md Maintenance step to protocol review cycle.

- [v1.6] [GAP] Phase 7 Feature Review references a "Reviewer" role with no formal preamble or mode definition. (from: DjTools/scue pipeline review) → Added Feature Review Mode (Phase 7) to Architect preamble spec (§6.3) and SCUE ARCHITECT.md.

- [v1.6] [GAP] No check that handoff packets incorporate preceding session outputs — `[INTERFACE IMPACT]`, `[BLOCKED]`, and `[SCOPE VIOLATION]` flags could be silently dropped. (from: DjTools/scue pipeline review) → Added Pre-Dispatch Cross-Reference section to SCUE ORCHESTRATOR.md and §6.3.

- [v1.6] [GAP] Domain expert review — protocol had no concept of domain expert evaluation of specs. (partially resolved) → Feature Rationale Check (Phase 3.5) brings domain challenge upstream. Feature Review Mode (Phase 7) adds spec conformance downstream. Remaining narrow gap (domain expert evaluating spec technical soundness) addressed by loading domain skill files into Architect during Phase 3.5 and Phase 7.

- [v1.5] [BUG] Validator PASS did not verify live execution — agents reported bugs as fixed (Developer wrote COMPLETE, Validator wrote PASS, Orchestrator wrote COMPLETE in state snapshot) without anyone running the server or testing live behavior. Validator preamble explicitly said "Do not attempt to run the code yourself." (from: DjTools/scue BUG-BRIDGE-CYCLE) → Created QA Tester role (§1.1) with live verification mandate. Added Phase 6a (QA Verification) to workflow (§3): required for bug fixes and FE-BE integration tasks. Added QA Verification Dispatch rule to Orchestrator preamble (§6.3). Clarified Validator verdict scope (§2.7, §6.1): PASS means "meets handoff contract," not "fix works." Bug fixes cannot be marked COMPLETE without QA PASS.

- [v1.5] [GAP] No artifact type for scenario-based test cases — bug logs captured what broke, but nothing captured what *should* happen across hardware/application states. Manual testing had to be repeated from scratch each time. (from: DjTools/scue BUG-BRIDGE-CYCLE) → Added Test Scenario Matrix artifact (§2.9) with Given/When/Then format, disruption+recovery pairing, concrete thresholds. Added QA Verdict artifact (§2.10). Architect writes initial scenarios during spec phase (§6.3 Architect additions); QA Tester expands during testing. Scenarios are cumulative (regression checks). Added `docs/test-scenarios/` and `specs/feat-[name]/test-scenarios.md` to directory structure (§5.1).

- [v1.5] [GAP] No QA Tester role — no agent responsible for running the system and verifying behavior against real/mocked conditions. Validator checked contracts; nobody checked live behavior. (from: DjTools/scue BUG-BRIDGE-CYCLE) → Created QA Tester role (§1.1): read-only + Bash, produces QA Verdicts, invoked by Orchestrator for bug fixes/FE-BE integration/operator request. Added QA Tester preamble (§6.5). Added to Claude Code migration Phase 4 (§12.2). Updated Quick Reference Card flow diagram (§9).

- [v1.5] [GAP] No hardware mock infrastructure guidance for agent-executable integration tests — QA Tester cannot autonomously simulate USB disconnect, board power off, etc. → Added mock tool guidance to QA Tester preamble (§6.5): use tools from `tools/` when available, mark scenarios as `REQUIRES_OPERATOR` when not. Added `## Mock Tool Gaps` section to QA Verdict (§2.10) to systematically capture missing mock capabilities for Architect backlog.

- [v1.5] [GAP] No guidance on when to create a dedicated agent role vs. a skill file — role additions were ad-hoc with no decision framework. → Added §1.4 (When to Create a Role vs. a Skill File) with signal table, heuristic test, and examples (QA Tester as role, TypeScript as skill file, Pro DJ Link as skill file).

- [v1.4] [BUG] CONTRACTS.md not updated when a Developer session introduces a new interface value — recurring despite existing contract awareness rules. Root cause: handoff packets for bug fixes didn't include an explicit AC for interface documentation, so Developers deferred it and Validators had no grounds to FAIL. Observed: DjTools/scue BUG-BRIDGE-CYCLE added `"waiting_for_hardware"` to bridge_status WS `mode` field without updating CONTRACTS.md. (from: DjTools/scue) → Added **Interface Contract Discipline** to Orchestrator preamble additions (§6.3): Orchestrator must include explicit interface documentation AC on any handoff where interface changes are plausible. Added **[INTERFACE IMPACT] Protocol** to Developer preamble additions (§6.3): Developer must flag and stop rather than silently deferring interface changes not covered by the handoff AC.

- [v1.3] [GAP] No migration path from Claude desktop app to Claude Code CLI with subagents. → Added Section 12 (Migration to Claude Code Subagents) covering phased migration (Phases 1–4), hard constraints (no nesting, no thinking mode, 200K independent context, 4–7× token cost), observability tooling, hook enforcement model, and delegation error prevention.

- [v1.3] [FRICTION] Subagent nesting limitation: workflow chains up to 3 levels deep are incompatible with Claude Code's no-nesting constraint. → Added callout to Section 3 (Workflow Protocol) noting that in Claude Code, all roles are direct subagents of the Orchestrator — Phase 4 → 4a chaining becomes two sequential Orchestrator-spawned subagents. Addressed in full in Section 12.

- [v1.3] [GAP] Subagent observability: no tooling or structural enforcement guidance. → Added Section 12.3 (Observability) documenting `claude-esp` as required from Phase 2, `claude-tmux` as recommended, and hooks-based logging for Phase 4. Added Section 12.4 (Hook Enforcement vs. Prompt Enforcement) with gate-by-gate comparison table.

- [v1.3] [GAP] Subagent delegation errors: no constraints on subagent system prompts preventing model cheapness. → Added Section 12.5 (Preventing Subagent Delegation Errors) with three rules: explicit output scope, tool restrictions as strongest constraint, and task-complete spawn prompts. Updated Section 1.1 role table with "Claude Code Tools" column providing hard tool restriction mappings per role.

- [v1.3] [IDEA] Tool restriction enforcement: mapping role permissions to Claude Code tool restrictions. → Added "Claude Code Tools" column to Section 1.1 role table with per-role tool lists. Documented in Section 12.4 as structural (YAML frontmatter `tools:` field) vs. prompt-based enforcement. Addressed in Section 6.0 YAML frontmatter template.

- [v1.3] [IDEA] Hooks as protocol gates: documenting which gates should be hook-enforced vs. prompt-enforced. → Added Section 12.4 (Hook Enforcement vs. Prompt Enforcement) with four-row table covering session summary, file-path scope, spawn logging, and tool restrictions. Updated Validator preamble Step 0 (Section 6.1) with Claude Code note on SubagentStop hook. Added `.claude/hooks/subagent-stop.sh` to Section 5.1 directory structure.

- [v1.3] [IDEA] Skills-as-frontmatter: skill files should be structured to work with Claude Code YAML frontmatter. → Added Section 6.0 (Claude Code Subagent Compatibility) documenting YAML frontmatter format for all preambles, description field discipline, and model field guidance. Added `.claude/agents/` directory to Section 5.1 project layout.

- [v1.2] [GAP] No mechanism for capturing, monitoring, or correcting frequent small agent missteps (wrong Python version, missing venv, retried commands). Missteps were invisible — no reporting, no pattern detection, no deterministic correction. → Implemented three-layer misstep management: **(1) Capture:** added `## Missteps` field to Session Summary schema (§2.2) and misstep reporting rule to COMMON_RULES.md spec. **(2) Review:** Orchestrator scans missteps at session start, tracks recurring patterns in state snapshot `## Recurring Missteps` (§2.8), proposes fixes (skill file, hook, or preamble rule) (§6.3). Validator flags missteps already covered by existing guidance (§6.1). **(3) Auto-correct:** Protocol Enforcer gains `.claude/settings.json` + `.claude/hooks/` as deliverable (IMPLEMENTATION_PROMPT.md §6) — PreToolUse hooks for deterministic command correction. Added `.claude/` to project directory structure (§5.1).

- [v1.2] [GAP] Agents attempt to edit files without reading them first — Edit tool rejects the change with "attempted to edit {file} without reading." Not documented in protocol, so agents had no reason to know the constraint existed. → Added "Read before edit" rule to COMMON_RULES.md spec (IMPLEMENTATION_PROMPT.md) and DEVELOPER.md additions (OPERATOR_PROTOCOL.md §6.3): read every file before editing; Edit tool enforces this per-session.

- [v1.2] [GAP] No formal Orchestrator continuity artifact — each new session reconstructed state from git history, session file globbing, and multiple reads in unpredictable locations. The `orchestrator-day-summary.md` pattern existed informally in DjTools/scue. → Formalized as **Orchestrator State Snapshot** (§2.8): schema defined, stored at `docs/agents/orchestrator-state.md`, written at session end and read immediately after preambles at session start. Added to §5.1 directory structure, §6.3 Orchestrator preamble additions, Phase 3 load order, §5 startup prompt spec, and templates deliverable in IMPLEMENTATION_PROMPT.md.

- [v1.2] [GAP] Protocol Enforcer generates Orchestrator startup prompts that omit `tasks.md` and session summaries — Orchestrator falls back to asking the operator verbally instead of reading artifacts. → Added startup prompts as a Protocol Enforcer deliverable (IMPLEMENTATION_PROMPT.md §5). Added `docs/agents/startup-prompts/` to project directory structure (OPERATOR_PROTOCOL.md §5.1). Updated ORCHESTRATOR.md spec: read loaded artifacts to determine state; if required files are absent, request them by name — do not ask for verbal summaries.

- [v1.2] [IDEA] Incorporate positive feedback into agent prompts. → Lightly implemented: added `## What Went Well` field to Validator Verdict schema (§2.7) and corresponding rule to Validator preamble (§6.1): specific, evidence-based praise before issues. Updated VALIDATOR.md spec in IMPLEMENTATION_PROMPT.md. Deferred: `## Feedback from Last Session` in handoff packets (no supporting failure yet).

- [v1.2] [BUG] Protocol Enforcer was incorrectly placed in project-level `preambles/` directory (Section 5.1), implying each project should have a `PROTOCOL_ENFORCER.md`. The Protocol Enforcer is a root-level role only — it operates across projects, not within them. → Removed `PROTOCOL_ENFORCER.md` from Section 5.1 preambles listing. Updated Section 5.2 meta-level structure to include `IMPLEMENTATION_PROMPT.md`. Updated roles table to note "root-level only — not a project agent." Reinforced in Section 6.4 and added explicit guard in `IMPLEMENTATION_PROMPT.md` Section 2.

- [v1.2] [BUG] Protocol Enforcer role existed in practice but was undefined in OPERATOR_PROTOCOL.md and IMPLEMENTATION_PROMPT.md — operators had no documented scope, invocation trigger, or relationship to other roles; IMPLEMENTATION_PROMPT.md was mislabeled as an Architect task. → Added Protocol Enforcer to roles table (Section 1.1). Revised Phase 0 to name Protocol Enforcer for infrastructure steps and Architect+human for project-specific docs (Section 3). Added PROTOCOL_ENFORCER.md to preambles directory listing (Section 5.1). Added Protocol Enforcer preamble (Section 6.4). Added propagation steps to Section 10.3. Reframed IMPLEMENTATION_PROMPT.md as Protocol Enforcer prompt.

- [v1.1] [BUG] Orchestrator resolved a bug inline without a session summary, bug log role tag, or milestone tracker update — next session had corrupted project state view. (from: DjTools/scue) → Added Inline Fix Protocol to Orchestrator preamble additions (Section 6.3): three-part delegation gate (single file + mechanical + isolated) before any inline fix; mandatory session summary (role: Orchestrator-inline), bug log update, and milestone tracker update before session end. Added role identifier to Session Summary schema (Section 2.2). Added inline-fix accountability and milestone maintenance rules to COMMON_RULES.md spec (IMPLEMENTATION_PROMPT.md).

- [v1.1] [GAP] No protocol guidance on when the Orchestrator should self-resolve vs. delegate to a Developer agent. (from: DjTools/scue) → Addressed by same Inline Fix Protocol change above.

- [v1.0] [BUG] Developer agent completed a task but did not write a session summary. → Added Step 0 pre-check to Validator preamble (Section 6.1): Validator now verifies session summary exists and is complete before evaluating code. Missing summary = automatic FAIL.

- [v1.0] [IDEA] Orchestrator should automatically identify completed features whose session artifacts are ready for archival. → Added Section 11 (Artifact Archival) to Operator Protocol with archive rules and timing. Added "Housekeeping: Archival" responsibility to Orchestrator preamble additions (Section 6.3).

- [v1.0] [GAP] No independent validation gate after Developer sessions — bugs could propagate silently to the next task. → Created Validator role (`docs/agents/preambles/VALIDATOR.md`). Independent check agent that receives handoff packet + session summary + code diff only. Produces pass/fail verdicts using `templates/validator-verdict.md`. Enforces: session summary pre-check (missing = auto FAIL), scope compliance, acceptance criteria verification, SCUE-specific rules (no cross-layer imports, no Pioneer data overwrites, no hardcoded config, type hints, logging module). Orchestrator updated to enforce Developer → Validator → next task cycle.

- [v1.0] [GAP] No structured UI/UX design step before frontend implementation — Developers made ad-hoc UI decisions without design specs. → Created Designer role (`docs/agents/preambles/DESIGNER.md`). Produces UI spec documents covering: component hierarchy, state flow, layout descriptions, interaction patterns, visual hierarchy. Does not write code or make architectural decisions (flags as `[DECISION NEEDED]`). References existing SCUE design system (Tailwind, existing components). Architect updated with `[REQUIRES DESIGNER REVIEW]` flag; Orchestrator updated with Designer invocation trigger for plans that include UI work.
