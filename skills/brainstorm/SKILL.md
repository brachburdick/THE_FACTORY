---
name: brainstorm
description: >
  Transform research findings into prioritized feature candidates. Use when
  the task involves generating ideas, applications, or possibilities from
  existing research. Signals: "brainstorm", "ideate", "applications of",
  "what could we build", "possibilities".
---

# Brainstorm Skill: Research → Candidates

## When to Use
After a research phase has produced findings, and before committing to
feature work. This skill bridges the gap between "what we know" and
"what we could build."

## Input Requirements
- One or more research findings files (from project `research/` directory)
- Optional: operator-provided constraints (budget, timeline, hardware)
- Optional: lens (perspective to brainstorm from)

## Phase 1: Load Research
1. Read all specified research findings files.
2. Extract the key capabilities, constraints, and data availabilities
   documented in those findings.
3. Note the "Recommended Next Steps" already listed in each finding —
   these are seeds, not the full brainstorm.

## Phase 2: Generate
1. For each significant capability or data source in the findings,
   generate 3-5 concrete application ideas.
2. Cross-pollinate: combine capabilities from different findings into
   novel applications.
3. Include at least one "stretch" idea per finding — something
   non-obvious that pushes the boundary of what the research enables.
4. Write each idea as a JSONL line to
   `{project}/.agent/brainstorm/{slug}.jsonl`.

**Required fields per idea:**
- `id`: `idea-NNN`
- `title`: Short name (< 60 chars)
- `oneliner`: One sentence describing what it does and why
- `source_findings`: Array of finding filenames this idea builds on
- `feasibility`: `high | medium | low | unknown`
- `novelty`: `high | medium | low`
- `effort`: `small | medium | large`
- `dependencies`: Array of existing components or capabilities needed
- `operator_verdict`: `null` (set during triage)
- `tags`: Freeform array for categorization

## Phase 3: Summarize
1. Present to the operator:
   - Total idea count
   - Feasibility distribution (how many high/medium/low)
   - Top themes or clusters
   - Any findings that produced few ideas (may indicate
     under-explored research)
2. Ask the operator if they want to triage now or defer.

## Phase 4: Triage (Operator-Driven)
1. Walk through ideas with the operator.
2. Operator sets `operator_verdict` on each:
   - `approved` → promote to task tracker
   - `deferred` → keep in brainstorm file for later
   - `rejected` → keep in file but skip
   - `merged:idea-NNN` → combine with another idea
3. For approved ideas, create a task in `.agent/tasks.jsonl`:
   ```json
   {"id":"TASK-ID","taskType":"feature","flowPhase":"intent",
    "status":"pending","summary":"from brainstorm idea-NNN: {title}",
    "source_brainstorm":"{slug}.jsonl#idea-NNN"}
   ```

## Negative Constraints — Do NOT:
- Do NOT generate ideas without grounding in specific findings.
  Every idea must cite its `source_findings`.
- Do NOT auto-approve or auto-promote ideas. The operator triages.
- Do NOT create tasks without operator approval.
- Do NOT write brainstorm output as markdown prose. Use JSONL.
- Do NOT combine brainstorming with implementation. Generate first,
  build later.
- Do NOT load this skill if no research findings exist — there is
  nothing to brainstorm from.

## Run Record
Write a run record to `.agent/runs.jsonl` after Phase 3 (or Phase 4
if triage happened in the same session):
```json
{"run_id":"run-YYYY-MM-DD-NNN","date":"ISO-8601",
 "project_id":"project","task_id":"TASK-ID",
 "task_type":"brainstorm","workflow_path":"skills/brainstorm/SKILL.md",
 "result":"success","ideas_generated":N,"ideas_approved":N}
```
