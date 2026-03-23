# Project Observations — THE_FACTORY Pipeline

> Project-level observations (Category A) from agent self-assessments.
> These are about the code, architecture, and project-specific practices of the pipeline itself.

## Pending

- [A2] 7 of 13 templates in `templates/` use blockquote metadata instead of YAML frontmatter, violating the normalized format established in v1.9. Affected templates were not individually checked during the rollout that was supposed to fix this. (from: self-assessment, claude-opus-4-6, 2026-03-22)

- [A1] `enable/als-reader/als_reader/writer.py`: `humanize_velocities` uses `hash((note_idx, int(time * 1000)))` for deterministic variation, but Python's `hash()` is not deterministic across sessions (randomized by default since 3.3). The same file produces different velocity patterns on each run unless `PYTHONHASHSEED` is set. Should use `hashlib` or a fixed-seed approach. (from: self-assessment, claude-opus-4-6[1m], 2026-03-22)

- [A1] `enable/als-reader/als_reader/writer.py`: Each MCP write tool (`rename_track`, `set_track_volume`, etc.) re-parses the entire .als file from disk. Applying 5 changes = 5 full decompress+parse+recompress cycles. No batch API exists — the `ALSWriter` class supports chained mutations but the MCP tools don't expose this. (from: self-assessment, claude-opus-4-6[1m], 2026-03-22)

- [A2] `enable/als-reader/als_reader/mcp_server.py`: Write tools access `writer._list_track_names()` (private method) for error messages. Public API boundary violated. (from: self-assessment, claude-opus-4-6[1m], 2026-03-22)

- [A3] `enable/als-reader/als_reader/writer.py`: `save()` writes `b'<?xml version="1.0" encoding="UTF-8"?>\n'` as a hardcoded prefix, but the original .als may have had different XML declaration attributes (standalone, encoding). The original declaration is discarded during `ET.fromstring()` and replaced with a guess. Could cause Ableton to reject files with non-standard original declarations. (from: self-assessment, claude-opus-4-6[1m], 2026-03-22)

- [A2] `enable/als-reader/als_reader/models.py`: `RackChain.devices` has forward reference to `Device` but no `__future__.annotations` wouldn't help here since `dataclasses.field` evaluates at class definition time. The type hint `list[Device]` works because `Device` is defined later in the same file but `RackChain` is defined first — this relies on Python evaluating annotations lazily with `from __future__ import annotations`, which is present. Fragile ordering dependency. (from: self-assessment, claude-opus-4-6[1m], 2026-03-22)

- [A4] `enable/als-reader/README.md`: pyproject.toml URLs reference `yourusername/als-reader` placeholder — will 404 if published to PyPI as-is. (from: self-assessment, claude-opus-4-6[1m], 2026-03-22)
