# uisato/ableton-mcp-extended — Research Report

> **Source:** https://github.com/uisato/ableton-mcp-extended
> **Base:** ahujasid/ableton-mcp (2330 stars, the original Ableton MCP)
> **Relationship:** Standalone repo bootstrapped from ahujasid's codebase, not a GitHub fork
> **Stats:** 139 stars | MIT License | Last activity: 2026-03-17
> **Researched:** 2026-03-20

---

## Overview

MCP server + Ableton Remote Script that allows AI assistants to control Ableton Live
via the Model Context Protocol. Extends the original ahujasid/ableton-mcp with additional
remote script commands, a UDP transport layer, and a bundled ElevenLabs voice/audio MCP server.

**Critical finding:** The "extended" label is half-delivered. The remote script has ~30 command
handlers (vs ~16 in base), but only 16 are exposed as MCP tools — nearly identical to the base.
The ~15 additional commands are implemented but not wired up to the MCP layer.

---

## Architecture

```
AI Assistant (Claude/Cursor)
    │
    ▼ MCP (stdio)
MCP Server (Python, FastMCP)  ──  MCP_Server/server.py
    │
    ▼ TCP (localhost:9877)
Ableton Remote Script (ControlSurface)  ──  AbletonMCP_Remote_Script/__init__.py
    │
    ▼ Live API
Ableton Live
```

**Transport modes:**
- **TCP only (standard):** Remote Script listens on `localhost:9877`. All MCP tool calls use this.
- **TCP + UDP hybrid:** Alternate Remote Script variant adds UDP on port `9878` for fire-and-forget
  real-time parameter updates. Only `set_device_parameter` and `batch_set_device_parameters`
  are supported over UDP.

**No Max4Live device.** Both base and extended use a Python Remote Script (ControlSurface API).

---

## MCP Tools (Exposed to AI Assistant) — 16 Total

| Tool | R/W/X | In Base? | Description |
|------|-------|----------|-------------|
| `get_session_info` | R | Yes | Session tempo, time sig, track counts, master vol/pan |
| `get_track_info` | R | Yes | Track devices, clips, properties by index |
| `get_browser_tree` | R | Yes | Hierarchical browser categories (instruments/sounds/drums/effects) |
| `get_browser_items_at_path` | R | Yes | Browse items at a category/folder path |
| `create_midi_track` | W | Yes | Create MIDI track at index (-1 = end) |
| `set_track_name` | W | Yes | Rename track by index |
| `create_clip` | W | Yes | Create MIDI clip with specified beat length |
| `add_notes_to_clip` | W | Yes | Add MIDI notes (pitch, start, duration, velocity, mute) |
| `set_clip_name` | W | Yes | Rename a clip |
| `set_tempo` | W | Yes | Set session BPM |
| `load_instrument_or_effect` | X | Yes | Load device by browser URI |
| `fire_clip` | X | Yes | Launch a clip slot |
| `stop_clip` | X | Yes | Stop a clip slot |
| `start_playback` | X | Yes | Start session playback |
| `stop_playback` | X | Yes | Stop session playback |
| **`load_drum_kit`** | **X** | **No** | **Load drum rack URI, then load specific kit from browser path** |

**Only `load_drum_kit` is unique to the extended version at the MCP layer.**

---

## Remote Script Commands (Implemented, NOT Exposed as MCP Tools)

These are the genuinely valuable additions — callable via raw TCP socket but invisible to
an AI assistant using standard MCP:

### Track Management
| Command | R/W/X | Description |
|---------|-------|-------------|
| `create_audio_track` | W | Create audio track (not just MIDI) |
| `set_track_level` | W | Set track volume |
| `set_track_pan` | W | Set track panning |

### Device/Parameter Control
| Command | R/W/X | Description |
|---------|-------|-------------|
| `get_device_parameters` | R | Read all params for a device (normalized 0.0–1.0) |
| `set_device_parameter` | W | Set single device parameter |
| `batch_set_device_parameters` | W | Set multiple parameters at once |

### Note Editing
| Command | R/W/X | Description |
|---------|-------|-------------|
| `delete_notes_from_clip` | W | Remove notes from a clip |
| `transpose_notes_in_clip` | W | Shift note pitches |
| `batch_edit_notes_in_clip` | W | Bulk note modifications |
| `quantize_notes_in_clip` | X | Snap notes to grid |
| `randomize_note_timing` | W | Humanize note positions |
| `set_note_probability` | W | Set per-note trigger probability |

### Clip Configuration
| Command | R/W/X | Description |
|---------|-------|-------------|
| `set_clip_loop_parameters` | W | Configure loop start/end/on-off |
| `set_clip_follow_action` | W | Set clip follow actions |

### Automation
| Command | R/W/X | Description |
|---------|-------|-------------|
| `add_clip_envelope_point` | W | Add automation breakpoint |
| `clear_clip_envelope` | W | Remove clip automation |

### Audio & Scenes
| Command | R/W/X | Description |
|---------|-------|-------------|
| `import_audio_file` | W | Import audio into a track |
| `create_scene` | W | Create new scene |
| `set_scene_name` | W | Rename scene |
| `delete_scene` | W | Remove scene |
| `fire_scene` | X | Launch scene |

---

## Bundled Extras

### ElevenLabs MCP Server (19 tools, separate process)

A standalone MCP server for ElevenLabs voice/audio APIs, bundled in `elevenlabs_mcp/`.
Requires `ELEVENLABS_API_KEY`. Output defaults to Ableton's User Library for immediate import.

Key tools: `text_to_speech`, `text_to_sound_effects`, `speech_to_speech`, `voice_clone`,
`isolate_audio`, `speech_to_text`.

Not deeply integrated with the Ableton MCP server — a convenience bundle.

### XY Mouse Controller (experimental)

`experimental_tools/xy_mouse_controller/` — Standalone Python script that maps mouse X/Y
coordinates to two Ableton device parameters via UDP at ~50 Hz. Bypasses AI assistant entirely.
Uses `pynput` + `screeninfo`.

---

## Value Assessment for Agent Pipeline

### For analyzing/understanding/giving feedback on projects: Limited

- No analysis tools (no spectral analysis, mixing feedback, arrangement review)
- No read access to audio content, waveforms, or plugin state beyond parameter names/values
- `get_device_parameters` (normalized 0–1) is the closest thing to mix inspection, and it's
  not even exposed as an MCP tool
- `get_session_info` + `get_track_info` provide structural overview but no audio-level insight

### For creating/modifying projects: Moderate improvement over base

The remote script additions (mixing, note editing, scenes, automation, audio import) are real
capability gains — but they're trapped behind the MCP tool registration gap.

### Key reference value

The `AbletonMCP_Remote_Script/__init__.py` (45KB) is a solid reference implementation of
expanded Live API command handling. Useful as a pattern library if building custom MCP tools.

---

## Maturity & Maintenance

- **30 commits total**, almost all README/docs updates
- **4 open issues**
- **1 external contributor** (installation doc fix)
- **Assessment:** Low-activity project. The remote script extensions are substantial code but
  feel unfinished — implemented at the Live API layer but never plumbed through to MCP tool
  registration. The gap between remote script capabilities and MCP tool surface is the defining
  characteristic of this repo.

---

## Key Takeaways

1. **The delta over ahujasid/ableton-mcp is mostly unrealized.** Only 1 new MCP tool (`load_drum_kit`).
2. **The remote script is the real asset** — ~15 additional command handlers covering mixing,
   note editing, automation, scenes, and device parameters.
3. **No analysis capabilities.** This is a control/creation tool, not an inspection/feedback tool.
4. **UDP transport** is architecturally interesting for real-time parameter control but niche.
5. **ElevenLabs bundle** is orthogonal — useful for voice/SFX generation, not project analysis.
6. **For our pipeline:** Use the remote script as a reference for Live API patterns. The MCP
   tool wrappers would need to be written (or the unwired commands exposed) to be useful.
