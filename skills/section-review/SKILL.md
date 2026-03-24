# Skill: Section Review

> **When to use:** Reviewing, auditing, or improving a project that has defined sections
> with boundary contracts. Triggered by: "review", "audit", "quality check", "section review".

## Prerequisites

The target project must have:
- `sections/SECTIONS.md` — section map with coupling rules and parallelization guidance
- `sections/<name>.md` — 1-page contract per section (purpose, owned paths, inputs, outputs, invariants, verification)
- Boundary enforcement evals in the pipeline eval suite

If these don't exist, create them first using `templates/section-contract.md` as the format.

## Three-Pass Review Model

### Pass 1: Section Review (parallelizable where safe)

**Goal:** Review each section's internals against its own contract.

**Dispatch:** One agent per section. Each agent receives ONLY:
- The section's contract file (`sections/<name>.md`)
- The section's owned source files
- The section's test suite
- The project's LEARNINGS.md (for known gotchas)

**Each agent does NOT receive:** Other sections' source code, other contracts, or the full CLAUDE.md.

**Agent instructions:**
1. Read the section contract. Understand purpose, invariants, and allowed dependencies.
2. Run the section's verification command. All tests must pass.
3. Review source code for: correctness, adherence to invariants, code quality, missed edge cases.
4. Check that no imports violate the "allowed dependencies" list.
5. Report findings as: violations (must fix), concerns (should fix), and observations (optional).

**Parallelization:** Check `SECTIONS.md` coupling map. Only parallelize sections marked as independent. Coupled sections run sequentially or as a combined review unit.

### Pass 2: Boundary Review (sequential, one agent)

**Goal:** Review the interfaces BETWEEN sections — this is where seam-bugs live.

**Dispatch:** One agent receives:
- ALL section contracts (but NOT source code)
- Cross-boundary type definitions (e.g., `docs/CONTRACTS.md`, `docs/interfaces.md`)
- The `SECTIONS.md` coupling map
- Any cross-boundary test results

**Agent instructions:**
1. For each boundary in the coupling map, verify:
   - Types that cross the boundary are defined in the contract docs
   - Input types match what the producing section actually exports
   - Output types match what the consuming section actually expects
   - Invariants on both sides of the boundary are compatible
2. Check for implicit assumptions: shared state, ordering dependencies, timing assumptions.
3. Check WebSocket/REST message schemas match between server and frontend.
4. Report boundary violations and implicit coupling that isn't documented.

### Pass 3: Integration Review (sequential, one agent)

**Goal:** Check end-to-end flows against acceptance criteria.

**Dispatch:** One agent receives:
- ALL section contracts (summaries, not full source)
- Section review findings from Pass 1
- Boundary review findings from Pass 2
- Project-level acceptance criteria or feature specs
- End-to-end test results (if available)

**Agent instructions:**
1. Trace each major user flow through the section map. Verify the flow is complete.
2. Check that Pass 1 and Pass 2 findings don't combine into larger systemic issues.
3. Verify that acceptance criteria are covered by at least one section's tests.
4. Identify gaps: flows that cross boundaries without contract coverage.
5. Produce a final assessment with: critical issues, section-level summaries, and recommended actions.

## Merge Protocol

After all three passes:
1. Collect findings from all agents.
2. Deduplicate (section agents may report the same issue if it's at a boundary).
3. Prioritize: boundary violations > contract violations > internal quality issues.
4. Create tasks in `.agent/tasks.jsonl` for any findings that need action.

## When NOT to Use This Model

- **Trivial changes** (typo fix, single-file edit): Just review the diff directly.
- **New section being built from scratch**: Use feature-flow, not section-review.
- **Cross-cutting refactor that changes boundaries**: Redesign sections first, then review.

## Measurement

Track these metrics in `.agent/runs.jsonl` for review-type tasks:

```json
{
  "task_type": "review",
  "review_model": "section-review",
  "sections_reviewed": 5,
  "pass1_findings": {"violations": 2, "concerns": 4, "observations": 1},
  "pass2_findings": {"boundary_violations": 1, "implicit_coupling": 0},
  "pass3_findings": {"coverage_gaps": 0, "systemic_issues": 0},
  "agents_dispatched": 7,
  "total_tokens": 45000,
  "wall_clock_minutes": 12
}
```

Compare against baseline (single-agent full-project review) to measure whether siloing helps. Key metrics:
- **Bugs found per token** — are section agents more efficient?
- **Boundary violations caught** — are Pass 2 findings unique (wouldn't be found in Pass 1)?
- **Rework rate** — do section-review findings lead to cleaner fixes than full-project findings?

## Principles (from SYNTROPY research)

- **Contracts at every boundary.** If types cross a boundary, they're documented and tested.
- **External verification.** Don't trust a section agent's self-assessment of boundary compliance.
- **Decompose where interactions are weak.** Sections split at real dataflow boundaries, not folders.
- **100% coverage.** Every source file belongs to exactly one section.
