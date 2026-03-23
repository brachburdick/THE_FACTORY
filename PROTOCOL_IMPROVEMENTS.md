# Protocol Improvements Log

> **How to use:** When you notice something during a session — an agent forgot a step,
> a template is missing a field, a workflow has a gap — add a one-liner here.
> Don't fix the protocol in the moment. Just capture the observation.
> Periodically, run a Protocol Review session to batch-process these into protocol changes.
>
> **v2.0 cleanup (2026-03-23):** 35+ items resolved or moved to project observations.
> Resolution history is in git (`git log --oneline -- PROTOCOL_IMPROVEMENTS.md`).

---

## Pending

<!-- Format: [TYPE] (Bx) Description. (from: source, date) -->
<!-- Types: BUG | GAP | FRICTION | IDEA -->
<!-- B-codes: B1=wasted effort, B2=missing context, B3=process friction, B4=reasoning failure, B5=communication, B6=root cause link -->
<!-- PROJECT-level observations (A-codes) belong in {project}/.agent/project-observations.md -->

### Deferred — needs design (revisit at v2.1)

- [IDEA] Lightweight workflow controller agent. Proposal: `support/proposals/WFC-001-workflow-controller.md`. v2.0 hooks handle most mechanical tasks — re-evaluate scope after 20 sessions.

- [IDEA] **DrawDown:** Visual process diagram editor backed by markdown files. Proposal: `support/proposals/DD-001-drawdown.md`.

- [FRICTION] (B3) Context checkpointing: interrupted tasks lose pre-loaded read state. `state-snapshot` tracks branch/files but not "which files were read and what decisions were made." Full solution likely requires a Claude Code feature, not custom infra.

- [GAP] (B4) Separate-context verification checks structural correctness but can miss runtime bugs across input variants. Behavioral contract checks (does method X work for ALL input variants?) need per-project eval cases, not a generic protocol rule.

- [GAP] (B3) Hardware-dependent bugs: debug-flow assumes software-only reproduction. No guidance for when QA discovers a bug requiring live hardware to reproduce.

- [FRICTION] (B1) Deep research tasks reinvent agent decomposition and question structure each time. A reusable "deep library investigation" skill would reduce 150-line research prompts to a template invocation.

- [GAP] (B4) Research findings that invalidate existing ADRs have no formal propagation mechanism. ADR superseded banner convention added to SCUE CLAUDE.md but no automated cross-reference check exists.

- [GAP] (B4) API references in specs/handoffs are sourced from web reads, not the actual JAR/package on disk. No verification step confirms they compile against the actual dependency version.

### Active — project-specific (not blocking v2)

- [GAP] (B4) CRUCIBLE: task verification gates — typecheck passed but dispatched agent couldn't receive its task. No gate between "files exist" and "task works end-to-end."

- [FRICTION] (B3) CRUCIBLE: nested git repo under `/projects/` — root `.gitignore` excludes it. Documented nowhere.

- [FRICTION] (B3) CRUCIBLE: integration tests require live API keys with no mock/stub fallback.

- [GAP] (B2) Platform resilience (OS sleep, App Nap, USB power management) — class of bug invisible to code review. Captured as SCUE project observations; no generic protocol rule warranted yet.

- [FRICTION] (B3) Memory bootstrap files referenced in system context may not exist at session start. Should degrade gracefully.

- [FRICTION] (B1) ALS XML schema undocumented + Live 12 changed element names. Research findings saved in `projects/enable/als-reader/docs/` but pattern will recur for any format-version divergence.

- [FRICTION] (B3) als-reader MCP server coupling: CLI summary path crashes without `fastmcp` installed. No test covers optional-dependency-missing path.

---

## Deferred

- [reviewed v2.0] [IDEA] User Advocate role → Superseded by skills model. Create a skill or eval case if needed.

- [reviewed v2.0] [FRICTION] Guided question scripts for session consistency → Not yet backed by enough cross-project evidence.

- [reviewed v2.0] [FRICTION] Git merge ceremony → Mechanical overhead but low-frequency. Revisit if it becomes a recurring friction point.
