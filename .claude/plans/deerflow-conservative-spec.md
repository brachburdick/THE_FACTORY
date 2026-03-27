---
status: DRAFT
project_root: /Users/brach/Documents/THE_FACTORY
revision_of: none
supersedes: none
superseded_by: none
pdr_ref: none
evidence_ref: support/research/deerflow-analysis-claude.md, support/research/deerflow-analysis-gpt.md
---

# Spec: DeerFlow-Inspired Conservative Improvements

## Frozen Intent

### Problem Statement
DeerFlow 2.0 (ByteDance, Feb 2026) demonstrates several architectural patterns —
ordered middleware pipelines, skill manifests, sub-agent concurrency caps,
context summarization, and portable skill archives — that would strengthen
THE_FACTORY without requiring ecosystem migration or new dependencies.

### Target Users
Operator (Brach) and the Claude Code agent sessions running inside THE_FACTORY.

### Desired Outcome
Five targeted improvements adopted from DeerFlow's design, implemented entirely
within the existing hook/skill/eval infrastructure. No Python/LangChain
dependency. No runtime changes. Measurable via existing eval suite.

### Non-Goals
- Adopting DeerFlow as a runtime or dependency
- Docker sandbox integration (see Moderate spec, below)
- Replacing the memory system
- Migrating to LangGraph or LangChain
- Changing the single-writer model

### Hard Constraints
- All 98+ existing evals must continue to pass
- No new runtime dependencies (no pip/npm additions)
- Hooks remain shell scripts or Python using only stdlib
- Changes must be backward-compatible with existing task queue and run records

### Quality Priorities
1. Correctness (no regressions)
2. Simplicity (minimal new files)
3. Performance (no added latency to hook pipeline)

## Mutable Specification

### Summary
Five improvements cherry-picked from DeerFlow's architecture, implemented as
enhancements to existing THE_FACTORY infrastructure: a hook pipeline manifest,
a skill index manifest, a sub-agent concurrency advisory, a context
summarization skill, and a portable `.skill` archive spec.

### Improvement 1: Hook Pipeline Manifest

**Problem:** Hooks are wired in `settings.json` as flat arrays per tool matcher.
Execution order is implicit (array position). There's no single view of the
full pipeline, no declared lifecycle phases, and no way to reason about
hook ordering without reading the JSON.

**DeerFlow pattern:** 11 numbered middleware stages with named lifecycle hooks
(`before_agent`, `before_model`, `after_model`, `wrap_model_call`).

**Implementation:**
Create `docs/hook-pipeline.md` — a declared, ordered manifest of all hooks
with their phase, matcher, type (blocking/advisory), and purpose.

```markdown
# Hook Pipeline

## PreToolUse Phase

| Order | Hook | Matcher | Type | Purpose |
|-------|------|---------|------|---------|
| 1 | git-guard.sh | Bash | Blocking | No commits to main, no force-push |
| 2 | fix-attempt-tracker.sh | Bash, Edit, Write | Blocking | 2-cap + compound budget |
| 3 | bash-risk-logger.sh | Bash | Advisory | Heuristic risk classification |
| 4 | prompt risk classifier | Bash | Blocking | LLM-based command risk gating |
| 5 | reference-check.sh | Edit | Advisory | Warns on rename→eval conflicts |
| 6 | risk-classifier.sh | Edit, Write | Blocking | Task risk level enforcement |
| 7 | blast-radius.sh | Edit, Write | Blocking | Scope check vs owned_paths |
| 8 | plan-gate.sh | Edit, Write | Blocking | Requires plan for high-risk |
| 9 | build-integrity.sh | Edit, Write | Advisory | Warns on infra file edits |

## PostToolUse Phase

| Order | Hook | Matcher | Type | Purpose |
|-------|------|---------|------|---------|
| 1 | mid-session-snapshot.py | Edit, Write | Passive | Snapshot every 15 mutations |
| 2 | read-state-logger.py | Read | Passive | Log file reads for cache |

## Stop Phase

| Order | Hook | Matcher | Type | Purpose |
|-------|------|---------|------|---------|
| 1 | langfuse-trace.py | * | Passive | Session metrics to Langfuse |
| 2 | audit-run-record.sh | * | Advisory | Warns if no run record |

## SessionEnd Phase

| Order | Hook | Matcher | Type | Purpose |
|-------|------|---------|------|---------|
| 1 | state-snapshot.py | * | Passive | Full state snapshot |
```

**Acceptance criteria:**
- Document exists and matches actual `settings.json` wiring
- Eval added: `test_hook_pipeline_manifest_matches_settings` — parses both
  files and asserts every hook in settings.json appears in the manifest

### Improvement 2: Skill Index Manifest

**Problem:** Skills are discovered by scanning directories and reading SKILL.md
frontmatter. There's no single index. The trigger table in CLAUDE.md is
manually maintained and can drift from actual skill files.

**DeerFlow pattern:** `extensions_config.json` with enabled/disabled state per
skill, path references only in system prompt, content loaded on-demand.

**Implementation:**
Create `skills/index.json` — auto-generated manifest of all skills.

```json
[
  {
    "name": "handoff",
    "path": "skills/handoff/SKILL.md",
    "description": "Use when handing off work across a genuine domain boundary",
    "triggers": ["handoff", "domain boundary", "cross-layer"],
    "scope": "pipeline"
  },
  {
    "name": "debug-flow",
    "path": ".claude/skills/debug-flow/SKILL.md",
    "description": "Fix, bug, error, broken, regression, failing",
    "triggers": ["fix", "bug", "error", "broken", "regression", "failing"],
    "scope": "pipeline"
  }
]
```

Add `scripts/build-skill-index.py` (~40 lines) that:
1. Globs `skills/**/SKILL.md` and `.claude/skills/**/SKILL.md`
2. Parses YAML frontmatter for `name` and `description`
3. Extracts trigger words from description
4. Writes `skills/index.json`

**Acceptance criteria:**
- `skills/index.json` exists and is valid JSON
- Every SKILL.md file in the repo has an entry in the index
- Eval added: `test_skill_index_covers_all_skills` — globs for SKILL.md,
  asserts each appears in `skills/index.json`

### Improvement 3: Sub-Agent Concurrency Advisory

**Problem:** No guidance on how many sub-agents (Agent tool calls) should run
concurrently. The single-writer model prevents edit conflicts, but parallel
read-only agents can still exhaust context or cause confusion.

**DeerFlow pattern:** `SubagentLimitMiddleware` caps concurrent `task` calls
at 3 (clamped to [2,4]).

**Implementation:**
Add guidance to CLAUDE.md under "Critical Reminders":

```markdown
- **Sub-agent concurrency cap.** Limit concurrent Agent tool calls to 3.
  Read-only agents (Explore, Plan) may run in parallel. Agents that produce
  artifacts should run sequentially to avoid merge conflicts in handoffs.
```

No hook enforcement — this is advisory for now. The prompt-hook system
(tf-089) could later enforce it if violations are observed.

**Acceptance criteria:**
- CLAUDE.md contains the concurrency guidance
- Eval added: `test_subagent_concurrency_guidance_exists` — greps CLAUDE.md
  for concurrency cap language

### Improvement 4: Context Summarization Skill

**Problem:** The context gate (turn 40 → end session) is binary. There's no
intermediate step to compress completed sub-task outputs before they
accumulate to the point of degradation.

**DeerFlow pattern:** `SummarizationMiddleware` triggers near token limits,
compresses completed sub-task results and older conversation history.

**Implementation:**
Create `skills/context-checkpoint/SKILL.md`:

```yaml
---
name: context-checkpoint
description: Use at natural task boundaries (after completing a sub-task,
  before starting a new phase) to compress context. Summarize completed
  work into a state snapshot and offload details to files.
---
```

The skill body instructs the agent to:
1. Write a summary of completed work to `.agent/context-checkpoints/{task-id}-{n}.md`
2. Update `state-snapshot.json` with the checkpoint reference
3. Continue with compressed context

Add to CLAUDE.md trigger table:

```markdown
| Context feels heavy / turn > 25 | `skills/context-checkpoint/SKILL.md` | Compress before degradation |
```

**Acceptance criteria:**
- Skill file exists with valid frontmatter
- Listed in trigger table
- Listed in `skills/index.json` (from Improvement 2)

### Improvement 5: Portable Skill Archive Spec

**Problem:** Skills are directory trees inside the repo. No standard format
for packaging, sharing, or installing skills across projects.

**DeerFlow pattern:** `.skill` archive — ZIP containing directory with
SKILL.md plus optional scripts and resources. `POST /api/skills/install`
extracts and registers.

**Implementation:**
Create `docs/skill-archive-spec.md` documenting the `.skill` format:

```markdown
# .skill Archive Format

A `.skill` file is a ZIP archive containing:

├── SKILL.md          # Required. YAML frontmatter + Markdown body.
├── scripts/          # Optional. Helper scripts referenced by SKILL.md.
├── templates/        # Optional. File templates used by the skill.
├── evals/            # Optional. Eval specs for the skill.
└── manifest.json     # Optional. Metadata: version, author, compatibility.

## Install
unzip foo.skill -d skills/custom/foo/

## manifest.json schema
{
  "name": "string (required)",
  "version": "semver (required)",
  "author": "string (optional)",
  "compatibility": "THE_FACTORY >=3.0 (optional)",
  "triggers": ["array", "of", "trigger", "words"]
}
```

Add `scripts/pack-skill.sh` (~20 lines): takes a skill directory, validates
SKILL.md exists, zips it as `{name}.skill`.

Add `scripts/install-skill.sh` (~15 lines): takes a `.skill` file, extracts
to `skills/custom/{name}/`, rebuilds `skills/index.json`.

**Acceptance criteria:**
- Spec document exists
- `pack-skill.sh` produces a valid ZIP from an existing skill directory
- `install-skill.sh` extracts and the skill appears in `skills/index.json`

---

## Task Breakdown

| ID | Title | Risk | Blocked By | Est. |
|----|-------|------|------------|------|
| tf-095 | Hook pipeline manifest doc + eval | low | — | 1 session |
| tf-096 | Skill index manifest + build script + eval | low | — | 1 session |
| tf-097 | Sub-agent concurrency advisory in CLAUDE.md + eval | low | — | < 1 session |
| tf-098 | Context summarization skill + trigger table entry | low | — | 1 session |
| tf-099 | Portable skill archive spec + pack/install scripts | low | tf-096 | 1 session |

All tasks are low-risk / routine tier per the oversight matrix.

---

## Future: Moderate Spec (DeerFlow as Execution Backend)

> **Not for implementation now.** Captured here so the idea doesn't get lost.

### Concept
Run DeerFlow as a local Docker service. Write a Python bridge
(`scripts/deerflow-dispatch.py`) wrapping `DeerFlowClient`. Add a
`sandbox-exec` tool to THE_FACTORY that delegates isolated code execution
tasks to DeerFlow while keeping all oversight hooks on our side.

### Architecture

```
THE_FACTORY (orchestration + oversight)
  │
  ├── hooks (risk, blast radius, fix-attempt, plan-gate)
  ├── eval suite (98+ tests)
  ├── memory (categorized, frontmatter-based)
  │
  └── scripts/deerflow-dispatch.py
        │
        ▼
    DeerFlow (Docker, port 2026)
        ├── Sandbox execution (Docker isolation per task)
        ├── Sub-agent parallel dispatch
        └── Filesystem-based collaboration
```

### Key Design Decisions
- **Handoff envelope → DeerFlow task:** Bridge script converts JSON Schema
  envelope to `DeerFlowClient.chat()` params, validates response against
  schema on return.
- **Memory stays ours:** DeerFlow's flat JSON with string dedup is a downgrade
  from our categorized system.
- **Oversight stays ours:** DeerFlow has zero enforcement infrastructure.
  Our hooks run before/after the bridge call.
- **Eval stays ours:** DeerFlow ships no evaluation. CRUCIBLE continues as
  the eval harness. DeerFlow is just an execution backend.

### Prerequisites
- Docker installed and running
- DeerFlow stable release (currently v2.0, 1 month old — monitor stability)
- Python 3.10+ for `DeerFlowClient`
- Pilot task identified (candidate: SCUE code generation or data pipeline)

### Risks
- LangChain dependency chain is heavy and breaks often
- DeerFlow is 1 month old — API may change
- Docker overhead for simple tasks may not justify the isolation benefit
- Adds a Python runtime dependency to a pipeline that currently avoids it

### When to Revisit
- When a task genuinely needs sandboxed code execution (not just file edits)
- When DeerFlow reaches v2.1+ and API stability is demonstrated
- When CRUCIBLE Phase 3 (RunEngine) is complete and could use a sandbox backend

---

## Open Questions
- None. All five conservative improvements are self-contained.

## Change Log
<!-- [DATE] [CHANGE] — caused by [source] -->
- 2026-03-27: Initial draft — caused by DeerFlow analysis documents (Claude + GPT)
