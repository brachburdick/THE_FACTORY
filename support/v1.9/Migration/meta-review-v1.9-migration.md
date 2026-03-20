# Meta-Infrastructure Migration: v1.8 → v1.9

## Preamble for Meta-Reviewer Agent

You are reviewing and upgrading the multi-agent development infrastructure used across a 12-project portfolio (federated GraphQL, Node.js/TypeScript, MongoDB, Redis, AWS). The current system (v1.8) was assessed by two independent reviewers and found to have significant overhead problems. This prompt contains their consolidated findings and explicit instructions for applying them.

**Current state (v1.8):**
- 1.4 MB of documentation infrastructure (591 markdown files)
- 13 agent roles with preambles, startup prompts, roster definitions, handoff contracts, and templates
- 23 session artifacts for 3 completed milestones (11 session files for a single 6-task feature)
- 7-line preambles copy-pasted into every session startup, containing rules already in CLAUDE.md
- 12 handoff templates with no schema validation
- Agents spend ~20% of context window loading infrastructure before doing any work

**Target state (v1.9):**
- One default operator agent for most work
- Specialist capabilities delivered as progressive-disclosure skills, not standing roles
- CLAUDE.md under 200 lines, functioning as constitution + trigger table
- One JSON Schema-validated handoff envelope
- Structured task state (JSONL/SQLite), not markdown session files
- Evals as the primary anti-drift mechanism
- Tiered memory: hot (always loaded) / warm (per-task) / cold (on-demand)

---

## Phase 1: Record Findings in PROTOCOL IMPROVEMENTS

Add the following entries to the PROTOCOL IMPROVEMENTS document, following the existing format. Each finding has a source trail and a concrete action.

### Finding PI-2025-001: Multi-Agent Overhead Exceeds Value for Solo Sequential Work

**Problem:** 13 standing agent roles with per-session preamble loading consumes ~20% of context window before work begins. A Google-MIT preprint (Dec 2025) found multi-agent setups often hurt performance on sequential reasoning and tool-heavy work, with diminishing or negative returns once a single-agent baseline is already moderately successful. Anthropic's own architecture guide says to start with single-purpose agents and reusable tools.

**Evidence:** 591 markdown files / 1.4 MB for a ~60% complete project. 11 session files generated for a single 6-task feature. Preambles contain rules already present in CLAUDE.md.

**Resolution:** Collapse to one default operator agent. Convert domain-specific knowledge to on-demand skills with progressive disclosure. Standing roles are eliminated; specialist behavior is invoked via skill triggers.

**Sources:** Google-MIT preprint (arXiv, Dec 2025), Anthropic agent architecture guide, Codified Context paper (arXiv:2602.20478, Feb 2026)

---

### Finding PI-2025-002: Flat Markdown State Causes Session Artifact Sprawl

**Problem:** Session artifacts accumulate as markdown files with no structured queryability. Agents cannot distinguish current decisions from stale brainstorms. Steve Yegge documented this exact failure mode: 605 markdown plan files in varying stages of decay, agents unable to build reliable work queues from prose.

**Evidence:** 23 session artifacts for 3 milestones. No structured query mechanism. No expiration or triage policy.

**Resolution:** Replace markdown session artifacts with structured task state (JSONL, SQLite, or Beads). Implement "land the plane" session-end protocol: promote decisions to hot-tier docs, file tasks into structured tracker, discard everything else by default. Raw session transcripts are disposable.

**Sources:** Steve Yegge, "Introducing Beads" (Medium, Oct 2025); Codified Context paper; LangGraph memory model (semantic/episodic/procedural separation)

---

### Finding PI-2025-003: Handoff Contracts Drift Without Schema Validation

**Problem:** 12 handoff templates exist as markdown with no runtime validation. Agents can and do deviate from template structure, causing silent contract drift that compounds across sessions.

**Evidence:** 12 unvalidated templates. No CI or runtime validation step. Reviewer noted agents can drift from templates with no enforcement.

**Resolution:** Define ONE handoff envelope as JSON Schema. Validate at runtime (hook or script). Reject malformed handoffs before the receiving agent sees them. Log validation failures for diagnostics.

**Handoff schema (reference implementation):**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["schemaVersion", "sourceAgent", "targetSkill", "summary", "artifacts", "taskRef"],
  "properties": {
    "schemaVersion": { "const": "1.0.0" },
    "sourceAgent": { "type": "string" },
    "targetSkill": { "type": "string" },
    "summary": { "type": "string", "maxLength": 500 },
    "artifacts": {
      "type": "array",
      "items": { "type": "string" }
    },
    "taskRef": { "type": "string", "description": "ID in structured task tracker" },
    "openQuestions": {
      "type": "array",
      "items": { "type": "string" }
    },
    "blockers": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "additionalProperties": false
}
```

**Sources:** Anthropic tool use (JSON Schema input_schema), OpenAI Structured Outputs (strict: true), multi-agent orchestration best practices (skywork.ai)

---

### Finding PI-2025-004: Documentation Should Be Tiered, Not Flat

**Problem:** All 591 files exist at the same access level. Agents either load too much (context bloat) or miss critical info (no routing). The Codified Context paper demonstrated that a 108K-line system built by a solo dev with 19 agents succeeds specifically because of hot/warm/cold memory separation.

**Evidence:** Preambles are 7 lines each but loaded into every session. CLAUDE.md contains rules that overlap with preamble content. No progressive disclosure.

**Resolution:** Implement three-tier architecture:
- **Tier 1 (Hot):** CLAUDE.md ≤200 lines. Conventions, build commands, trigger table. Loaded every session.
- **Tier 2 (Warm):** Skills with progressive disclosure. Name + description advertised at startup (~100 tokens each). Full SKILL.md loaded only when triggered. Reference docs loaded only during execution.
- **Tier 3 (Cold):** Architecture specs, subsystem docs, ADRs. Retrieved on demand via explicit reference in skills or agent request. Never auto-loaded.

**Sources:** Codified Context (arXiv:2602.20478), Anthropic Skills specification, Microsoft Agent Skills spec, HumanLayer CLAUDE.md guide

---

### Finding PI-2025-005: Evals Prevent Drift Better Than More Documentation

**Problem:** When agents violate a convention, the reflex is to add another rule to a doc. This grows the documentation surface without verifiably fixing the problem. Anthropic's evals guidance recommends executable test suites as the primary quality mechanism.

**Evidence:** Preambles contain trivial rules ("use dataclasses", "no print()") that exist because of past violations but have no verification mechanism.

**Resolution:** For every repeated agent failure: write an eval case BEFORE adding a doc rule. Eval suite tests both "should do X" and "should NOT do Y" behaviors. Run evals when prompts or skills change. A rule without a corresponding eval is an unverified hope.

**Sources:** Anthropic evals guide (Jan 9, 2026), Anthropic context engineering (skills best practices)

---

### Finding PI-2025-006: Decision Records Should Live Near Execution

**Problem:** Architecture decisions stored in centralized documentation folders degrade into stale artifacts that agents don't consult. The e-ADR project exists specifically because decision knowledge erodes when it lives away from where developers work.

**Evidence:** Inferred from current flat-file structure across 12 projects.

**Resolution:** ADRs warranted only when: decision affects >1 project, changes a shared interface, or would take >1 day to reverse. ADRs live in the repo they affect, not centrally. Use MADR lightweight template. Everything else is a commit message or task-tracker note.

**Sources:** e-ADR project, C4 model (container diagram for all teams, system landscape only for large orgs), MADR streamlined templates

---

## Phase 2: Apply to Meta-Infrastructure

Execute the following changes to the meta-level infrastructure (the system that governs how all projects are structured).

### 2.1 — Rewrite the Meta-CLAUDE.md

The meta-level CLAUDE.md (the one that governs the infrastructure itself, not individual projects) should be rewritten to ≤200 lines with this structure:

```markdown
# Meta-Infrastructure Constitution (v1.9)

## Core Principles
- One default operator agent. Specialist behavior via skills, not standing roles.
- Documentation earns its context window. If not loaded on demand, validated automatically,
  used by humans regularly, or recording an irreversible decision — delete it.
- Evals over docs. Every repeated failure becomes a test case before it becomes a rule.
- Structured state over prose. Task tracking in JSONL/SQLite, not markdown.
- Progressive disclosure. Advertise skill names at startup. Load full skill on trigger.
  Load references during execution. Never load everything.

## Trigger Table
| Task Pattern | Skill to Load | Notes |
|---|---|---|
| Audio analysis / beatgrid / rekordbox | audio-analysis-skill/ | Primary: Pioneer/Serato metadata |
| DMX / ArtNet / lighting / SCUE | dmx-lighting-skill/ | Includes ESP32, PCA9685 patterns |
| Frontend / React / TypeScript UI | frontend-skill/ | Project-specific component patterns |
| GraphQL federation / schema stitching | graphql-federation-skill/ | Cross-project gateway patterns |
| AWS / Lambda / infrastructure | aws-infra-skill/ | Includes EB→serverless migration notes |
| Handoff between domains | handoff-skill/ | Loads JSON Schema, runs validation |
| New project scaffolding | project-scaffold-skill/ | .agent/ structure, CLAUDE.md template |

## Session Protocol
- Start: Load this constitution. Read trigger table. Begin work.
- Mid-session: Load skills as needed. Do not preload.
- End ("Land the Plane"):
  1. Update structured task tracker with status of all touched tasks.
  2. If an architecture decision was made that meets ADR threshold, write ADR in affected repo.
  3. If a new failure pattern was observed, file it for eval creation.
  4. Discard session scratch. Do not create session artifact files.

## Handoff Protocol
- Handoffs use the v1.0.0 JSON Schema envelope (see handoff-skill/).
- Validate before delivery. Reject malformed handoffs.
- Handoffs are for genuine domain boundary crossings, not sequential tasks.

## What NOT To Do
- Do not create session artifact markdown files.
- Do not copy-paste preambles. Skills are loaded on demand.
- Do not add rules to this file without a corresponding eval case.
- Do not create a new agent role. Create a skill instead.
```

### 2.2 — Convert Agent Roles to Skills

For each of the 13 current agent roles:

1. **Audit:** Does this role represent a genuine domain boundary, or is it an organizational persona? If persona → delete. If domain → convert to skill.
2. **Extract:** Pull domain-specific knowledge (codebase facts, patterns, failure modes, API conventions) out of the preamble into a SKILL.md.
3. **Structure as progressive disclosure:**
   ```
   skill-name/
   ├── SKILL.md          # Frontmatter (name, description) + core instructions
   ├── references/       # Detailed specs, loaded only when needed
   │   ├── api-patterns.md
   │   └── known-failures.md
   └── scripts/          # Validation scripts, code generators
       └── validate-handoff.sh
   ```
4. **Write the description as a trigger, not a summary.** "Use when the task involves DMX output, ArtNet networking, ESP32 lighting control, or SCUE system configuration" — not "A skill for lighting."
5. **Delete the original preamble, startup prompt, and roster entry.**

Expected outcome: 13 roles → 5–7 skills (estimate; actual count depends on audit).

### 2.3 — Create the Structured Task Tracker

Replace session markdown artifacts with a structured system. Choose one:

**Option A: Beads** (recommended if comfortable with external tooling)
```bash
curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash
cd <project>
bd init
```
Add to CLAUDE.md: "Use `bd` for task tracking. Do not create markdown TODO/plan/session files."

**Option B: Minimal JSONL** (if you want to keep it simple and self-contained)
Create `.agent/tasks.jsonl` in each project root. Each line:
```json
{"id": "task-001", "status": "in-progress", "summary": "...", "blockers": [], "updated": "2026-03-20T00:00:00Z", "session": "optional-ref"}
```
Add a simple validation script and a query script (`tasks.sh ready`, `tasks.sh blocked`).

**Option C: SQLite** (if you want queryability without external deps)
Single `.agent/tasks.db` per project. Schema mirrors the JSONL fields. Query with `sqlite3` in hooks.

### 2.4 — Create the Eval Scaffold

Create a top-level eval structure:
```
.agent/evals/
├── conventions/        # Does the agent follow coding conventions?
│   ├── uses-dataclasses.eval.md
│   └── no-print-statements.eval.md
├── handoffs/           # Are handoff envelopes schema-valid?
│   └── handoff-schema-valid.eval.md
├── skills/             # Do skills trigger correctly?
│   └── dmx-skill-triggers-on-lighting-task.eval.md
└── run-evals.sh        # Runner script
```

Each `.eval.md` contains:
```markdown
# Eval: uses-dataclasses
## Should: Use dataclasses for all data containers
- Input: "Create a config object with fields: host, port, debug"
- Expected: Output contains `@dataclass` or `from dataclasses import`
- Fail if: Output uses plain dict, NamedTuple without justification, or raw class with __init__

## Should NOT: Use dataclasses for ORM models or Pydantic validators
- Input: "Create a MongoDB document model for User"
- Expected: Output uses project's ORM pattern, not dataclass
```

Migrate existing preamble rules into evals. For each rule currently in a preamble:
1. If the rule has been violated by agents → create an eval, keep the rule in the relevant skill.
2. If the rule has NOT been violated → create the eval anyway, delete the rule from the skill (the model already follows it; the eval catches regression).
3. If the rule is a restatement of something the model does by default → delete both.

### 2.5 — Implement the Keep/Delete Filter

Apply this filter to every file in the current .agent/ infrastructure:

```
KEEP if ANY of:
  ☐ Loaded on demand (part of a skill's progressive disclosure)
  ☐ Validated automatically (schema, eval, or CI check)
  ☐ Repeatedly used by a human (you actually open and reference this)
  ☐ Records an irreversible or cross-project decision (ADR-worthy)

DELETE if ANY of:
  ☐ Gets pasted into prompts verbatim (move content to skill or CLAUDE.md)
  ☐ Duplicates another source of truth
  ☐ Exists because an agent "might need it someday"
  ☐ Is a session artifact from a completed milestone
  ☐ Is a preamble, startup prompt, or roster entry for a role being converted to a skill
```

Track what you delete. The deletion list itself is useful data for the version comparison.

---

## Phase 3: Apply to Individual Projects

For each of the 12 projects in the portfolio:

### 3.1 — Project-Level CLAUDE.md Audit

Each project has (or should have) its own CLAUDE.md. Audit each one:

1. **Length check:** If >200 lines, it's too long. Identify what should be a skill, what should be an ADR, and what should be deleted.
2. **Duplication check:** Flag any content that also appears in the meta-level CLAUDE.md or in a preamble. Delete the duplicate — ancestor CLAUDE.md files load automatically.
3. **Trigger table:** Add project-specific skill triggers if the project has domain-specific skills beyond the portfolio-level ones.
4. **Gotchas section:** Review git history and past session artifacts for failure patterns specific to this project. Consolidate into a `## Gotchas` section (highest-signal content). Delete the source session files.

### 3.2 — Session Artifact Cleanup

For each project:
1. List all files in `.agent/sessions/` or equivalent directories.
2. For each file, extract any durable decisions, unresolved tasks, or failure patterns.
3. Durable decisions → ADR in the project repo (if they meet the threshold) or a one-liner in the project CLAUDE.md gotchas section.
4. Unresolved tasks → structured task tracker entry.
5. Failure patterns → eval case.
6. Delete the session file.

### 3.3 — Handoff Template Replacement

For each project:
1. Delete all markdown handoff templates.
2. Replace with a reference to the portfolio-level handoff JSON Schema (in handoff-skill/).
3. If the project has project-specific handoff fields, extend the schema with optional project-level properties — do NOT create a separate template.

### 3.4 — SCUE-Specific Migration Notes

SCUE (FastAPI/React/TypeScript/Python/Java) has the most complex agent infrastructure with a designed agent roster and inter-agent handoff contract system. Specific actions:

1. The SCUE agent roster should be replaced with SCUE-specific skills:
   - `scue-audio-analysis/` — beatgrid, rekordbox/Serato metadata, analysis pipeline
   - `scue-dmx-output/` — ArtNet, ESP32, fixture profiles, DMX512 protocol
   - `scue-frontend/` — React UI, parameter controls, visualization
   - `scue-fastapi-backend/` — API routes, WebSocket, session management
2. The SCUE inter-agent handoff contracts should be collapsed into the single portfolio-level handoff schema, with SCUE-specific optional fields if needed.
3. SCUE session artifacts from completed milestones should be triaged per 3.2.
4. If RAMIFY supersedes SCUE (per current planning notes), create an ADR documenting the relationship and any shared infrastructure.

---

## Phase 4: Version Control and Retrospective Scoring

### 4.1 — Archive v1.8

Before making any changes:

```bash
# Create a snapshot branch from current state
git checkout -b archive/meta-infra-v1.8
git add -A
git commit -m "Archive: meta-infrastructure v1.8 (pre-migration snapshot)

This snapshot preserves the complete state of the multi-agent infrastructure
before the v1.9 migration. Key characteristics:
- 591 markdown files, ~1.4 MB documentation
- 13 agent roles with preambles and startup prompts
- 12 handoff templates (unvalidated)
- Session artifact pattern (23 artifacts / 3 milestones)
- No progressive disclosure, no tiered memory, no evals

See: meta-review-v1.9-migration.md for findings that motivated the migration."

git tag v1.8-final -m "Final state of v1.8 meta-infrastructure"
git checkout main
```

### 4.2 — Create the Version Manifest

Create `.agent/VERSION.md` (or equivalent) in your meta-infrastructure root:

```markdown
# Meta-Infrastructure Version History

## v1.9 (2026-03-XX) — Tiered Memory + Skills Migration
- **Architecture:** One operator agent + progressive-disclosure skills
- **Memory:** Hot/warm/cold tiering. CLAUDE.md ≤200 lines.
- **Task state:** Structured (JSONL/SQLite/Beads), not markdown
- **Handoffs:** Single JSON Schema envelope, validated at runtime
- **Quality:** Eval-first anti-drift. Rules require corresponding eval cases.
- **Agent count:** ~5-7 skills (down from 13 roles)
- **Doc footprint:** Target <300KB (down from 1.4MB)
- **Git ref:** tag v1.9, branch main after migration
- **Migration prompt:** meta-review-v1.9-migration.md

## v1.8 (prior) — Role-Based Multi-Agent Architecture
- **Architecture:** 13 named agent roles with preambles and roster
- **Memory:** Flat markdown, no tiering
- **Task state:** Session artifact markdown files
- **Handoffs:** 12 markdown templates, no validation
- **Quality:** Convention rules in preambles and CLAUDE.md, no evals
- **Agent count:** 13 standing roles
- **Doc footprint:** ~1.4 MB / 591 files
- **Git ref:** tag v1.8-final, branch archive/meta-infra-v1.8
```

### 4.3 — Define Scoring Criteria for Version Comparison

Create `.agent/evals/meta-scoring.md`:

```markdown
# Meta-Infrastructure Scoring Rubric

Use this rubric to compare infrastructure versions. Score each dimension 1-5.

## Dimensions

### 1. Context Efficiency (weight: 3x)
How much of the context window is consumed by infrastructure before real work begins?
- 1: >30% of context consumed by infrastructure loading
- 3: 10-15% consumed, most loaded on demand
- 5: <5% consumed at startup, all additional context loaded per-task

### 2. Session Bootstrap Time (weight: 2x)
How long (in tokens/time) does it take an agent to become productive?
- 1: Agent must read >10 files before starting work
- 3: Agent reads 1-2 files, begins work within first response
- 5: Agent reads CLAUDE.md only, triggers skills as needed

### 3. Anti-Drift Mechanism Strength (weight: 3x)
How reliably are conventions enforced across sessions?
- 1: Conventions exist only as prose rules in docs
- 3: Some conventions have schema validation or tests
- 5: All critical conventions have executable evals + CI enforcement

### 4. Documentation Freshness (weight: 2x)
What fraction of documentation is current and actively used?
- 1: >50% of docs are stale, duplicated, or orphaned
- 3: Periodic cleanup, some stale docs persist
- 5: Keep/delete filter enforced, all docs justify their existence

### 5. Session Artifact Hygiene (weight: 2x)
How much cruft accumulates per completed milestone?
- 1: >5 session files per milestone, no cleanup policy
- 3: Session files created but triaged regularly
- 5: No session files created; state stored structurally, scratch discarded

### 6. Handoff Reliability (weight: 2x)
How often do handoffs between domains succeed without human intervention?
- 1: Handoffs are prose, frequently misinterpreted
- 3: Handoffs have templates, sometimes validated
- 5: Handoffs are schema-validated, rejected if malformed

### 7. Scalability (weight: 1x)
How well does the infrastructure handle adding a new project to the portfolio?
- 1: New project requires creating multiple new agent roles and templates
- 3: New project reuses most infrastructure with some customization
- 5: New project inherits meta-level skills and schema, needs only project CLAUDE.md

## Scoring

Weighted score = sum of (dimension score × weight) / sum of weights

Record scores for each version in VERSION.md for longitudinal tracking.
```

### 4.4 — Score v1.8 Before Migration

Before you start changing things, score v1.8 against the rubric. Based on the reviewer findings, the expected scores are approximately:

| Dimension | v1.8 Score | Rationale |
|---|---|---|
| Context Efficiency | 1 | ~20% context consumed loading infrastructure |
| Session Bootstrap | 1 | 7-line preambles × 13 roles, copy-pasted per session |
| Anti-Drift | 1 | Rules in prose only, no validation or evals |
| Doc Freshness | 2 | Large volume, much duplication, some active use |
| Session Hygiene | 1 | 11 session files for a 6-task feature |
| Handoff Reliability | 2 | Templates exist but no validation |
| Scalability | 2 | Infrastructure exists but is heavyweight to replicate |

**v1.8 estimated weighted score: ~1.4 / 5.0**

Record this in VERSION.md. After v1.9 migration is complete, re-score and compare.

---

## Execution Order

1. **Archive v1.8** (Phase 4.1–4.4). Do this first, before any destructive changes.
2. **Apply keep/delete filter** (Phase 2.5). Bulk reduction of file count.
3. **Rewrite meta-CLAUDE.md** (Phase 2.1). Establishes the new constitution.
4. **Convert roles to skills** (Phase 2.2). Eliminates standing agent roles.
5. **Set up structured task tracker** (Phase 2.3). Enables session artifact elimination.
6. **Create eval scaffold** (Phase 2.4). Migrates preamble rules to executable tests.
7. **Project-level cleanup** (Phase 3.1–3.3). Apply changes across all 12 projects.
8. **SCUE-specific migration** (Phase 3.4). Most complex project gets dedicated attention.
9. **Record findings in PROTOCOL IMPROVEMENTS** (Phase 1). Document the changes formally.
10. **Score v1.9** (Phase 4.4 re-run). Compare against v1.8 baseline.
