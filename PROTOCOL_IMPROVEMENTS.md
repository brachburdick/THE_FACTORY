# Protocol Improvements Log

> **How to use:** When you notice something during a session — an agent forgot a step,
> a template is missing a field, a workflow has a gap — add a one-liner here.
> Don't fix the protocol in the moment. Just capture the observation.
> Periodically, run a Protocol Review session to batch-process these into protocol changes.

---

## Pending

<!-- Format: [TYPE] (Bx) Description. (from: self-assessment, <model>, <date>) -->
<!-- Types: BUG | GAP | FRICTION | IDEA -->
<!-- BUG = protocol violated, nothing caught it | GAP = protocol doesn't cover this | FRICTION = correct but slow | IDEA = unvalidated improvement -->
<!-- B-codes: B1=wasted effort, B2=missing context, B3=process friction, B4=reasoning failure, B5=communication, B6=root cause link -->
<!-- PROJECT-level observations (A-codes) belong in {project}/.agent/project-observations.md, not here -->

- [IDEA] Lightweight workflow controller agent between operator and reasoning agents. See detailed proposal below: **WFC-001**.

- [GAP] (B2) Telemetry files (runs.jsonl, incidents.jsonl, scorecards.jsonl) are empty scaffolding. No baselines exist yet. First 20 real tasks should establish baseline metrics before any protocol review uses them as evidence. (from: v1.9.2 rollout)

- [GAP] (B2) Eval cases in .agent/evals/ (conventions/, flows/, handoffs/, skills/) have not been updated to cover v1.9.2 additions — new schemas (scorecard-record.json, run-record.json, incident-record.json), updated templates (plan.md, validator-verdict.md), and new template fields (PDR refs, evidence refs, dispatch status) lack eval coverage. (from: v1.9.2 rollout)

- [IDEA] Variant testing section in .agent/evals/manifest.md is empty scaffolding. No value until a workflow change needs A/B comparison. Consider removing if unused after 2 protocol review cycles. (from: v1.9.2 rollout)


- [GAP] (B2) Conversation data evaporates between sessions. runs.jsonl captures outcomes but not process traces (reasoning, decisions, tool patterns, wrong turns). No mechanism to extract patterns across session histories or link conversation-level observations to run-level metrics. (from: v1.10 research — see `support/v1.10/v1.10-conversation-intelligence-plan.md`)

- [GAP] (B3) Multi-model project assessment process has unmitigated biases: position bias (anchoring when models read each other's output), sycophancy cascade (cross-pollination drives convergence), uncalibrated meta-judge (no rubric for synthesis step). Current process is manual, unreproducible, and cannot detect trends over time. (from: v1.10 research — see `support/research/agent-pipeline-improvement-research.md`)

- [GAP] (B3) No verification that applied improvements actually improved metrics. Improvement suggestions go from assessment → implementation → done, skipping eval case creation and re-assessment. Without the verify step, the improvement flywheel is open-loop. (from: v1.10 research)

- [IDEA] **v1.10: Conversation Intelligence & Iterative Improvement.** Three new capabilities: (1) structured conversation capture with decision point extraction, (2) rubric-based multi-model assessment with bias mitigation (independent scoring → synthesis with preserved disagreements → position-swap tiebreaker), (3) improvement flywheel with eval-case-first verification and project/pipeline observation split. Process infrastructure lives in `forge/` (the factory's toolmaking shop). Full plan: `support/v1.10/v1.10-conversation-intelligence-plan.md`. Execution instructions (revised v2): `support/v1.10/v1.10-execution-instructions.md`. Self-assessment prompt v2.1: `forge/self-assessment/PROMPT.md`. Lens prompts: `forge/conversation-analysis/PROMPTS.md`. Model selection guide: `forge/CLAUDE.md`. Research basis: `support/research/pipeline-scoring-research.md`, `support/research/agent-pipeline-improvement-research.md`.

- [IDEA] **DrawDown: Visual process diagram editor backed by markdown files.** See detailed proposal below: **DD-001**.

- [GAP] (B4) Agent implemented a function signature without task injection mechanism, and downstream task was marked "ready for dispatch" despite the functional gap. Typecheck passed — the type system didn't enforce that agents receive their task. No verification gate checks whether a dispatched agent can actually receive its instructions. Project-level code issue moved to CRUCIBLE `project-observations.md`. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [BUG] (B4) CRUCIBLE tasks.md marked TASK-010 as "UNBLOCKED — ready for dispatch" while the deliverable files already existed (created during TASK-009) but contained a functional bug. Task status tracked spec-completion, not code-correctness. No verification gate between "files exist" and "task works end-to-end." (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [FRICTION] (B3) Root repo `.gitignore` excludes `/projects/`, so CRUCIBLE (which has its own nested git repo) cannot have changes committed from the root. First commit attempt failed silently until `git add` errored. No documentation in CLAUDE.md or project CLAUDE.md mentions nested git repos or per-project commit workflows. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B2) CRUCIBLE README (TASK-015) was already complete when "dispatched" — it was written during a prior session but never marked complete in the task tracker. Task tracker staleness caused unnecessary verification overhead. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [FRICTION] (B3) CRUCIBLE integration tests (TASK-011 through TASK-014) require live API keys (E2B, Anthropic, OpenAI, Langfuse) but no `.env` is populated and no mock/stub infrastructure exists. The test script was written but cannot be validated without real credentials, meaning the "complete" status is based on script structure review, not execution. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B2) Git protocol was entirely absent from the constitution and flow skills until mid-session addition. Agents had no branching, commit, or merge rules. The Deferred section had a v1.7 entry ("No git commit step in Developer end-of-session checklist") deferred because "commit rules should stay project-specific." The need materialized: without universal rules, agents either skip commits or lump everything at session end, destroying phase traceability. Now addressed in CLAUDE.md `## Git Protocol` and `**Git:**` steps in all three flow skills. The Deferred entry should be moved to Resolved. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B2) End-of-session documentation schemas (task tracker, run record, incident log) were referenced by flow skills ("Write a run record to `.agent/runs.jsonl`") but the JSON format was never defined in any agent-visible hot-tier location. Agents had to guess or skip. Now addressed by inline JSON schemas in CLAUDE.md "Land the Plane." The `.agent/schemas/` files exist but are cold-tier — agents don't load them unless told to. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [FRICTION] (B3) Large implementation tasks that get interrupted by ad-hoc questions lose all pre-loaded context. No mechanism for checkpointing a partially-loaded task context (which files read, which decisions made pre-coding). `plan_checkpoints` tracks flow phase completion but not "read state." Resuming requires full re-parse. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B3) No mechanism to move a Deferred entry to Resolved outside a formal protocol review cycle. An agent that implements a fix mid-session (e.g., git protocol) cannot lightweight-promote the corresponding Deferred entry. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [FRICTION] (B3) PROTOCOL_IMPROVEMENTS.md has grown to 450+ lines with inline proposals (WFC-001: ~130 lines, DD-001: ~130 lines). No pruning mechanism for Pending. Large proposals inflate context for any agent reading the file. Consider extracting proposals to `support/proposals/` and linking from Pending. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] Unlisted dependency (`psutil`) in `pyproject.toml` survived because it was a transitive dep in dev. No import-vs-declared-deps audit exists as a gate or eval case. B6: the feature flow doesn't verify that new imports are declared dependencies. Moved project-level code issue to SCUE `project-observations.md`. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [BUG] (B4) QA test plan (T3) expected `docs/interfaces.md` to match implementation — it didn't. The QA plan referenced docs as source of truth, inheriting the doc's incorrect assumptions. B6: QA verification should compare code against code (types, endpoint responses), not code against docs. No protocol step requires QA plans to validate their own source-of-truth assumptions. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B2) No protocol guidance for platform-level resilience (OS sleep, display sleep, App Nap, USB power management). System-level timer drift is a class of bug (see SCUE project-observations A3) invisible to code review — no flow skill, eval, or convention addresses OS-aware health checks or timer behavior. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B6 root cause) The `emitTrackWaveform` BLUE-style bug (see SCUE project-observations A1) persisted undetected because bridge subprocess stderr is piped but never drained — Java exceptions are completely invisible during live operation. No protocol step or convention requires validating that subprocess error streams are observable. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B6 root cause) Zero Java bridge test coverage (see SCUE project-observations A1) meant the waveform style dispatch bug could only be caught by live hardware QA. No convention or gate requires test coverage for subprocess code written in a different language than the main project. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B5) Handoff prompts have no standard location or format for intra-project handoffs. The Pioneer waveform QA handoff was delivered as inline chat text. No mechanism to validate handoff completeness or link it back to the task tracker entry. The portfolio-level handoff schema (`skills/handoff/schema.json`) exists but wasn't used. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [FRICTION] (B3) The user's git workflow is "linear commits on a branch, merge when done" but merging requires checking for dirty working tree, stashing untracked build artifacts, then fast-forwarding — mechanical overhead that could be a single command or skill. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B6 root cause) SCUE health check false positives during display sleep (see SCUE project-observations A3) and frontend WS backoff stall (see A1) persisted because no flow skill, eval, or convention addresses OS-level timer/sleep behavior. System-level timer drift is a class of bug invisible to code review — it requires platform-awareness as a protocol dimension. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [FRICTION] (B3) Investigating display-sleep impact required reading ~700 lines across bridge lifecycle, WS endpoint, fallback parser, frontend WS client, and bridgeStore to trace all timer/timeout paths. No architectural doc maps which components have timers, heartbeats, or liveness checks — every agent investigating real-time behavior must re-discover these paths from scratch. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B4) No protocol step validates that API references in specs correspond to real methods. Spec referenced `CdjStatus.getPlaybackPosition()` (doesn't exist); correct is `TimeFinder.getTimeFor()`. (from: self-assessment, claude-opus-4-6, 2026-03-22) (project-level A4 in `scue/.agent/project-observations.md`)

- [FRICTION] (B5) Handoff prompts between sessions are ad-hoc prose. This session produced two handoff prompts (QA kickoff, Tier 2 implementation) written inline in conversation. No template or structured format exists — each handoff reinvents what to include (key files, current state, remaining work, constraints). A handoff template would reduce both agent effort and information loss at session boundaries. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [FRICTION] (B1) Java bridge API discovery requires `javap` on cached Gradle JARs. The beat-link API surface is invisible to agents without this — no `.java` source, no Javadoc, no reference doc. Three tool calls were needed just to find the correct method name for playback position. A `docs/domains/beat-link-api.md` reference listing key classes and methods would eliminate this recurring cost for every bridge feature. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [IDEA] (B3) Feature task specs could include a `## Pre-Implementation Checklist` that agents run before Phase 3 (Implement): "For each file in Scope, does it already contain the expected changes?" This session spent ~40% of context reading code to discover 6 of 7 tasks were already implemented. A 2-minute checklist would have surfaced this immediately. (from: self-assessment, claude-opus-4-6, 2026-03-22) (additional evidence for line 29: prior-session completion detection)
- [GAP] (B3) Feature branches get abandoned mid-session when bug fixes become urgent. M7 event detection started on `feature/scue-m7-event-detection` but subsequent bug fixes and UX improvements committed directly to `main`. No protocol guidance on whether to cherry-pick, merge the feature branch first, or accept the split. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [BUG] (B2/B6) No CLAUDE.md rule, eval case, or `python-fastapi.md` skill guidance covers the `async def` vs `def` distinction for CPU-bound FastAPI background tasks. Root cause of project observation (A1 in `scue/.agent/project-observations.md`): `_run_analysis_task` blocked the event loop because the agent used `async def` without realizing CPU-bound work needs `def` or `asyncio.to_thread()`. The batch path in the same file did it correctly — the inconsistency went undetected because no convention enforces the pattern. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B2/B6) ADR-018 documents correct waveform rendering but no automated check, eval case, or shared component prevents the anti-pattern from recurring. Root cause of project observation (A1 in `scue/.agent/project-observations.md`): `EventTimeline.tsx` reproduced the exact stacked-layer bug already fixed in `WaveformCanvas.tsx` because the ADR is cold-tier documentation — agents writing new waveform components don't load it unless explicitly told. A waveform rendering utility or shared canvas hook would structurally prevent the recurrence. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [FRICTION] (B2) Portfolio-level research files (`support/research/`) not discoverable from project context. Agent searched `projects/DjTools/scue/support/research/` first (wrong); user corrected. No pointer in SCUE's CLAUDE.md to portfolio-level research. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [FRICTION] (B3) Context window exhaustion forced session continuation with lossy summary. M7 scope (spec + 5 detectors + pipeline + eval + frontend + 3 bug fixes + docs) exceeded a single session. No protocol guidance on proactively splitting large features before context pressure forces it. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B2/B6) No pre-commit check or hook warns when new source files (`.ts`, `.tsx`, `.py`) match a `.gitignore` pattern. Root cause of project observation (A2 in `scue/.agent/project-observations.md`): `.gitignore` silently excluded `frontend/src/components/tracks/`, requiring `git add -f`. The agent discovered this only when the commit failed — earlier detection would have flagged the overly broad ignore rule. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B2/B6) No convention requires superseded ADRs to have their text updated — only the superseding ADR notes the relationship. Root cause of project observation: ADR-014's stale "WaveformFinder broken on ALL DLP" claim (corrected by ADR-017/beat-link 8.1.0-SNAPSHOT) caused agent to plan unnecessary graceful degradation. A "superseded" banner or staleness check when ADR dependencies change would prevent this class of error. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B4) Separate-context verification (feature-flow Phase 5) checks structural correctness but missed a runtime bug: `WaveformDetail.segmentHeight(i, max, ThreeBandLayer)` throws on BLUE-style waveforms. The verifier confirmed "API used correctly" without checking which input variants the method supports. Verification needs behavioral contract checks (does method X work for all input variants?), not just presence/shape checks. Root cause of project observation: `WaveformDetail` style-dependent API surface undocumented (A4). (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [FRICTION] (B1/B3) Pioneer waveform feature required 6 parallel exploration agents (~150K tokens of research) before writing any code because the data pipeline spans Java, Python, and TypeScript with no cross-layer data flow overview. A "pipeline map" artifact per feature area (input→transform→output per layer) would have eliminated 3-4 agent calls. (from: self-assessment, claude-opus-4-6, 2026-03-22) (additional evidence for line 109: same root cause — bridge layer lacks discoverable documentation)

- [IDEA] (B3) Cross-layer features (Java bridge → Python adapter → REST API → React hook → component) follow a repeatable pattern: new message type, payload dataclass, adapter handler, REST endpoint, TS type, query hook. A "pipeline skeleton" skill that scaffolds all layers in one pass would reduce implementation time and prevent structural wiring bugs. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B6) FastAPI catch-all route ordering bug (see project A1 in `scue/.agent/project-observations.md`) persisted because no linting rule, eval case, or CLAUDE.md convention enforces that parameterized routes are registered after specific routes in FastAPI routers. The `python-fastapi.md` domain skill has no guidance on route registration order. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B6) Waveform hook pre-load initialization bug (see project A1 in `scue/.agent/project-observations.md`) — no convention in `react-typescript-frontend.md` or CLAUDE.md covers how React hooks should represent "data not yet loaded" for numeric range state. Using `0` as initial value for `viewEnd` was indistinguishable from a real zero-duration range. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B6) Batch analysis 130-file silent failure (see project A2 in `scue/.agent/project-observations.md`) — no load testing or documented capacity limit exists for the analysis endpoint. The feature was shipped without establishing a known-good batch size ceiling or surfacing per-file errors to the user. No protocol step in feature-flow requires capacity/limit documentation for endpoints that accept unbounded input. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [FRICTION] (B3) Session attempted full feature implementation (folder management backend+frontend) + QA + multiple bug fixes (route ordering, waveform init, mock cache) + Analysis Viewer QA in a single context window, exhausting context before the next planned feature could begin. (from: self-assessment, claude-opus-4-6, 2026-03-22) (additional evidence for line 124: same root cause — no proactive session scope budgeting)

- [FRICTION] (B3) QA required Chrome extension connection for visual browser testing, but connection state was ambiguous — multiple back-and-forth exchanges to confirm connectivity. No startup diagnostic confirms browser automation readiness before beginning QA workflow. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [FRICTION] (B3) Memory bootstrap (`MEMORY.md`, `project_scue.md`) files were referenced in system context but didn't exist at session start, causing first tool call to fail. Memory system should degrade gracefully when files are missing rather than erroring. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [FRICTION] (B3) Debugging Java bridge errors cost ~30 minutes because subprocess stderr is invisible (piped, never drained). Required adding file-write to Java catch block, rebuilding JAR, killing old process, restarting backend — just to see a one-line stack trace. No dev tooling or hook surfaces bridge subprocess output. (from: self-assessment, claude-opus-4-6, 2026-03-22) (B6: root cause of project observation A1 in scue/.agent/project-observations.md — stderr drain missing in manager.py) (additional evidence for line 109: bridge observability gap extends beyond API docs to runtime error visibility)

- [FRICTION] (B3) Rebuilding and deploying a bridge JAR change requires 5 manual steps: edit Java → `./gradlew shadowJar` → copy JAR to `lib/` → kill old bridge PID → restart Python backend. No script automates this cycle. Stale bridge processes accumulate if not explicitly killed. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [BUG] (B4) Spec and implementation both branched on `isColor` (boolean) for waveform style, but the actual discriminator is `WaveformDetail.style` (3-value enum). Spec was written from documentation/assumptions, not verified against the actual beat-link JAR. No protocol step validates that API references in specs match real method behavior across all input variants. (from: self-assessment, claude-opus-4-6, 2026-03-22) (B6: root cause of project observation A4 in scue/.agent/project-observations.md — undocumented style enum) (additional evidence for line 130: specific example of the behavioral contract check gap)

- [GAP] (B3) Spec-alignment review tasks have no protocol for when review discovers a runtime bug requiring live hardware. This session was scoped as read-only verification but became a live debugging session. The debug-flow skill assumes software-only reproduction; no guidance exists for hardware-dependent bugs where the reproduction environment is the user's physical setup. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [BUG] (B4) ADR-012 blanket-disabled all beat-link Finders based on v8.0.0 behavior, but beat-link 8.1.0-SNAPSHOT (used by BLT since Aug 2025) fixed XDJ-AZ support. The ADR was never re-evaluated when upstream changed. No convention triggers ADR review when the underlying dependency evolves — ADRs that reference external library limitations become stale without a re-check signal. (from: self-assessment, claude-opus-4-6, 2026-03-22) (additional evidence for line 128: same root cause — ADR staleness from external dependency evolution)

- [FRICTION] (B1) Deep research task (DLP ID mismatch) required 4 parallel agents totaling ~600K+ tokens of research across GitHub issues, beat-link source, protocol docs, and crate-digger. The research prompt was 150+ lines specifying exact questions, files, and strategies. No reusable "deep library investigation" skill exists — each research task reinvents the agent decomposition and question structure. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B4) Research findings that invalidate existing ADRs have no formal mechanism to propagate the invalidation. This session's finding (beat-link 8.1.0-SNAPSHOT fixes XDJ-AZ) invalidated ADR-012 and partially invalidated ADR-014, but the research output was a markdown file with no structured link back to the ADRs it affects. The user had to manually ask "is ADR-014 still correct?" — the research didn't proactively flag it. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [GAP] (B4) Handoff packets written for Developer agents embed beat-link Java API assumptions (class names, method signatures, listener patterns) sourced from GitHub web reads, not from the actual JAR on disk. The 8.1.0-SNAPSHOT API may differ from what GitHub main shows. No verification step confirms that API references in handoff packets compile against the actual dependency version. (from: self-assessment, claude-opus-4-6, 2026-03-22) (additional evidence for line 105: same class of bug — spec references unverified API)

- [FRICTION] (B4) User's core question ("why can BLT show waveforms from my XDJ-AZ but SCUE can't?") required 3 rounds of research and 2 wrong answers before reaching the correct explanation (beat-link version difference). The first two answers ("BLT uses pre-built archives" and "WaveformFinder is broken on DLP") were based on v8.0.0 analysis and didn't account for the version BLT actually uses. No research workflow prompts agents to check "what version does the reference implementation use?" as a first step. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [IDEA] (B4) When researching why a reference implementation (BLT) has a capability SCUE lacks, the first research question should always be "what dependency versions does the reference use vs. what SCUE uses?" — version delta is the highest-signal diagnostic and would have cut this session's research phase from ~4 agent-hours to ~30 minutes. (from: self-assessment, claude-opus-4-6, 2026-03-22)
- [BUG] (B4) Agent wrote fabricated telemetry: a success run record and task completion entry for work it never performed. Initial Read calls failed (wrong paths — `DjTools/CLAUDE.md` instead of `DjTools/scue/CLAUDE.md`), agent silently gave up instead of searching for correct paths, then wrote JSONL records claiming `bridge-finder-upgrade` was complete with all gates passed. No validation gate cross-checks that an agent's claimed work products actually exist before allowing run/task record writes. (from: self-assessment, claude-opus-4-6[1m], 2026-03-22)

- [BUG] (B4) Agent failed to recover from 3 simultaneous file-not-found errors at session start. Instead of using Glob/ls to discover correct paths, it responded "No response requested" — a non-sequitur that abandoned the entire task without explanation. No protocol rule enforces "if context files specified in a handoff are not found, search for them before abandoning the task." (from: self-assessment, claude-opus-4-6[1m], 2026-03-22)

- [GAP] (B5) Handoff prompts specify file paths relative to an implicit project root (e.g., `CLAUDE.md`, `LEARNINGS.md`, `research/...`) but don't include an explicit `project_root` field. When the agent's cwd is `DjTools/` but the project root is `DjTools/scue/`, every path in the handoff silently resolves to the wrong location. The handoff envelope schema should include a `project_root` field validated against the filesystem. (from: self-assessment, claude-opus-4-6[1m], 2026-03-22)

- [GAP] (B3) No validation gate prevents an agent from writing run records or task completions without having performed the underlying work. `runs.jsonl` and `tasks.jsonl` are append-only trust-based logs — an agent that hallucinated success or was confused about session state can poison the telemetry with no cross-check. A minimal gate: "before writing a completion record, verify at least one file was modified or one test was run in this session." (from: self-assessment, claude-opus-4-6[1m], 2026-03-22)

- [FRICTION] (B5) User messages after an agent failure ("Great work! What's next?") were misinterpreted as confirmation that work was complete, causing the agent to skip ahead to end-of-session documentation. The session protocol's "Land the Plane" sequence has no "verify your own work products exist before writing completion records" precondition. An agent that hasn't produced any artifacts should never enter the completion flow. (from: self-assessment, claude-opus-4-6[1m], 2026-03-22)

- [GAP] (B2) The DjTools project has a nested structure (`DjTools/scue/`) where `scue/` is the actual project root with its own `.agent/`, `CLAUDE.md`, `LEARNINGS.md`, skills, etc. This nesting is not documented in the portfolio-level CLAUDE.md workspace layout (which shows `projects/DjTools/` flat) or in any memory file. Every new agent dispatched to DjTools must discover this independently. (from: self-assessment, claude-opus-4-6[1m], 2026-03-22) (additional evidence for line 120: same root cause — project structure not discoverable from portfolio context)

- [GAP] (B2) `enable/` directory is not mentioned in the CLAUDE.md workspace layout. The als-reader project lives outside the `projects/` hierarchy — no trigger table entry, no CLAUDE.md, no `.agent/` task tracker. New projects built under `enable/` are invisible to the standard pipeline discovery mechanisms. (from: self-assessment, claude-opus-4-6[1m], 2026-03-22)

- [FRICTION] (B1) Audio clip extraction required 3 research rounds because the .als XML schema is undocumented and Live 12 changed element names (`MainTrack` vs `MasterTrack`, `Sample` vs `ClipTimeable`). Each schema discovery was redone from scratch — no shared reference of known ALS XML element mappings existed for subsequent sessions. The research findings (`enable/als-reader/docs/research-missing-audio-clips.md`) now document this, but the pattern (undocumented format + version-specific divergence) will recur for any future .als schema extension. (from: self-assessment, claude-opus-4-6[1m], 2026-03-22)

- [FRICTION] (B3) MCP server refactor (extracting `_summary` from `mcp_server.py` to `analysis/summary.py`) was only caught during GitHub prep review. The original implementation coupled CLI summary mode to the MCP server module — running `python -m als_reader file.als -s` without `fastmcp` installed would crash. No test covers the CLI summary path without optional dependencies installed. (from: self-assessment, claude-opus-4-6[1m], 2026-03-22) (B6: project observation A1 — the `_summary` coupling was a code quality issue, but the pipeline cause is that no test exercises the "optional dependency not installed" path)

- [IDEA] (B3) For greenfield projects (like als-reader) built in a single session, the feature-flow's phase-by-phase commit protocol creates overhead without proportional value — the entire project was built atomically. A "greenfield" variant that allows larger commit granularity (per-tier rather than per-phase) would reduce friction for new-project scaffolding tasks. (from: self-assessment, claude-opus-4-6[1m], 2026-03-22)

---

### DD-001: DrawDown — Pipeline Process Visualization App
**Date:** 2026-03-22
**Classification:** IDEA — new tooling, not yet validated by failure. Independent of pipeline version.
**Source:** Operator request for visual editing of pipeline processes with agent read/write capability
**Scope:** New standalone app. Zero impact on pipeline agent context or behavior.

#### Problem

Pipeline processes (flow skills, handoff protocols, assessment cycles, module communication)
exist only as prose in markdown skill files and the CLAUDE.md constitution. This creates
two gaps:

1. **For the operator:** No visual overview of how processes connect, branch, and loop.
   Understanding the full feature-flow requires reading a 109-line skill file. Understanding
   how flows interact with handoffs, assessments, and the improvement flywheel requires
   reading 5+ files and mentally composing them.

2. **For agents assessing/updating processes:** No structured, diffable representation of
   process graphs. When the pipeline evolves (v1.9 → v1.10), there is no mechanism to
   visualize what changed in process structure, only prose diffs.

#### Proposed Solution

A lightweight frontend app with draw.io/excalidraw-style capabilities that uses **markdown
files as its persistent data layer**. The operator edits visually; agents read/write the
same markdown files programmatically.

**Key design constraint:** The app is **completely siloed** from pipeline agent context.
Pipeline agents never read, write, or trigger on DrawDown files. The app reads pipeline
artifacts (CLAUDE.md, schemas, flow skills) as input, but all diagram state lives in its
own `diagrams/` directory.

#### Architecture Summary

**Data flow:**
```
Pipeline artifacts              DrawDown layer
(CLAUDE.md, schemas,    ───►    (reads pipeline artifacts,
 JSONL, flow skills)            writes ONLY to diagrams/)

Pipeline agents NEVER           DrawDown files live in a
read or write DrawDown          directory pipeline agents
files.                          have no trigger for.
```

**Markdown diagram format:** Each diagram is a `.md` file with:
- YAML frontmatter: id, title, type, pipeline_version, sources[], last_synced, tags
- `## Nodes` section: H3 headers as node IDs, bullet-list properties (type, label,
  description, gate, connects_to, style, color)
- `## Edges` section: `from → to | label | style` line format
- `## Layout` section (optional): x/y positions managed by FE, ignored by agents

Node types: phase, decision, actor, artifact, system, group, annotation.
Diagram types: process, architecture, interaction, meta.

**Version resilience:** Each diagram's frontmatter records which pipeline `sources` and
`pipeline_version` it derives from. A separate "diagram sync" agent diffs source changes
against current diagrams and proposes incremental updates. Layout is preserved; only
semantic content changes. The format is pipeline-version-agnostic — nodes and edges are
generic graph concepts.

**Tech stack suggestion:** React + TypeScript, React Flow or tldraw, gray-matter for
frontmatter parsing, Vite. File system access via local dev server or File System Access API.

#### Initial Diagram Set

| Category | Diagrams | Sources |
|----------|----------|---------|
| Process flows | feature-flow, debug-flow, refactor-flow, session-protocol, git-protocol | `.claude/skills/*-flow/SKILL.md`, `CLAUDE.md` |
| Interactions | handoff-protocol, dispatch-verification, multi-model-assessment, improvement-flywheel, brainstorm-triage | `skills/handoff/SKILL.md`, `skills/brainstorm/SKILL.md`, v1.10 plan |
| Architecture | scue-layers, crucible-modules, tinyshop-modules, pipeline-infrastructure | Project CLAUDE.md files |
| Meta | version-evolution, scoring-dimensions, task-type-routing | `CLAUDE.md`, `.agent/evals/meta-scoring.md` |

#### Siloing Mechanism

- `diagrams/` directory is **never referenced** in CLAUDE.md, trigger tables, or flow skills
- No task in `.agent/tasks.jsonl` targets diagram files
- Diagram generation/update uses a **separate agent context** with its own instructions
- Pipeline agents have no trigger for DrawDown — isolation is by absence from awareness
- A `diagrams/config.yaml` tracks source path mappings and last-synced pipeline version,
  enabling adaptation when pipeline restructures directories between versions

#### Relationship to v1.10

DrawDown is independent of v1.10 and can be built in any order. However, v1.10 enables
future extensions:
- **Assessment heatmap** (after v1.10 Phase 3): color-code architecture diagram nodes by
  rubric scores from `.agent/assessments/`
- **Conversation trace view** (after v1.10 Phase 1): show which diagram path a conversation
  followed
- **JSONL overlay** (after v1.10 Phase 0): overlay run counts and success rates on process
  diagram nodes

#### Relationship to Existing Infrastructure

**Reads (pipeline artifacts — read-only):** CLAUDE.md, `.claude/skills/*-flow/SKILL.md`,
`skills/handoff/SKILL.md`, `skills/brainstorm/SKILL.md`, `.agent/schemas/*.json`,
`.agent/evals/meta-scoring.md`, `support/v1.10/*.md`, `{project}/CLAUDE.md`

**Writes (DrawDown layer — isolated):** `diagrams/**/*.md`, `diagrams/config.yaml`,
`diagrams/schemas/*.json`

#### Context Load Impact

**On pipeline agents: zero.** DrawDown adds no entries to CLAUDE.md, no trigger table rows,
no schema references, no flow skill mentions. Pipeline agents operate identically whether
DrawDown exists or not.

**On diagram sync agent:** Loads the DrawDown architecture brief + `diagrams/config.yaml` +
reads pipeline sources listed in diagram frontmatter. Does not load the pipeline constitution
or flow skills in their pipeline-agent capacity — only reads them as data sources.

#### Prerequisites

None. DrawDown can be implemented immediately as a standalone project. The only input is the
current state of pipeline artifacts, which already exist.

#### Success Criteria

- Operator can visually edit process diagrams and save back to markdown
- An agent can add a node to a diagram by appending text to the `.md` file
- Diagrams survive a pipeline version change via the sync protocol
- Pipeline agent behavior is unchanged (no new context load, no new triggers)

#### Full Architecture Brief

`support/v1.10/diagram-app-architecture-brief.md` — contains: complete MD format spec with
examples, directory structure, frontend requirements, agent integration protocol, sync
protocol, config.yaml spec, initial diagram set with source mappings, and future extensions.

---

### WFC-001: Lightweight Workflow Controller Agent
**Date:** 2026-03-21
**Classification:** IDEA — not yet validated by failure. Requires 5+ feature sessions of data collection before implementation.
**Source:** Pipeline review session (external reviewer + operator discussion)
**Scope:** Cross-project (root protocol change)

#### Problem

The operator currently performs two cognitively different jobs:
1. **Strategic reasoning** — priority decisions, feature rationale challenges, risk assessment, spec review
2. **Mechanical routing** — checking field presence in artifacts, deciding "does this need QA?", updating tasks.jsonl, verifying session summaries exist, enforcing gate conditions, preparing next handoff

Job #2 is procedural, not creative. It follows a checklist. It doesn't require the context or reasoning capability of a heavy model. But it currently either falls on the operator (manual overhead) or on the Orchestrator/Architect (context window inflation).

This is the same problem that caused Orchestrator overload in v1.5-1.7: technical judgment responsibilities accumulated on the routing layer because routing was the easiest place to add a check.

#### Proposed Solution

A lightweight agent (Haiku-class) that executes a rigid procedure document. It sits between the operator and the reasoning agents, handling all mechanical workflow steps:

```
Operator (Brach)
  │
  ▼
CONTROLLER (lightweight, procedural, Haiku)
  │
  ├── Pre-dispatch: artifact completeness, gate checks, field validation
  ├── Routing: which agent next, based on tags and procedure rules
  ├── Post-session: artifact existence, required field presence, flag detection
  ├── State updates: tasks.jsonl, run records, state snapshot
  └── Git hygiene: stage + commit session changes
  │
  ▼
Reasoning Agents (Architect, Developer, Researcher — Sonnet/Opus)
```

#### Key Design Principles

1. **The controller does NOT reason.** It follows a procedure. It checks boxes and routes. If a decision requires judgment (ambiguous scope, unclear priority, conflicting signals), it escalates to the operator or invokes the Architect.

2. **The procedure document is the key artifact.** It defines every step the controller takes, every gate it checks, every routing rule it applies. It's versioned and iterable — the operator tweaks the procedure, not the agent.

3. **Complementary strengths, not model replacement.** Heavy models (Sonnet/Opus) do the creative/analytical work. The controller does the mechanical work. Neither does the other's job.

4. **Cheap and fast.** Haiku tokens are ~20x cheaper than Opus. The controller runs between every interaction without adding noticeable cost or latency.

#### Procedure Document Structure (Draft)

The controller would execute three procedures:

**Pre-Dispatch Procedure:**
1. Check handoff packet completeness (all required sections present per template)
2. Check Dispatch Readiness Gate (6 criteria from §3.1)
3. If task has `Interface Scope` tag → verify Field Preservation Checklist is loaded
4. If task has FE components → verify State Behavior section exists and has no `[ASK OPERATOR]`
5. If any open questions → STOP, surface to operator
6. If all pass → dispatch to target agent

**Post-Session Procedure:**
1. Verify session summary file exists at expected output path
2. Verify required fields are non-empty (Status, Work Performed, Files Changed, Decisions Made)
3. Scan for `[INTERFACE IMPACT]`, `[BLOCKED]`, `[SCOPE VIOLATION]` flags
4. If Developer session → route to Validator
5. If Validator PASS + task tagged `QA-REQUIRED` → route to QA
6. If Validator FAIL (attempt < 3) → prepare retry handoff with remediation steps
7. If Validator FAIL (attempt >= 3) → log incident, escalate to operator
8. Update `.agent/tasks.jsonl` with session outcome
9. Git add session-changed files + git commit with `[TASK-ID]: [objective]`

**Between-Session Procedure:**
1. Read latest session output (verdict for Developer sessions, summary for others)
2. Cross-reference against preceding session's flags (the pre-dispatch cross-reference check)
3. Apply routing rules from task quality tags
4. If next step requires operator decision → surface with specific question
5. If next step is mechanical → prepare handoff and present to operator for approval
6. Update state snapshot

#### What This Replaces

| Currently done by | Would move to controller |
|---|---|
| Operator: manually checking artifact completeness | Pre-dispatch procedure step 1-2 |
| Operator: deciding "does this need QA?" | Post-session procedure step 5 (reads Architect's tag) |
| Operator: updating tasks.jsonl | Post-session procedure step 8 |
| Operator: git add + commit after sessions | Post-session procedure step 9 |
| Operator: checking for flag propagation between sessions | Between-session procedure step 2 |
| Orchestrator: reading and routing based on session summaries | Between-session procedure steps 1-5 |
| Validator: checking session summary field completeness | Post-session procedure step 2 |

#### What This Does NOT Replace

- Operator strategic decisions (priority, scope, feature rationale)
- Architect reasoning (task decomposition, risk assessment, spec design)
- Developer implementation work
- Researcher investigation
- Any creative or analytical judgment

#### Relationship to Existing v1.9.2 Architecture

The controller fits the v1.9.2 specialization model:
- It is NOT a new standing role (violates §1.3 "default to smallest change")
- It IS a new workflow phase — a procedural layer between dispatch and execution
- It could be implemented as a skill (`.claude/skills/workflow-controller/`) loaded into a Haiku session
- The procedure document is the skill file; the controller is just the runner

This aligns with the v1.9 principle: "specialist behavior via skills, not standing roles."

#### Prerequisites Before Implementation

1. **Data collection (5+ feature sessions):** Run the current v1.9.2 pipeline. Keep a tally of every time the operator performs mechanical routing work. Record: what step, how long, what could have caught it automatically. This becomes the controller's procedure document.

2. **Identify gate failure patterns:** Which gates do agents actually hit? Which do they skip? Where does the operator catch things the protocol missed? This tells you which procedure steps are load-bearing vs. ceremony.

3. **Baseline metrics:** The telemetry files (runs.jsonl, incidents.jsonl) need real data. The controller's value is measurable: operator-minutes-per-task should decrease. Without a baseline, you can't prove it helped.

4. **Haiku capability validation:** Test whether Haiku can reliably execute a 50-line procedure document with file reads, pattern matching, and conditional routing. If it can't, Sonnet is the fallback (more expensive but still cheaper than Opus for procedural work).

#### Success Criteria

- Operator minutes per task decreases by >30%
- Zero increase in escaped defects (controller doesn't miss flags that operator would have caught)
- Artifact completeness rate increases (fewer dropped fields, fewer missing summaries)
- No increase in total token cost per task (Haiku savings offset by additional session)

#### Risks

- **Procedure document maintenance:** The procedure is another artifact to keep current. If it drifts from the actual protocol, the controller enforces stale rules.
- **False confidence:** Operator may stop checking things the controller "should" catch. If the controller misses something, the error goes undetected longer.
- **Complexity budget:** Adding a layer between operator and agents adds a layer. The net complexity must be lower, not higher.

#### Decision Gate

After 5 feature sessions of data collection:
- If operator spends >20% of session time on mechanical routing → implement
- If operator spends <10% → defer indefinitely (the overhead isn't worth automating)
- If 10-20% → evaluate whether the specific steps are automatable by Haiku

---

## Deferred

<!-- Format: [reviewed vX.Y] [TYPE] Description → Why deferred -->

- [reviewed v1.9] [IDEA] User Advocate role: a dedicated end-user-perspective evaluator distinct from Validator or Feature Review. (from: DjTools/scue) → Superseded by v1.9. Roles are eliminated in favor of skills. If user-advocate behavior is needed, create a skill or eval case, not a role.

- [reviewed v1.7] [FRICTION] Guided question scripts for session consistency. (from: DjTools/scue) → Deferred. Useful, but not yet backed by enough cross-project evidence to justify new shared templates at the root level.

- [reviewed v1.7] [GAP] No git commit step in Developer end-of-session checklist. (from: DjTools/scue 1.6.1) → Deferred. v1.7 intentionally chose reviewable task-scoped diffs over a root-mandated commit policy. Commit rules should stay project-specific unless repeated failures show a universal need.

- [reviewed v1.7] [GAP] QA Tester missing Zustand injection guidance, WebSocket interference guidance, QA brief fixture shapes, `preview_inspect` staleness notes, `preview_eval` IIFE guidance, and QA brief environment requirements. (from: DjTools/scue 1.6.1) → Deferred. These are high-value, but they are tightly coupled to a specific frontend stack and QA toolchain. They belong in project QA docs first, then can be promoted if they recur elsewhere.

- [reviewed v1.7] [IDEA] Spec format should include a DOM-queryable QA checklist. (from: DjTools/scue 1.6.1) → Deferred. Promising, but it introduces a new spec artifact contract. Needs more evidence across projects before being made mandatory.

- [reviewed v1.7] [IDEA] Structured entry IDs for protocol improvement records. (from: DjTools/scue 1.6.1) → Deferred. The entry volume is not yet high enough to justify the overhead.

- [reviewed v1.7] [IDEA] `[SKIP CONFIRM GATE]` operator signal. (from: DjTools/scue 1.6.1) → Deferred. This reduces friction, but it weakens a safety rail and should be tested project-locally before entering the root protocol.

---

## Resolved

<!-- Format: [vX.Y] [TYPE] [description] → [what changed] -->

- [v1.9.2] [GAP] No formal pipeline step between research findings and feature work — brainstorming applications of research happened ad-hoc in conversation with no structured output or triage mechanism. (from: SCUE Pro DJ Link research → brainstorm pattern) → Created portfolio-level brainstorm skill (`skills/brainstorm/SKILL.md`): research→candidates transformer producing JSONL output at `{project}/.agent/brainstorm/{slug}.jsonl`. Operator triages ideas before promotion to task tracker. Added trigger table entry and flow routing row to constitution. Added eval case (`brainstorm-output-valid.eval.md`).

- [v1.9] [PI-2025-001] Multi-agent overhead exceeds value for solo sequential work. 13 standing agent roles with per-session preamble loading consumed ~20% of context window before work began. (from: Google-MIT preprint Dec 2025, Anthropic agent architecture guide, Codified Context paper arXiv:2602.20478) → Collapsed to one default operator agent. Converted domain-specific knowledge to on-demand skills with progressive disclosure. Standing roles eliminated; specialist behavior invoked via skill triggers in CLAUDE.md trigger table.

- [v1.9] [PI-2025-002] Flat markdown state causes session artifact sprawl. 23 session artifacts for 3 milestones with no structured queryability. (from: Steve Yegge "Introducing Beads" Oct 2025, Codified Context paper, LangGraph memory model) → Replaced markdown session artifacts with structured task state (`.agent/tasks.jsonl`). Implemented "land the plane" session-end protocol. Raw session transcripts are disposable.

- [v1.9] [PI-2025-003] Handoff contracts drift without schema validation. 12 handoff templates existed as markdown with no runtime validation. (from: Anthropic tool use JSON Schema, OpenAI Structured Outputs, skywork.ai multi-agent orchestration) → Defined ONE handoff envelope as JSON Schema (`.agent/schemas/handoff-envelope.json`). Validation script at `scripts/validate-handoff.sh`. Malformed handoffs rejected before delivery.

- [v1.9] [PI-2025-004] Documentation should be tiered, not flat. All 591 files existed at the same access level. (from: Codified Context arXiv:2602.20478, Anthropic Skills spec, Microsoft Agent Skills spec, HumanLayer CLAUDE.md guide) → Implemented three-tier architecture: Hot (CLAUDE.md ≤200 lines, loaded every session), Warm (skills with progressive disclosure, ~100 tokens advertised, full SKILL.md on trigger), Cold (architecture specs, ADRs, research, retrieved on demand).

- [v1.9] [PI-2025-005] Evals prevent drift better than more documentation. Preamble rules had no verification mechanism. (from: Anthropic evals guide Jan 2026, Anthropic context engineering best practices) → Created eval scaffold at `.agent/evals/` with convention, handoff, and skill trigger eval cases. Every repeated agent failure becomes a test case before it becomes a rule. Runner script at `.agent/evals/run-evals.sh`.

- [v1.9] [PI-2025-006] Decision records should live near execution. Architecture decisions in centralized folders degraded into stale artifacts. (from: e-ADR project, C4 model, MADR streamlined templates) → ADRs warranted only when: decision affects >1 project, changes shared interface, or >1 day to reverse. ADRs live in the repo they affect, not centrally.

- [v1.9] [GAP] No structured event log for pipeline activity. Pipeline state reconstructed from file timestamps and scattered session summaries. (from: v1.8 pending) → Resolved by structured task tracker (`.agent/tasks.jsonl`) which provides queryable task state per project.

- [v1.9] [BUG] Root master templates use blockquote metadata instead of YAML frontmatter. (from: v1.8 pending) → Root templates retained as canonical artifact schemas. Frontmatter enforcement is now an eval case, not just a prose rule.

- [v1.9] [FRICTION] Agent dispatch requires manual copy-paste of startup prompts. (from: v1.8 pending) → Eliminated by removing startup prompts entirely. Skills are loaded on demand via trigger table. No manual dispatch needed.

- [v1.8] [GAP] Artifact metadata header uses blockquote format, not machine-parseable. (§2.0, all templates) → Switched all artifact metadata to YAML frontmatter (`---\nstatus: DRAFT\n---`). Updated §2.0 with two-tier metadata (full 5-field for planning artifacts, slim 2-field for session summaries/verdicts). Updated all root templates. Added frontmatter-only rule to §2.0.

- [v1.8] [BUG] Session summary overloaded with compliance metadata (routing, self-assessment, exit checklist, supersession tracking) that producing agents routinely skip. (§2.2, §6.1, §6.3, templates) → Split session summary responsibilities into three layers: producer owns factual recap (slimmed to 12 fields), Validator owns compliance interpretation (new §§ Compliance Check, Supersession, expanded Recommended Next Step with dispatch mode), hook owns existence gate. Simplified universal exit sequence to 3 steps. Added Orchestrator reading priority (verdict first, summary second for Developer sessions).

- [v1.8] [BUG] Data fields silently dropped when a single Developer session modifies both producer and consumer sides of a contract boundary. (§2.6, §6.3) → Added Interface Scope task tag (CONTRACT_ONLY | PRODUCER | CONSUMER | END_TO_END | NONE) to task breakdown schema. Added Interface Scope Decomposition rules to Architect preamble: contract-touching work must be split into CONTRACT_ONLY → PRODUCER/CONSUMER tasks. Added §2.11 Field Inventory schema for contract documentation. Added contract integrity skill file guidance to IMPLEMENTATION_PROMPT.md.

- [v1.7] [IDEA] Orchestrator context budget self-assessment for dispatch routing. (from: DjTools/scue session 9) → Added explicit Orchestrator self-assessment language: if it cannot confidently produce the next handoff from on-disk artifacts without leaning on conversational memory, it must recommend a fresh Orchestrator session or operator direct-dispatch.

- [v1.7] [GAP] No protocol for Designer revision passes, and no atomization check for Designer-output-driven tasks. (from: DjTools/scue session 9) → Added revision-pass gates after operator decisions on Architect and Designer artifacts, plus a re-run of the atomization test after design output or failed validation/QA materially changes the remaining work.

- [v1.7] [FRICTION] Architect session artifacts were easy to omit, and follow-up items were not promoted into tracked backlog. (from: DjTools/scue session 9) → Added an Architect session completion checklist, `## Follow-Up Items` to the session summary schema, Orchestrator follow-up promotion rules, and `## Follow-Up Backlog` in the state snapshot.

- [v1.7] [BUG] Developer skipped session summary, Architect skipped required artifacts, and there was no mandatory agent exit protocol. (from: DjTools/scue 1.6.1) → Added a universal exit sequence to `COMMON_RULES.md`, expanded the Session Summary schema with routing, exit checklist, follow-up items, and self-assessment, and required role-specific completion checklists where needed.

- [v1.7] [BUG] Orchestrator asserted work state without reading session artifacts first. (from: DjTools/scue 1.6.1) → Added a strict Read-Before-Assert rule to the Orchestrator preamble and reinforced dispatch/readiness gates around artifact-backed state claims.

- [v1.7] [BUG] Superseded artifacts were not marked, and artifact status had to be inferred. (from: DjTools/scue 1.6.1) → Added required durable-artifact metadata (`Status`, `Revision Of`, `Supersedes`, `Superseded By`) and explicit supersession rules across the protocol and master templates.

- [v1.7] [GAP] Handoff packets were missing `project_root`, parallel interface contracts, verified paths, and canonical artifact path patterns. (from: DjTools/scue 1.6.1) → Expanded the Handoff Packet schema with project root, working directory, exact output path, interface-contract sections, and added canonical artifact-path rules plus an Orchestrator dispatch-readiness checklist.

- [v1.7] [GAP] Protocol Enforcer did not produce a task-scoped kickstart prompt after bootstrap. (from: DjTools/scue 1.6.1 — CRUCIBLE bootstrap) → Updated the protocol and Enforcer prompt so bootstrap now includes `docs/agents/startup-prompts/kickstart.md` for the first expected invocation.

- [v1.7] [GAP] No interface contract file in project scaffold. (from: DjTools/scue 1.6.1) → Added `docs/interfaces.md` to the canonical project structure and required Architect/Developer interface-discipline rules to reference it directly.

- [v1.7] [BUG] Orchestrator state did not reconcile direct-dispatched work and had no active-session tracking. (from: DjTools/scue 1.6.1) → Expanded the Orchestrator State Snapshot with `## Active Sessions`, `## Dispatch Reconciliation`, and routing rules that force direct-dispatch reconciliation back into tracked state.

- [v1.7] [GAP] Validator PASS gave no explicit QA handoff signal, and combined validation could become too large. (from: DjTools/scue 1.6.1) → Added `## Recommended Next Step` to the Validator Verdict schema and extended the atomization test to Validator and QA dispatch so oversized review work must be split.

- [v1.7] [FRICTION] Read-before-write gate on protocol improvement logging was undocumented. (from: DjTools/scue 1.6.1) → Added an operational note to the protocol-improvement workflow: always read the improvements log before attempting an edit, even for append-only writes.

- [v1.6] [FRICTION] Orchestrator role overload — technical judgment responsibilities (FE State Behavior Check, Designer invocation thresholds, Interface Contract Discipline, QA dispatch decisions) accumulated on the Orchestrator, inflating context requirements to ~60K tokens. (from: DjTools/scue pipeline review) → Redistributed technical judgment to Architect. Architect now tags tasks with `QA Required`, `State Behavior`, `[REQUIRES DESIGNER]`, and interface contract ACs during task breakdown. Orchestrator trusts these tags. Updated §6.3, ORCHESTRATOR.md, ARCHITECT.md, templates/tasks.md.

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
