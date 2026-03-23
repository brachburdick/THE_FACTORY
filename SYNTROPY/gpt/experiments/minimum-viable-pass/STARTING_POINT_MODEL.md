# Starting Point Model: L2

Use this as the first "good enough" SYNTROPY model.

---

## Purpose

Solve small software tasks while preserving acceptance criteria and using real verification, without introducing full decomposition overhead.

---

## Rules

1. Restate the goal and acceptance criteria before changing code.
2. Create a plan with at most 3 steps.
3. Execute one step at a time.
4. After each meaningful code change, run the external verifier.
5. If verification fails, do one local replan and try again.
6. Do not generate extra frameworks, maps, or schemas unless the task actually needs them.
7. Finish by reporting:
   - whether the acceptance criteria were met
   - what verification was run
   - whether a replan was needed

---

## Minimal Output Shape

### Goal

- one short paragraph

### Acceptance Criteria

- flat bullet list

### Plan

1. step one
2. step two
3. step three

### Execution

- edits made
- verification result
- replan if needed

---

## Why This Layer

This keeps the load-bearing SYNTROPY ideas:

- intent preservation
- bounded leaf solvability
- external verification
- replanning when needed

It deliberately omits:

- heavy artifact families
- full decomposition graphs
- formal coverage maps
- advanced boundary taxonomies
- multi-agent orchestration
