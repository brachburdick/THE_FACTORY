# DD-001: DrawDown — Pipeline Process Visualization App

**Date:** 2026-03-22
**Classification:** IDEA — new tooling, not yet validated by failure. Independent of pipeline version.
**Source:** Operator request for visual editing of pipeline processes with agent read/write capability
**Scope:** New standalone app. Zero impact on pipeline agent context or behavior.

## Problem

Pipeline processes (flow skills, handoff protocols, assessment cycles, module communication)
exist only as prose in markdown skill files and the CLAUDE.md constitution. This creates
two gaps:

1. **For the operator:** No visual overview of how processes connect, branch, and loop.
   Understanding the full feature-flow requires reading a 109-line skill file. Understanding
   how flows interact with handoffs, assessments, and the improvement flywheel requires
   reading 5+ files and mentally composing them.

2. **For agents assessing/updating processes:** No structured, diffable representation of
   process graphs. When the pipeline evolves (v1.9 → v2.0), there is no mechanism to
   visualize what changed in process structure, only prose diffs.

## Proposed Solution

A lightweight frontend app with draw.io/excalidraw-style capabilities that uses **markdown
files as its persistent data layer**. The operator edits visually; agents read/write the
same markdown files programmatically.

**Key design constraint:** The app is **completely siloed** from pipeline agent context.
Pipeline agents never read, write, or trigger on DrawDown files. The app reads pipeline
artifacts (CLAUDE.md, schemas, flow skills) as input, but all diagram state lives in its
own `diagrams/` directory.

## Architecture Summary

**Data flow:**
```
Pipeline artifacts              DrawDown layer
(CLAUDE.md, schemas,    →       (reads pipeline artifacts,
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

**Tech stack suggestion:** React + TypeScript, React Flow or tldraw, gray-matter for
frontmatter parsing, Vite. File system access via local dev server or File System Access API.

## Full Architecture Brief

`support/v1.10/diagram-app-architecture-brief.md`
