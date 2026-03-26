# ADR-002: File-Based Artifact Coordination

**Date:** 2026-03-20
**Status:** Accepted
**Deciders:** Brach (operator), established during v1.9→v2.0 migration

## Context

THE_FACTORY needs a coordination mechanism for agent state: task queues, run records,
incident logs, session snapshots. The options were: (a) a database (SQLite or Postgres),
(b) an external service (Linear, GitHub Issues), or (c) append-only JSONL files in the repo.

The pipeline runs in a single-operator context with low write concurrency. The primary
consumers are the agent itself, assess.py, and human review.

## Decision

Use **append-only JSONL files** in `.agent/` for all coordination artifacts: `tasks.jsonl`,
`runs.jsonl`, `incidents.jsonl`, `trigger-misses.jsonl`. Each line is a self-contained JSON
object. Schemas are defined in `.agent/schemas/` and validated by the eval suite.

State snapshots (`state-snapshot.json`) use regular JSON for the current session state.

## Consequences

### Positive
- Zero infrastructure — no database server, no migrations, no connection strings
- Git-native — artifacts are versioned alongside the code they describe
- Human-readable — `cat .agent/runs.jsonl | python -m json.tool` works
- Eval-testable — schema validation is a pytest test, not a migration script
- Append-only semantics prevent accidental data loss

### Negative
- No query language — analysis requires loading into Python (assess.py)
- Duplicate entries possible (JSONL append semantics — last entry for an ID wins)
- No concurrent write safety — fine for single-agent, would break with parallelism
- File grows unbounded — will need rotation or archiving eventually

### Neutral
- JSON schemas provide structure without a database schema migration system
- The `additionalProperties: true` policy allows forward-compatible field additions

## Alternatives Considered

### SQLite
Would provide querying and concurrency safety, but adds a dependency and makes artifacts
opaque to `git diff`. Deferred to v2.2 P7 if corruption or concurrency appears.

### External issue tracker (Linear, GitHub Issues)
Would add external dependency and network latency to every task update. The agent needs
sub-second read/write for state management during active sessions.
