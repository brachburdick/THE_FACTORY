# ahujasid/ableton-mcp — Research Report

> **Date:** 2026-03-20
> **Source:** https://github.com/ahujasid/ableton-mcp
> **Purpose:** Evaluate for use in an AI agent pipeline that reads, analyzes, and gives feedback on Ableton Live projects.

## TL;DR

ahujasid/ableton-mcp is the **original** MCP server for Ableton Live (~2,300 stars, MIT). jpoindexter's version is a **fork** that expanded 16 tools to ~90. For an agent pipeline that needs to *read and analyze* existing projects, **ahujasid is insufficient** — it can write MIDI notes but cannot read them back, and lacks device parameter inspection, scene management, and return track visibility. **Use jpoindexter/ableton-mcp instead.**

---

## 1. Architecture

Both repos share the same fundamental architecture (jpoindexter forked ahujasid):

- **Custom Remote Script** (`_Framework.ControlSurface`) runs inside Ableton's embedded Python interpreter
- **TCP socket** on `localhost:9877` — JSON request/response protocol
- **FastMCP** stdio server connects as a TCP client
- No AbletonOSC, no Max for Live, no third-party bridge

### ahujasid-specific weaknesses

- Health check uses fragile `sendall(b'')` (jpoindexter replaced with proper `health_check` command)
- No thread-safety lock on the connection
- Hard-coded timeouts (jpoindexter uses env vars)
- No test suite

### Dependencies

- `mcp[cli]>=1.3.0` — the only runtime dependency
- Python 3.10+
- No FastAPI, no OSC libs, no audio libs

### Connection Flow

```
Claude Desktop (stdio) → FastMCP server → TCP socket → Remote Script (inside Ableton)
```

State-modifying calls are dispatched to Ableton's main thread via `schedule_message(0, fn)` plus a `queue.Queue` for response synchronization (10-second timeout).

---

## 2. Tool Inventory (16 tools)

### Transport / Session (4 tools)

| Tool | R/W | Notes |
|---|---|---|
| `get_session_info()` | R | tempo, time sig, track count, master vol/pan |
| `set_tempo(tempo)` | W | |
| `start_playback()` | W | |
| `stop_playback()` | W | |

### Tracks (3 tools)

| Tool | R/W | Notes |
|---|---|---|
| `get_track_info(track_index)` | R | name, type, mute/solo/arm, vol/pan, clip slots, device names |
| `create_midi_track(index)` | W | No audio track creation |
| `set_track_name(track_index, name)` | W | |

### Clips (4 tools)

| Tool | R/W | Notes |
|---|---|---|
| `create_clip(track_index, clip_index, length)` | W | |
| `set_clip_name(track_index, clip_index, name)` | W | |
| `fire_clip(track_index, clip_index)` | W | |
| `stop_clip(track_index, clip_index)` | W | |

### MIDI (1 tool)

| Tool | R/W | Notes |
|---|---|---|
| `add_notes_to_clip(track_index, clip_index, notes)` | W | **Cannot read notes back** |

Note format: `{pitch, start_time, duration, velocity, mute}`

### Browser / Device Loading (4 tools)

| Tool | R/W | Notes |
|---|---|---|
| `get_browser_tree(category_type)` | R | instruments, sounds, drums, audio_effects, midi_effects |
| `get_browser_items_at_path(path)` | R | Path format: `"category/folder/subfolder"` |
| `load_instrument_or_effect(track_index, uri)` | W | URI-based loading via recursive browser traversal |
| `load_drum_kit(track_index, rack_uri, kit_path)` | W | Two-step: load rack, then find and load kit |

### Missing Categories (no tools at all)

- **Devices:** No parameter read/write (`set_device_parameter` exists in the command router but has no MCP tool)
- **Mixer:** No volume/pan/mute/solo setters
- **Scenes:** No scene management
- **Return/Send tracks:** No visibility
- **Arrangement view:** Nothing
- **Recording:** Nothing
- **Warp/Groove:** Nothing
- **Routing:** Nothing
- **Undo/Redo:** Nothing

---

## 3. Data Shapes

### `get_session_info` returns

```json
{
  "tempo": 120.0,
  "signature_numerator": 4,
  "signature_denominator": 4,
  "track_count": 8,
  "return_track_count": 2,
  "master_track": { "name": "Master", "volume": 0.85, "panning": 0.0 }
}
```

### `get_track_info` returns

```json
{
  "index": 0,
  "name": "Bass",
  "is_audio_track": false,
  "is_midi_track": true,
  "mute": false,
  "solo": false,
  "arm": false,
  "volume": 0.85,
  "panning": 0.0,
  "clip_slots": [
    { "index": 0, "has_clip": true, "clip": { "name": "Clip 1", "length": 4.0, "is_playing": false, "is_recording": false } }
  ],
  "devices": [
    { "index": 0, "name": "Analog", "class_name": "PluginDevice", "type": "instrument" }
  ]
}
```

---

## 4. Differentiation vs jpoindexter/ableton-mcp

### What ahujasid has that jpoindexter doesn't

**Nothing.** jpoindexter is a strict superset.

### What jpoindexter adds (~74 additional tools)

| Category | Key additions |
|---|---|
| MIDI | `get_clip_notes`, `remove_notes`, `transpose_notes`, `quantize_clip_notes`, `humanize_*` |
| Devices | `get_device_parameters`, `set_device_parameter`, `toggle_device`, rack chain access |
| Mixer | Full vol/pan/mute/solo/arm setters, send levels, return tracks, master control |
| Scenes | Full CRUD + fire/stop/duplicate |
| Arrangement | Length, loop, locators, jump-to-time |
| Clips | Delete, duplicate, loop, gain, pitch, warp mode, automation r/w |
| Tracks | Audio creation, delete, duplicate, freeze/flatten, group, monitoring, color, routing |
| Recording | Start/stop, session/arrangement record, overdub, capture MIDI |
| AI helpers | `generate_drum_pattern`, `generate_bassline`, `get_scale_notes` |
| Infra | REST API server (FastAPI), Max for Live device, test suite, undo/redo |

### Relationship

jpoindexter is a **fork** of ahujasid. Same TCP protocol, same remote script pattern, heavily extended. Not an independent implementation.

---

## 5. Maturity

| Metric | ahujasid | jpoindexter |
|---|---|---|
| Stars | ~2,300 | ~7 |
| Forks | ~288 | ~2 |
| Contributors | 4 | 1 |
| License | MIT | MIT |
| Open issues | 28 | 0 |
| Version | 1.0.0 | 2.0.0 |
| Tests | None | Yes (pytest) |
| REST API | No | Yes (FastAPI) |
| Max for Live | No | Yes |

ahujasid has far more community visibility but appears to have plateaued — 28 open issues and a significant feature gap suggest maintenance-mode. jpoindexter is lower-profile but substantially more capable.

---

## 6. Agent Fitness

### For reading/analyzing an existing Ableton project

**ahujasid: Insufficient.** An agent can see:
- Track names, types, device chain names (names only, no parameter values)
- Clip existence (name, length, playing state)
- Session-level metadata (tempo, time sig)

An agent **cannot** see: MIDI note content, device parameter values, send/return routing, scene structure, arrangement layout, warp settings, or automation.

**jpoindexter: Substantially better.** Adds `get_clip_notes`, `get_device_parameters`, return track inspection, scene enumeration, arrangement view, warp info, and routing visibility.

### Remaining gap (both repos)

Neither can export audio, analyze frequency content, or provide sonic feedback. A real-world experiment (John Hurliman, Dec 2025) found that meaningful production feedback required custom audio analysis endpoints + Max4Live WAV export to close the "the model can't hear" loop.

---

## 7. Recommendation

**Use jpoindexter/ableton-mcp as the foundation.** ahujasid is only relevant as historical context. For the "give feedback on a project" goal, the critical path is:

1. **jpoindexter** for structural/MIDI/device/mixer read access (~90 tools)
2. **Audio analysis pipeline** for sonic analysis the MCP can't provide
3. **Custom tools** for automation reading and audio content inspection (neither repo covers these)

---

## References

- [ahujasid/ableton-mcp](https://github.com/ahujasid/ableton-mcp)
- [jpoindexter/ableton-mcp](https://github.com/jpoindexter/ableton-mcp)
- [Experiments with ableton-mcp (Dec 2025) — John Hurliman](https://jhurliman.org/post/804323197731373056/experiments-with-ableton-mcp-dec-2025)
- [Ableton Live MCP Server — PulseMCP](https://www.pulsemcp.com/servers/ahujasid-ableton-live)
