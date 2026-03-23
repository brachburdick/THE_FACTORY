# DrawDown: Architecture Brief

> **Date:** 2026-03-22
> **Type:** Architecture brief for future implementation agent
> **Scope:** New standalone app that reads/writes pipeline process diagrams as markdown
> **Depends on:** THE_FACTORY v1.9+ infrastructure (CLAUDE.md, schemas, JSONL records)
> **Does NOT modify:** Pipeline constitution, flow skills, agent behavior, or task tracking

---

## 1. What This App Is

A lightweight frontend application with draw.io/excalidraw-style diagramming capabilities
that uses **markdown files as its persistent data layer**. Diagrams describe:

- Software development processes (flow skills: debug, feature, refactor)
- Inter-module communication within projects (layer boundaries, API contracts)
- Agent-agent and user-agent interaction patterns (handoffs, dispatch, verification)
- The review/assessment/improvement cycle (v1.10 flywheel)
- Pipeline infrastructure evolution across versions

The app serves two audiences:
1. **The human operator** — visual editing, drag-and-drop, zoom, pan, connect nodes
2. **Agents** — programmatic read/write of the same markdown files to assess and update diagrams

The app is **read-only with respect to pipeline infrastructure**. It reads pipeline
artifacts (CLAUDE.md, schemas, JSONL, flow skills) to populate initial diagram content,
but all diagram state lives in its own siloed directory.

---

## 2. Name

**DrawDown** — visual diagrams that ground ("draw down") abstract pipeline processes into
concrete, editable maps. Also evokes "markdown" (the data layer) and "draw" (the interaction).

---

## 3. Siloing Strategy

### 3.1 The Problem
Pipeline agents already operate under context-budget pressure (hot/warm/cold memory tiers).
Adding diagram files to the pipeline's awareness would increase agent context load without
improving task execution. The diagram layer is *about* the pipeline, not *part of* it.

### 3.2 The Solution: One-Way Data Flow

```
Pipeline artifacts              Diagram app layer
(CLAUDE.md, schemas,    ───►    (reads pipeline artifacts,
 JSONL, flow skills)            writes ONLY to its own dir)

Pipeline agents NEVER           Diagram MD files live in a
read or write diagram           directory that pipeline agents
MD files.                       have no trigger for.
```

### 3.3 Directory Structure

```
THE_FACTORY/
├── CLAUDE.md                    ← Pipeline agents read this (hot tier)
├── .agent/                      ← Pipeline structured state
├── skills/                      ← Pipeline skills
├── .claude/skills/              ← Pipeline flow skills
├── support/                     ← Historical reference (cold tier)
│
└── diagrams/                    ← ALL diagram app state lives here
    ├── config.yaml              ← App config: pipeline version, source paths
    ├── schemas/
    │   └── diagram-node.json    ← JSON Schema for diagram MD format
    ├── processes/               ← Process flow diagrams
    │   ├── feature-flow.md
    │   ├── debug-flow.md
    │   ├── refactor-flow.md
    │   ├── assessment-cycle.md
    │   └── improvement-flywheel.md
    ├── architecture/            ← Module/layer communication diagrams
    │   ├── scue-layers.md
    │   ├── crucible-modules.md
    │   └── tinyshop-modules.md
    ├── interactions/            ← Agent-agent and user-agent diagrams
    │   ├── handoff-protocol.md
    │   ├── dispatch-verification.md
    │   └── multi-model-assessment.md
    └── meta/                    ← Pipeline evolution diagrams
        ├── version-changelog.md
        └── scoring-dimensions.md
```

### 3.4 Keeping Pipeline Agents Ignorant

- The `diagrams/` directory is **never referenced** in CLAUDE.md, trigger tables,
  or any flow skill.
- No task in `.agent/tasks.jsonl` should target diagram files.
- Diagram generation/update is done by a **separate agent context** that loads the
  app's own instructions, not the pipeline constitution.
- The `.gitignore` or CLAUDE.md does NOT need to exclude `diagrams/` — pipeline agents
  simply have no trigger for it. The trigger table is the gatekeeper.

### 3.5 Updating Diagrams When Pipeline Changes

When a pipeline version ships (e.g., v1.9 → v1.10):

1. A dedicated "diagram sync" agent (or the human) runs with the app's instructions
2. It reads the new CLAUDE.md, schemas, flow skills
3. It diffs against the diagram app's `config.yaml` (which records the last-synced
   pipeline version)
4. It proposes updates to affected diagram MD files
5. The human reviews/applies via the app's visual editor

This is a **pull model** — diagrams pull from pipeline state on demand, rather than
pipeline agents pushing to diagrams during normal work.

---

## 4. Markdown Diagram Format

### 4.1 Design Goals

- Human-readable in any markdown viewer (GitHub, VS Code, etc.)
- Machine-parseable with simple regex/YAML parsing — no custom parser needed
- Captures both **semantic content** (what the nodes mean) and **layout hints**
  (where they should render), but layout is always optional
- Excalidraw-compatible export path (the FE can generate Excalidraw JSON from this)

### 4.2 Format Specification

Each diagram is a single `.md` file with three sections:

```markdown
---
id: feature-flow
title: "Feature Flow: Intent → Spec → Plan → Implement → Test → Verify"
type: process                    # process | architecture | interaction | meta
version: 1                       # Incremented on structural changes
pipeline_version: "1.9.2"       # Pipeline version this diagram reflects
sources:                         # Pipeline artifacts this diagram derives from
  - ".claude/skills/feature-flow/SKILL.md"
  - "CLAUDE.md#task-type-flow-routing"
last_synced: "2026-03-22"
tags: [flow, feature, phases]
---

# Feature Flow

## Nodes

### intent-check
- type: phase
- label: "Phase 0: Intent Check"
- description: "Confirm feature has sufficient intent capture"
- gate: "Dispatch readiness met. All required intent fields explicit."
- connects_to: [spec]
- style: rounded-rect
- color: blue

### spec
- type: phase
- label: "Phase 1: Spec"
- description: "Define what will be built"
- gate: "Spec exists with inputs, outputs, edge cases. Human confirmed."
- connects_to: [plan]
- style: rounded-rect
- color: blue

### plan
- type: phase
- label: "Phase 2: Plan"
- description: "Break spec into ordered implementation steps"
- gate: "Implementation plan exists with ordered steps and file list."
- connects_to: [implement]
- style: rounded-rect
- color: blue

### implement
- type: phase
- label: "Phase 3: Implement"
- description: "Build the feature according to the plan"
- gate: "All planned implementation steps complete."
- connects_to: [test]
- style: rounded-rect
- color: green

### test
- type: phase
- label: "Phase 4: Test"
- description: "Verify feature works, no regressions"
- gate: "All new tests pass. No regressions."
- connects_to: [verify]
- style: rounded-rect
- color: green

### verify
- type: phase
- label: "Phase 5: Verify & Close"
- description: "Separate-context verification, run record, close task"
- gate: "Separate context verified. Run record written."
- connects_to: []
- style: rounded-rect
- color: green

### escalation
- type: decision
- label: "Escalate to Operator"
- description: "Missing intent, spec ambiguity, or 3+ retry failures"
- connects_to: [intent-check]
- style: diamond
- color: red

## Edges

- from: intent-check → to: spec | label: "Intent confirmed" | style: solid
- from: intent-check → to: escalation | label: "Missing fields" | style: dashed | color: red
- from: spec → to: plan | label: "Human approved" | style: solid
- from: plan → to: implement | label: "Plan ready" | style: solid
- from: implement → to: test | label: "Steps complete" | style: solid
- from: implement → to: plan | label: "Plan wrong, replanning" | style: dashed | color: orange
- from: test → to: verify | label: "All pass" | style: solid
- from: test → to: implement | label: "Failures found" | style: dashed | color: orange
- from: escalation → to: intent-check | label: "Operator resolved" | style: dotted

## Layout (optional — FE manages this, agents can ignore)

positions:
  intent-check: { x: 400, y: 50 }
  spec: { x: 400, y: 200 }
  plan: { x: 400, y: 350 }
  implement: { x: 400, y: 500 }
  test: { x: 400, y: 650 }
  verify: { x: 400, y: 800 }
  escalation: { x: 100, y: 125 }

canvas:
  width: 800
  height: 900
  zoom: 1.0
```

### 4.3 Node Types

| Type | Shape | Use |
|------|-------|-----|
| `phase` | Rounded rectangle | Flow skill phases, process steps |
| `decision` | Diamond | Branch points, gates, conditionals |
| `actor` | Person/circle | User, agent, model |
| `artifact` | Document/cylinder | Files, schemas, JSONL records |
| `system` | Rectangle | External systems, services |
| `group` | Dashed box | Grouping related nodes (e.g., "Layer 0") |
| `annotation` | Sticky note | Comments, notes, warnings |

### 4.4 Edge Styles

| Style | Meaning |
|-------|---------|
| `solid` | Normal flow / happy path |
| `dashed` | Error/exception path |
| `dotted` | Optional / conditional |
| `thick` | High-traffic / critical path |

### 4.5 Diagram Types

| Type | Content | Example sources |
|------|---------|-----------------|
| `process` | Flow skill phases, gates, escalation paths | `.claude/skills/*-flow/SKILL.md` |
| `architecture` | Module boundaries, layer communication, contracts | Project CLAUDE.md, schemas |
| `interaction` | Agent-agent handoffs, user-agent protocols | `skills/handoff/SKILL.md`, handoff-envelope.json |
| `meta` | Pipeline evolution, scoring dimensions, version diffs | CLAUDE.md, `.agent/evals/meta-scoring.md` |

### 4.6 Why This Format

- **Frontmatter** is standard YAML — every markdown parser handles it
- **Nodes section** uses H3 headers as node IDs + bullet-list properties. An agent
  can add a node by appending an H3 block. The FE parses node properties from the
  bullet list.
- **Edges section** uses a simple `from → to | key: value` format that's easy to
  regex-parse and easy to read
- **Layout section** is clearly separated and optional. Agents can modify semantic
  content (nodes, edges) without touching layout. The FE manages layout on visual edit.
- **No JSON blobs in markdown.** The format stays readable even without the app.

---

## 5. Version Resilience

### 5.1 The Adaptation Problem

Pipeline versions change the structure of flows, schemas, and protocols. The app must
adapt without a full rewrite each time.

### 5.2 Adaptation Mechanism: Source Mapping + Diffing

Each diagram's frontmatter records:
- `pipeline_version`: which version it was generated from
- `sources`: which specific files it derives from
- `last_synced`: when it was last updated

When a new pipeline version ships:

1. The sync agent reads the new CLAUDE.md and extracts the version
2. For each diagram, it checks `pipeline_version` against the new version
3. For stale diagrams, it reads the listed `sources` in the new version
4. It diffs the source content against what the diagram currently represents
5. It proposes node/edge additions, removals, or modifications
6. The human reviews via the visual editor

### 5.3 What Makes This Resilient

- **The format is pipeline-agnostic.** Nodes, edges, and layout are generic graph
  concepts. Whether the pipeline has 3 flows or 30, the format doesn't change.
- **Source mapping, not source embedding.** Diagrams point to sources, they don't
  copy source content. When sources change, the pointer still works.
- **Incremental updates.** A pipeline version change doesn't regenerate all diagrams.
  Only diagrams whose `sources` changed need updating. The diff tells you what changed.
- **Layout preservation.** When an agent updates semantic content (adds a node),
  existing layout positions are preserved. Only the new node needs positioning.

### 5.4 What Requires Manual Attention

- **New diagram types.** If v1.11 introduces a completely new concept (e.g., a new
  flow type), a new diagram file must be created. The sync agent can detect this by
  comparing the trigger table across versions.
- **Structural reorganization.** If the pipeline restructures fundamentally (e.g.,
  moving from skills/ to a different pattern), source paths break. The config.yaml
  records path mappings that can be updated.

---

## 6. Frontend Requirements

### 6.1 Core Features (MVP)

| Feature | Priority | Notes |
|---------|----------|-------|
| Parse diagram MD → render as interactive graph | P0 | Read the format from §4 |
| Drag-and-drop node positioning | P0 | Updates Layout section only |
| Connect nodes with edges | P0 | Updates Edges section |
| Add/edit/delete nodes | P0 | Updates Nodes section |
| Save back to MD file | P0 | Round-trip: parse → edit → serialize |
| Zoom, pan, fit-to-screen | P0 | Standard canvas controls |
| Node property editor (sidebar) | P1 | Edit description, gate, type, style |
| Edge property editor | P1 | Edit label, style, color |
| Multiple diagram tabs | P1 | Load from diagrams/ directory |
| Auto-layout (dagre/elk) | P2 | For diagrams without Layout section |
| Export to Excalidraw JSON | P2 | Interop with Excalidraw ecosystem |
| Export to SVG/PNG | P2 | For embedding in docs |
| Diff view (two versions) | P3 | Show what changed between syncs |

### 6.2 Tech Stack Suggestion

- **React + TypeScript** — matches SCUE/Tinyshop patterns in the portfolio
- **React Flow** or **tldraw** — proven open-source canvas libraries
  - React Flow: better for structured flowcharts with typed edges/handles
  - tldraw: better for freeform drawing, closer to Excalidraw feel
- **gray-matter** — YAML frontmatter parsing
- **Vite** — fast dev server, simple config
- **File system access** — either:
  - Local dev server with fs read/write API (simplest)
  - File System Access API in browser (no server needed, but browser-only)
  - VS Code extension webview (if you want IDE integration)

### 6.3 Agent Integration

Agents interact with diagram files via standard file read/write — no API needed.
The app watches the file system and hot-reloads when a diagram file changes.

Agent workflow for updating a diagram:
1. Read the `.md` file
2. Parse frontmatter + nodes + edges (simple text processing)
3. Add/modify/remove nodes or edges
4. Write the file back, preserving the Layout section unchanged
5. The FE detects the file change and re-renders

---

## 7. Initial Diagram Set

When the app is first built, generate these diagrams from current pipeline state:

### 7.1 Process Diagrams (from flow skills)

| Diagram | Source |
|---------|--------|
| `feature-flow.md` | `.claude/skills/feature-flow/SKILL.md` |
| `debug-flow.md` | `.claude/skills/debug-flow/SKILL.md` |
| `refactor-flow.md` | `.claude/skills/refactor-flow/SKILL.md` |
| `session-protocol.md` | `CLAUDE.md` Session Protocol + Land the Plane |
| `git-protocol.md` | `CLAUDE.md` Git Protocol |

### 7.2 Interaction Diagrams (from handoff + assessment)

| Diagram | Source |
|---------|--------|
| `handoff-protocol.md` | `skills/handoff/SKILL.md` + `.agent/schemas/handoff-envelope.json` |
| `dispatch-verification.md` | Feature-flow Phase 0 + Phase 5 |
| `multi-model-assessment.md` | v1.10 plan Part 2 (when implemented) |
| `improvement-flywheel.md` | v1.10 plan Part 3 |
| `brainstorm-triage.md` | `skills/brainstorm/SKILL.md` |

### 7.3 Architecture Diagrams (per project)

| Diagram | Source |
|---------|--------|
| `scue-layers.md` | `scue/CLAUDE.md` (Layer 0-3 architecture) |
| `crucible-modules.md` | `CRUCIBLE/CLAUDE.md` |
| `tinyshop-modules.md` | `Tinyshop/CLAUDE.md` |
| `pipeline-infrastructure.md` | `CLAUDE.md` Workspace Layout + Memory Tiers |

### 7.4 Meta Diagrams

| Diagram | Source |
|---------|--------|
| `version-evolution.md` | `support/v1.8/`, `support/v1.9/`, `support/v1.10/` |
| `scoring-dimensions.md` | `.agent/evals/meta-scoring.md` |
| `task-type-routing.md` | `CLAUDE.md` Trigger Table + Task-Type Flow Routing |

---

## 8. Agent Instructions for Diagram Sync

When a future agent is tasked with syncing diagrams after a pipeline version change,
it should follow this protocol:

### 8.1 Sync Protocol

```
1. Read `diagrams/config.yaml` → get last_synced_pipeline_version
2. Read `CLAUDE.md` → get current pipeline version
3. If versions match → no sync needed, exit
4. For each diagram file in diagrams/**/*.md:
   a. Read frontmatter → get sources[]
   b. For each source, read the current file content
   c. Compare current source content against what the diagram represents
   d. If source has new phases/nodes → add corresponding nodes
   e. If source removed phases/nodes → mark for removal (don't auto-delete)
   f. If source changed descriptions/gates → update node properties
   g. Preserve the Layout section unchanged
   h. Update frontmatter: pipeline_version, last_synced
5. Update `diagrams/config.yaml` → last_synced_pipeline_version
6. Report changes to operator for review
```

### 8.2 What the Sync Agent Needs

- Read access to: CLAUDE.md, .claude/skills/, skills/, .agent/schemas/,
  project-level CLAUDE.md files
- Write access to: diagrams/ only
- No pipeline skill loading. The sync agent has its own instructions (this document).
- The sync agent does NOT use the trigger table, flow skills, or task tracker.
  It is a completely separate execution context.

---

## 9. config.yaml Spec

```yaml
# diagrams/config.yaml
app_name: "TBD"                           # Chosen name from §2
last_synced_pipeline_version: "1.9.2"
pipeline_root: ".."                        # Relative path to THE_FACTORY root

# Source path mappings — update these if pipeline restructures directories
source_paths:
  constitution: "CLAUDE.md"
  flow_skills: ".claude/skills/"
  portfolio_skills: "skills/"
  schemas: ".agent/schemas/"
  meta_scoring: ".agent/evals/meta-scoring.md"
  projects:
    scue: "scue/CLAUDE.md"
    crucible: "CRUCIBLE/CLAUDE.md"
    tinyshop: "Tinyshop/CLAUDE.md"

# Path mapping version history — enables adaptation across pipeline versions
path_history:
  - version: "1.9.2"
    mappings: {}  # Current, no overrides needed
  # Future: if v1.11 moves skills/ to .claude/portfolio-skills/,
  # add a mapping here and the sync agent resolves it
```

---

## 10. Relationship to Existing Infrastructure

### What This App Reads (pipeline artifacts — read-only)

| Artifact | What it provides to diagrams |
|----------|------------------------------|
| `CLAUDE.md` | Trigger table, flow routing, session protocol, git protocol |
| `.claude/skills/*-flow/SKILL.md` | Phase definitions, gates, negative constraints |
| `skills/handoff/SKILL.md` | Handoff protocol, dispatch states |
| `skills/brainstorm/SKILL.md` | Brainstorm phases, triage states |
| `.agent/schemas/*.json` | Field definitions for handoff, run records, incidents |
| `.agent/evals/meta-scoring.md` | Scoring dimensions for meta diagrams |
| `support/v1.10/*.md` | Assessment cycle, flywheel, conversation capture |
| `{project}/CLAUDE.md` | Project architecture, layer definitions |

### What This App Writes (diagram layer — isolated)

| Artifact | Purpose |
|----------|---------|
| `diagrams/**/*.md` | Diagram content files |
| `diagrams/config.yaml` | App config and sync state |
| `diagrams/schemas/*.json` | Diagram format schemas (self-contained) |

### What Pipeline Agents Never Touch

Pipeline agents have no trigger for `diagrams/`. The CLAUDE.md trigger table does not
reference it. No flow skill mentions it. No schema links to it. The isolation is
maintained by **absence from the pipeline's awareness**, not by access control.

---

## 11. Future Extensions

| Extension | When | What |
|-----------|------|------|
| Live JSONL overlay | After v1.10 Phase 0 (pipeline scoring) | Overlay run counts, success rates on process diagram nodes |
| Assessment heatmap | After v1.10 Phase 3 (assessment skill) | Color-code architecture diagram nodes by assessment scores |
| Conversation trace view | After v1.10 Phase 1 (conversation capture) | Show which diagram path a conversation followed |
| Collaborative editing | If team grows | WebSocket sync for multi-user editing |
| Version timeline | After 3+ pipeline versions | Animate diagram evolution across versions |
