# Section-Review Manager-Worker Pilot Design

**Task:** tf-068
**Date:** 2026-03-27
**Status:** Design — ready to execute when a suitable project milestone occurs

## Objective

Run one controlled multi-agent section review (using Claude Code's Agent tool)
and benchmark against the existing single-agent baseline. Measure whether
parallelization improves bugs-per-token, wall-clock time, or boundary findings.

## Experiment Setup

### Target Project

Use SCUE (most mature section structure). Requires:
- `projects/DjTools/scue/sections/SECTIONS.md` exists
- At least 3 sections defined with contracts
- Test suite passing as baseline

### Baseline (single-agent)

Run the full section-review skill with a single agent doing all three passes
sequentially. Record:
- Total tokens consumed
- Wall-clock time
- Findings: violations, concerns, observations
- Boundary findings (cross-section issues)

### Treatment (manager-worker)

Use Claude Code's Agent tool to parallelize:

**Manager agent:**
- Reads SECTIONS.md
- Spawns one worker per section for Pass 1
- Collects findings
- Runs Pass 2 (boundary review) itself
- Runs Pass 3 (integration) itself

**Worker agents (Pass 1):**
- Each receives ONE section contract + owned files
- Reviews section internals only
- Returns structured findings report
- Does NOT see other sections

### Protocol

```
1. Manager reads SECTIONS.md, identifies sections
2. Manager spawns N workers in parallel (Agent tool, subagent_type=Explore)
3. Each worker:
   a. Read section contract
   b. Read owned source files
   c. Run section verification command
   d. Report findings (violations, concerns, observations)
4. Manager collects all worker results
5. Manager runs Pass 2: boundary review
   - Check cross-section imports
   - Verify boundary contracts
   - Flag coupling violations
6. Manager runs Pass 3: integration review
   - Check end-to-end behavior
   - Verify section interactions
   - Assess overall architecture
7. Manager produces final report
```

## Metrics

| Metric | How to Measure | Baseline | Treatment |
|---|---|---|---|
| **Tokens consumed** | Sum all agent token counts | ___ | ___ |
| **Wall-clock time** | Session start to report | ___ min | ___ min |
| **Findings: violations** | Count from report | ___ | ___ |
| **Findings: concerns** | Count from report | ___ | ___ |
| **Boundary findings** | Cross-section issues found | ___ | ___ |
| **Bugs-per-1K-tokens** | violations / (tokens/1000) | ___ | ___ |
| **Rework needed** | Issues missed that needed revisit | ___ | ___ |

## Success Criteria

The pilot is worth scaling if ANY of:
- Treatment finds >= 1 boundary violation baseline missed
- Treatment completes in < 70% wall-clock time of baseline
- Bugs-per-1K-tokens is >= 1.3x baseline

The pilot should NOT scale if:
- Total tokens > 2x baseline (cost inefficient)
- Worker agents fail to scope correctly (read files outside section)
- Manager overhead negates parallelization gains

## Risks

| Risk | Mitigation |
|---|---|
| Workers drift beyond section scope | Explicit file scope in agent prompts, blast-radius hook active |
| Manager overwhelmed by worker findings | Structured report format, cap findings per worker |
| Token cost explosion | Set tool_call_limit on workers, monitor in real-time |
| Section contracts too vague for workers | Pre-check contract completeness before spawning |

## Prerequisites

- [x] tf-060: Extended skill frontmatter (inputs/outputs for skills)
- [x] tf-042: JSON schemas for JSONL files
- [ ] SCUE sections defined with contracts
- [ ] SCUE test suite passing

## Execution Plan

1. Verify SCUE sections exist and are up to date
2. Run baseline: single-agent full section review, record metrics
3. Run treatment: manager-worker parallel review, record metrics
4. Compare metrics in the template above
5. Write findings to `.agent/runs.jsonl` with experiment tag
6. Decide: scale (integrate into skill) or archive (document why not)
