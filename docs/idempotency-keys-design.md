# Idempotency Keys for Event-Driven Sessions

**Status:** Design — implement with automation Phase 1
**Task:** tf-059
**Date:** 2026-03-27

## Problem

When THE_FACTORY moves toward event-driven session triggers (file watches,
webhook callbacks, scheduled tasks), the same event can fire multiple times:
- Filesystem events can duplicate (rapid saves, editor writes)
- Webhooks can retry on timeout
- Scheduled tasks can overlap if a session runs long

Without deduplication, the pipeline may spawn redundant sessions that
conflict with each other (concurrent edits to the same files, duplicate
task claims, competing commits).

## Design

### Event ID Derivation

Each trigger produces an `event_id` — a stable, deterministic hash derived
from the trigger payload. Same payload always produces the same ID.

```
event_id = sha256(event_type + "|" + canonical_payload)[:16]
```

**Canonical payload** depends on event type:

| Event Type | Canonical Payload | Example |
|---|---|---|
| `file_change` | sorted file paths + content hashes | `src/main.py:a1b2c3` |
| `webhook` | request body (sorted keys) | `{"pr": 42, "action": "opened"}` |
| `schedule` | task_id + scheduled_time (minute granularity) | `nightly-assess:2026-03-27T09:00` |
| `manual` | timestamp (second granularity) | `2026-03-27T04:10:15` |

### Event Log

Events are stored in `.agent/events.jsonl`:

```json
{
  "event_id": "a1b2c3d4e5f67890",
  "event_type": "file_change",
  "timestamp": "2026-03-27T04:10:15Z",
  "payload_summary": "src/main.py changed",
  "session_id": "abc-123",
  "status": "completed",
  "result": "success"
}
```

**Fields:**
- `event_id` — deterministic hash (primary key for dedup)
- `event_type` — one of: `file_change`, `webhook`, `schedule`, `manual`
- `timestamp` — when the event was received
- `payload_summary` — human-readable description
- `session_id` — the Claude Code session that handled this event (null if skipped)
- `status` — `pending | in_progress | completed | skipped | failed`
- `result` — `success | partial | failed | duplicate` (null while in_progress)

### Deduplication Logic

```
on_event(event):
    event_id = derive_event_id(event)
    existing = lookup(events_jsonl, event_id)

    if existing and existing.status in ("in_progress", "completed"):
        log(event_id, status="skipped", result="duplicate")
        return  # skip

    if existing and existing.status == "failed":
        # Retry failed events — don't dedup failures
        pass

    log(event_id, status="in_progress")
    session = start_session(event)
    log(event_id, status="completed", result=session.result, session_id=session.id)
```

### Dedup Window

Events are only deduplicated within a configurable window (default: 1 hour).
Events older than the window are eligible for re-processing. This prevents
stale dedup entries from blocking legitimate re-triggers.

```json
{
  "dedup_window_minutes": 60
}
```

### Concurrency

The event log uses append-only JSONL with advisory file locking:
1. Acquire lock on `.agent/events.lock`
2. Read last N entries (within dedup window)
3. Check for duplicate
4. Append new entry
5. Release lock

For single-machine use (current target), `fcntl.flock` is sufficient.
Multi-machine scenarios would require a shared store (out of scope for v1).

## Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "status"],
  "properties": {
    "event_id": { "type": "string", "minLength": 16, "maxLength": 16 },
    "event_type": { "type": "string", "enum": ["file_change", "webhook", "schedule", "manual"] },
    "timestamp": { "type": "string", "format": "date-time" },
    "payload_summary": { "type": "string" },
    "session_id": { "type": ["string", "null"] },
    "status": { "type": "string", "enum": ["pending", "in_progress", "completed", "skipped", "failed"] },
    "result": { "type": ["string", "null"], "enum": ["success", "partial", "failed", "duplicate", null] }
  }
}
```

## Implementation Plan (for Phase 1)

1. Add schema to `.agent/schemas/event.schema.json`
2. Add `derive_event_id()` utility to a shared module
3. Add dedup check to session startup hook
4. Wire file-change triggers (if/when file watchers land)
5. Add eval: `test_event_entries_valid` (schema validation, like other JSONL tests)

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Hash collision | 16-char hex = 64-bit space, sufficient for event dedup |
| Lock contention | Advisory locks, short critical section, single-machine only |
| Stale dedup blocking retriggers | Configurable dedup window, failed events always retrigger |
| Event log growth | Periodic rotation (archive entries older than 7 days) |

## Open Questions

- Should the dedup window be per-event-type? (File changes may need shorter windows than schedules)
- Should the event log be pruned automatically, or left for operator cleanup?
- Integration with Langfuse: should events become Langfuse traces?
