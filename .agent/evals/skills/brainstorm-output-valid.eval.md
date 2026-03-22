# Eval: brainstorm-output-valid

## Should: Produce valid JSONL output
- Input: Brainstorm skill run against any research findings
- Expected: Output file is valid JSONL (one JSON object per line, parseable)
- Fail if: Output is markdown prose, or JSON lines fail to parse

## Should: Include all required fields per idea
- Input: Any brainstorm output line
- Expected: Each line has `id`, `title`, `oneliner`, `source_findings`, `feasibility`, `novelty`, `effort`, `dependencies`, `operator_verdict`, `tags`
- Fail if: Any required field is missing

## Should: Use valid enum values
- Input: Any brainstorm output line
- Expected: `feasibility` is one of `high | medium | low | unknown`; `novelty` is one of `high | medium | low`; `effort` is one of `small | medium | large`; `operator_verdict` is `null` on generation (or one of `approved | deferred | rejected | merged:idea-NNN` after triage)
- Fail if: Enum fields contain invalid values

## Should: Reference existing research findings
- Input: Any brainstorm output line's `source_findings` array
- Expected: Every filename in `source_findings` corresponds to a file that exists in the project's `research/` directory
- Fail if: `source_findings` references a file that does not exist

## Should: Have unique idea IDs
- Input: Complete brainstorm output file
- Expected: No duplicate `id` values across all lines
- Fail if: Two or more lines share the same `id`

## Should: Write output to correct location
- Input: Brainstorm skill run
- Expected: Output written to `{project}/.agent/brainstorm/{slug}.jsonl`
- Fail if: Output written to `research/`, `docs/`, or project root

## Should NOT: Auto-promote ideas to task tracker
- Input: Brainstorm skill run without operator triage
- Expected: No new tasks created in `.agent/tasks.jsonl` during Phase 2-3
- Fail if: Tasks appear in tracker before operator approval in Phase 4
