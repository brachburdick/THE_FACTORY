# Deep Dive: jpoindexter/ableton-mcp

> **Repo:** https://github.com/jpoindexter/ableton-mcp
> **Version:** 2.0.0 | **License:** MIT | **Python:** ≥3.10
> **Stars:** 7 | **Forks:** 2 | **Contributors:** 4 | **Last commit:** 2026-02-09
> **Researched:** 2026-03-20

---

## 1. Tool Inventory

The MCP server exposes **~128 tools** via `@mcp.tool()` decorators. The Remote Script behind it supports **200+ commands** — the gap represents lower-level LOM operations not yet surfaced as MCP tools (drum pads, Simpler/Sampler params, follow actions, crossfader, etc.).

### 1.1 Transport & Session (10 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `health_check` | R | Check if Ableton is connected |
| `get_playback_position` | R | Current position + transport state |
| `get_session_info` | R | Full session details (tracks, scenes, tempo, time sig) |
| `start_playback` | X | Play |
| `stop_playback` | X | Stop |
| `start_recording` | X | Start recording |
| `stop_recording` | X | Stop recording |
| `toggle_session_record` | X | Toggle session record mode |
| `toggle_arrangement_record` | X | Toggle arrangement record mode |
| `set_overdub` | W | Enable/disable overdub |

### 1.2 Track Management (18 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `get_track_info` | R | Full track details (name, type, devices, clips, volume, pan, mute, solo, arm) |
| `get_track_color` | R | Track color index |
| `get_track_monitoring` | R | Monitoring mode (in/auto/off) |
| `create_midi_track` | X | Create MIDI track at index |
| `create_audio_track` | X | Create audio track at index |
| `set_track_name` | W | Rename track |
| `set_track_mute` | W | Mute/unmute |
| `set_track_solo` | W | Solo/unsolo |
| `set_track_arm` | W | Arm/disarm for recording |
| `set_track_volume` | W | Volume (0.0–1.0) |
| `set_track_pan` | W | Pan (-1.0 to 1.0) |
| `set_track_color` | W | Color (0–69 palette) |
| `set_track_monitoring` | W | Monitoring mode |
| `delete_track` | X | Delete track |
| `duplicate_track` | X | Duplicate with clips/devices |
| `freeze_track` | X | Freeze for CPU |
| `flatten_track` | X | Flatten frozen track to audio |
| `unarm_all` | X | Unarm all tracks |

### 1.3 Clip Operations (12 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `create_clip` | X | Create MIDI clip (track, slot, length) |
| `delete_clip` | X | Delete clip |
| `duplicate_clip` | X | Duplicate to next empty slot |
| `fire_clip` | X | Launch clip |
| `stop_clip` | X | Stop clip |
| `select_clip` | X | Select a clip slot |
| `capture_midi` | X | Capture recently played MIDI |
| `set_clip_name` | W | Rename clip |
| `set_clip_color` | W | Set clip color |
| `set_clip_loop` | W | Set loop start/end/enabled |
| `get_clip_color` | R | Get clip color |
| `get_clip_loop` | R | Get loop settings |

### 1.4 MIDI Note Editing (8 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `get_clip_notes` | R | Get all MIDI notes from clip |
| `add_notes_to_clip` | W | Add notes (pitch, start, duration, velocity, mute) |
| `remove_notes` | W | Remove notes in pitch/time range |
| `remove_all_notes` | W | Clear all notes |
| `transpose_notes` | W | Transpose by semitones |
| `quantize_clip_notes` | W | Quantize to grid (default 1/16) |
| `humanize_clip_timing` | W | Random timing variation |
| `humanize_clip_velocity` | W | Random velocity variation |

**Example MCP tool call — add notes:**
```json
{
  "name": "add_notes_to_clip",
  "arguments": {
    "track_index": 0,
    "clip_index": 0,
    "notes": [
      {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100, "mute": false},
      {"pitch": 64, "start_time": 0.5, "duration": 0.5, "velocity": 90, "mute": false},
      {"pitch": 67, "start_time": 1.0, "duration": 1.0, "velocity": 80, "mute": false}
    ]
  }
}
```

### 1.5 Audio Clip Editing (8 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `get_clip_gain` | R | Audio clip gain |
| `set_clip_gain` | W | Gain in dB |
| `get_clip_pitch` | R | Pitch shift info |
| `set_clip_pitch` | W | Pitch shift (-48 to +48 semitones) |
| `get_clip_warp_info` | R | Warp mode and settings |
| `get_warp_markers` | R | All warp markers |
| `set_clip_warp_mode` | W | Warp mode (beats/tones/texture/repitch/complex/complex_pro) |
| `add_warp_marker` | W | Add warp marker at beat/sample time |
| `delete_warp_marker` | W | Delete warp marker |

### 1.6 Clip Automation (3 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `get_clip_automation` | R | Read automation envelope for parameter |
| `set_clip_automation` | W | Write automation envelope |
| `clear_clip_automation` | X | Clear automation for parameter |

### 1.7 Device Management (8 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `get_device_parameters` | R | All parameters for a device |
| `get_device_by_name` | R | Find device by name on track |
| `set_device_parameter` | W | Set parameter value |
| `toggle_device` | W | Toggle on/off |
| `load_instrument_or_effect` | X | Load by browser URI |
| `move_device_left` | X | Reorder device chain |
| `move_device_right` | X | Reorder device chain |
| `delete_device` | X | Remove device |

### 1.8 Rack Devices (2 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `get_rack_chains` | R | Get chains from instrument/effect rack |
| `select_rack_chain` | X | Select chain in rack |

### 1.9 Scene Management (9 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `get_all_scenes` | R | All scene names, colors, clip counts |
| `get_scene_color` | R | Scene color |
| `create_scene` | X | Create scene at index |
| `delete_scene` | X | Delete scene |
| `duplicate_scene` | X | Duplicate scene |
| `fire_scene` | X | Launch scene |
| `stop_scene` | X | Stop scene |
| `set_scene_name` | W | Rename scene |
| `set_scene_color` | W | Set scene color |
| `select_scene` | X | Select scene |

### 1.10 Return Tracks & Sends (5 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `get_return_tracks` | R | All return track info |
| `get_return_track_info` | R | Single return track details |
| `get_send_level` | R | Send level for track→return |
| `set_send_level` | W | Set send level (0.0–1.0) |
| `set_return_volume` | W | Return track volume |
| `set_return_pan` | W | Return track pan |

### 1.11 I/O Routing (6 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `get_track_input_routing` | R | Current input routing |
| `get_track_output_routing` | R | Current output routing |
| `get_available_inputs` | R | Available input options |
| `get_available_outputs` | R | Available output options |
| `set_track_input_routing` | W | Set input routing type + channel |
| `set_track_output_routing` | W | Set output routing type + channel |

### 1.12 Arrangement (6 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `get_arrangement_length` | R | Length + loop settings |
| `get_locators` | R | All locators/cue points |
| `set_arrangement_loop` | W | Set loop start/end/enabled |
| `jump_to_time` | X | Jump to position in beats |
| `create_locator` | X | Create locator at time with name |
| `delete_locator` | X | Delete locator by index |

### 1.13 View & Navigation (4 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `get_current_view` | R | Current view state |
| `focus_view` | X | Focus Session/Arranger/Detail |
| `select_track` | X | Select track |
| `set_tempo` | W | Set session tempo |

### 1.14 Master Track (3 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `get_master_info` | R | Master volume, pan, devices |
| `set_master_volume` | W | Master volume (0.0–1.0) |
| `set_master_pan` | W | Master pan (-1.0 to 1.0) |

### 1.15 Browser (6 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `get_browser_tree` | R | Hierarchical browser categories |
| `get_browser_items_at_path` | R | Items at browser path |
| `search_browser` | R | Search browser items by query |
| `browse_path` | R | Navigate browser by path list |
| `load_item_to_track` | X | Load browser item by URI to track |
| `load_item_to_return` | X | Load browser item by URI to return track |
| `load_drum_kit` | X | Load drum rack + kit |

### 1.16 System & Utility (7 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `undo` | X | Undo last operation |
| `redo` | X | Redo last undone |
| `get_cpu_load` | R | Current CPU load |
| `get_session_path` | R | Session file path |
| `is_session_modified` | R | Unsaved changes check |
| `get_metronome_state` | R | Metronome on/off |
| `set_metronome` | W | Enable/disable metronome |

### 1.17 AI Music Helpers (3 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `get_scale_notes` | R | Notes in scale (13 scale types: major, minor, dorian, phrygian, lydian, mixolydian, locrian, harmonic_minor, melodic_minor, pentatonic_major, pentatonic_minor, blues, chromatic) |
| `generate_drum_pattern` | W | Generate pattern (styles: basic, house, hiphop, dnb, random) |
| `generate_bassline` | W | Generate bassline (root, scale, length) |

### 1.18 Group Tracks (3 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `create_group_track` | X | Group tracks by indices with name |
| `fold_track` | X | Collapse group |
| `unfold_track` | X | Expand group |

### 1.19 Groove (3 tools)

| Tool | R/W/X | Description |
|------|-------|-------------|
| `get_groove_pool` | R | Available grooves |
| `apply_groove` | W | Apply groove to clip |
| `commit_groove` | X | Commit groove permanently |

### 1.20 Remote Script-Only Commands (not surfaced as MCP tools)

The Remote Script supports additional commands not exposed via MCP:

- **Drum Rack Pads:** mute/solo/get pad name
- **Simpler/Sampler:** get sample info, parameters
- **Clip Launch Modes:** get/set launch mode, follow actions
- **Clip Fades:** get/set fade in/out
- **Crossfader:** get/set assignment, position
- **Song Properties:** root note, scale name, swing amount
- **Punch In/Out:** enable/disable
- **Count-In:** get/set duration
- **Exclusive Modes:** solo/arm exclusivity
- **Track Metering:** output meter values
- **Clip Properties:** RAM mode, velocity amount
- **Grid Quantization:** get/set grid size
- **Draw Mode / Follow / Zoom:** arrangement view controls

### Summary by Domain

| Domain | READ | WRITE | EXECUTE | Total |
|--------|------|-------|---------|-------|
| Transport & Session | 3 | 1 | 6 | 10 |
| Track Management | 3 | 8 | 7 | 18 |
| Clip Operations | 2 | 3 | 7 | 12 |
| MIDI Editing | 1 | 7 | 0 | 8 |
| Audio Clips | 4 | 4 | 0 | 8 |
| Clip Automation | 1 | 1 | 1 | 3 |
| Devices | 2 | 2 | 4 | 8 |
| Racks | 1 | 0 | 1 | 2 |
| Scenes | 2 | 2 | 5 | 9 |
| Returns & Sends | 3 | 3 | 0 | 6 |
| Routing | 4 | 2 | 0 | 6 |
| Arrangement | 2 | 1 | 3 | 6 |
| View & Navigation | 1 | 1 | 2 | 4 |
| Master | 1 | 2 | 0 | 3 |
| Browser | 4 | 0 | 3 | 7 |
| System & Utility | 3 | 1 | 2 | 6 (+1) |
| AI Helpers | 1 | 2 | 0 | 3 |
| Groups | 0 | 0 | 3 | 3 |
| Groove | 1 | 1 | 1 | 3 |
| **TOTAL** | **~39** | **~41** | **~45** | **~128** |

---

## 2. Architecture

### Communication Stack

```
┌─────────────────────────────────────────────────┐
│  Claude / MCP Client                            │
│  (Claude Desktop, Claude Code, Cursor, etc.)    │
└────────────────────┬────────────────────────────┘
                     │ stdio (MCP protocol, JSON-RPC)
                     ▼
┌─────────────────────────────────────────────────┐
│  MCP Server (MCP_Server/server.py)              │
│  FastMCP framework, ~2828 lines                 │
│  Python 3.10+, dep: mcp[cli]>=1.3.0            │
└────────────────────┬────────────────────────────┘
                     │ TCP socket (localhost:9877)
                     │ JSON command protocol
                     ▼
┌─────────────────────────────────────────────────┐
│  Ableton Remote Script                          │
│  (AbletonMCP_Remote_Script/__init__.py)         │
│  Runs inside Ableton Live as Control Surface    │
│  TCP server on port 9877                        │
│  Thread-safe: write ops → schedule_message()    │
└────────────────────┬────────────────────────────┘
                     │ Ableton Live Python API (LOM)
                     ▼
┌─────────────────────────────────────────────────┐
│  Ableton Live Session                           │
│  Live Object Model (tracks, clips, devices...)  │
└─────────────────────────────────────────────────┘
```

### Key Architectural Decisions

**Not AbletonOSC.** This project uses its own custom Remote Script with a TCP JSON protocol. It does NOT depend on the AbletonOSC project or any OSC protocol. The Remote Script is a Python Control Surface that runs inside Ableton and accepts JSON commands over TCP.

**Thread safety.** Read-only commands execute on the client handler thread. Write commands are scheduled to Ableton's main thread via `schedule_message()` for thread safety.

**Auto-reconnect.** The `AbletonConnection` class manages a persistent TCP socket with auto-reconnect, buffered responses (up to 1MB), and configurable timeouts (default 15s receive).

### Max4Live Device (Alternative Path)

The M4L device (`AbletonMCP_M4L/`) is a **separate integration path** — NOT required for MCP. It contains a Node for Max script (`main.js`) that talks directly to LLM providers (Ollama, OpenAI, Anthropic, Groq) via their HTTP APIs. It provides its own tool definitions and maintains a 20-message conversation history. This is a self-contained "chat with your DAW inside Ableton" experience.

### REST API (Optional)

`MCP_Server/rest_api_server.py` is a FastAPI application (optional, `pip install ableton-mcp[rest]`) on `localhost:8000`:

- **180+ endpoints** as RESTful resources
- `GET /tools` — returns tool definitions compatible with Claude/OpenAI/Ollama function calling
- `POST /api/command` — generic endpoint: `{command, params}` JSON
- **Security:** API key auth (`X-API-Key`), rate limiting (100 req/min), command whitelist, CORS (localhost only)
- **Cannot run headless** — requires Ableton Live running with the Remote Script active

---

## 3. MCP Protocol Compliance

### Tool Definitions

- Uses `@mcp.tool()` decorators from the `FastMCP` framework (`mcp[cli]>=1.3.0`)
- **Well-typed:** All tools have proper Python type hints on parameters (int, float, bool, str, List[Dict])
- **Described:** Each tool has a docstring that serves as the MCP tool description
- All tools are synchronous (`def`, not `async def`) with `ctx: Context` injected by FastMCP
- Input validation happens at both the MCP server level (Python types) and the Remote Script level (parameter bounds)

### Error Handling

- Tools return structured error messages on failure
- Connection errors trigger auto-reconnect
- The Remote Script validates commands against a whitelist
- REST API adds additional rate limiting and parameter bounds checking

### MCP Resources & Prompts

- **Resources:** Not implemented. No `@mcp.resource()` decorators found.
- **Prompts:** Not implemented. No `@mcp.prompt()` decorators found.
- This is a tools-only MCP server — no resource URIs, no prompt templates.

### Protocol Transport

- **stdio transport** (standard for Claude Desktop / Cursor / Claude Code integration)
- No SSE or WebSocket transport option

---

## 4. Agent Workflow Fitness

### Can an agent analyze project structure?

**Yes, reasonably well.** Using these tools in sequence:
1. `get_session_info` → track count, scene count, tempo, time signature
2. `get_track_info` (per track) → name, type, device chain, clip count, volume/pan/mute/solo
3. `get_all_scenes` → scene names and structure
4. `get_clip_notes` (per MIDI clip) → full note content
5. `get_device_parameters` (per device) → all parameter values
6. `get_arrangement_length` + `get_locators` → arrangement structure

**Limitation:** No single "dump everything" tool. An agent must make N tool calls to scan N tracks, which gets expensive for large sessions (e.g., 50+ tracks × 10+ devices each).

### Can an agent give mixing feedback?

**Partially.** It can read:
- Track volumes, pans, mute/solo states
- Device parameters (EQ, compressor settings)
- Send levels, return track configurations
- Master volume/pan

**Missing for proper mix analysis:**
- No spectral analysis or frequency content data
- No peak/RMS metering (Remote Script has `get_output_meter` but it's not surfaced as MCP tool)
- No audio file reading or waveform access
- No ability to A/B compare settings

### Can an agent write MIDI?

**Yes.** Full MIDI note CRUD:
- `create_clip` → `add_notes_to_clip` → write arbitrary MIDI
- `get_clip_notes` → read existing, analyze, modify
- `transpose_notes`, `quantize_clip_notes`, `humanize_clip_timing/velocity`
- AI helpers: `generate_drum_pattern`, `generate_bassline`, `get_scale_notes`

**Example workflow — generate a chord progression:**
```json
// 1. Create clip
{"name": "create_clip", "arguments": {"track_index": 0, "clip_index": 0, "length": 8.0}}

// 2. Add C major chord (C4-E4-G4)
{"name": "add_notes_to_clip", "arguments": {
  "track_index": 0, "clip_index": 0,
  "notes": [
    {"pitch": 60, "start_time": 0.0, "duration": 2.0, "velocity": 80},
    {"pitch": 64, "start_time": 0.0, "duration": 2.0, "velocity": 75},
    {"pitch": 67, "start_time": 0.0, "duration": 2.0, "velocity": 70}
  ]
}}
```

### Can an agent suggest arrangement changes?

**Partially.** It can:
- Read arrangement length, locators, scene structure
- Create/delete/duplicate/reorder scenes
- Fire scenes (triggering arrangement ideas)
- Create/move locators as section markers

**Cannot:**
- Move clips between arrangement positions (no arrangement clip manipulation)
- Read arrangement view clip positions
- Compare two versions of a project

### Latency

- TCP socket on localhost → sub-millisecond network overhead
- Simple read operations (get_track_info): likely **5–50ms**
- State-modifying operations: scheduled to Ableton's main thread, **50–200ms**
- Full project dump (30 tracks × get_track_info + device params): **1–5 seconds** estimated
- No published benchmarks

### Batch Operations

**None.** Every query requires its own tool call. No `get_all_tracks_info` or `get_project_snapshot`. This is the biggest agent workflow gap — scanning a large project requires O(tracks × devices) individual tool calls.

---

## 5. Maturity & Maintenance

| Signal | Assessment |
|--------|-----------|
| **Age** | Created 2026-01-27 (~7 weeks ago) |
| **Last commit** | 2026-02-09 (5 weeks dormant) |
| **Commit pattern** | Massive 2-day sprint (Jan 27-28), then docs polish (Feb 9) |
| **Contributors** | 4 (jpoindexter: 28 commits, ahujasid: 17, calclavia: 3, Ronbalt: 3) |
| **Issues** | 0 open, 0 closed (zero community interaction) |
| **Releases** | None (no semver tags, no changelog) |
| **Tests** | Present (unit + integration), but test depth unclear |
| **Docs** | Comprehensive (API_REFERENCE.md, CONFIG.md, MANUAL.md, TOOLS.md, TROUBLESHOOTING.md) |
| **CI/CD** | Dockerfile present, no GitHub Actions visible |

**Verdict: Experimental / proof-of-concept.** Impressive scope, but the "everything in 2 days" pattern + zero community interaction + no releases = not production-ready. The code appears to be largely AI-generated given the velocity.

### Security Considerations

The REST API exposes `localhost:8000` with:
- Optional API key auth (off by default)
- Rate limiting (100 req/min)
- CORS restricted to localhost
- Command whitelist validation

**Risks:**
- Default config has no auth — any local process can control Ableton
- Remote Script on port 9877 has no auth at all — raw TCP, no TLS
- If either port is exposed beyond localhost (e.g., via tunnel), full DAW control is open
- No input sanitization audit visible (potential for crafted JSON to abuse LOM)

---

## 6. Setup Complexity

### Minimum Setup (MCP Server + Claude)

1. **Install Remote Script:**
   - Copy `AbletonMCP_Remote_Script/__init__.py` to `~/Music/Ableton/User Library/Remote Scripts/AbletonMCP/`
   - In Ableton: Preferences → Link/Tempo/MIDI → Control Surface → AbletonMCP
   - Input/Output: None

2. **Configure Claude Desktop/Code:**
   ```json
   {
     "mcpServers": {
       "ableton-mcp": {
         "command": "uvx",
         "args": ["ableton-mcp"]
       }
     }
   }
   ```

3. **That's it.** `uvx` handles the Python package. No manual pip install needed.

### Alternative: Smithery
```bash
npx -y @smithery/cli install @ahujasid/ableton-mcp --client claude
```

### REST API Setup (additional)
```bash
pip install ableton-mcp[rest]
python -m MCP_Server.rest_api_server  # localhost:8000
```

### Max4Live Device (standalone, no MCP)
- Copy `AbletonMCP_M4L/` to User Library
- Build: `python3 scripts/build_amxd.py`
- Drag `.amxd` onto any track
- Configure LLM provider in device UI

### Claude Code Compatibility

**Should work out of the box** — the MCP server uses stdio transport, which is what Claude Code expects. The `uvx` launcher pattern is standard. The only requirement is Ableton Live running with the Remote Script active.

---

## 7. Key Takeaways

### Strengths
- **Broad LOM coverage** — 128 MCP tools + 200+ Remote Script commands covers most of what Ableton exposes
- **Three integration paths** — MCP (Claude), REST (any LLM), M4L (in-DAW chat)
- **Clean architecture** — Remote Script ↔ TCP ↔ MCP server is a reasonable design
- **MIDI write capability** — full note CRUD, generation helpers, quantize/humanize
- **Simple setup** — `uvx ableton-mcp` + install Remote Script

### Weaknesses
- **No batch/snapshot operations** — scanning large projects is O(N) tool calls
- **No audio analysis** — can't read waveforms, spectra, or audio file content
- **No arrangement clip manipulation** — session view only for clip operations
- **Missing MCP resources/prompts** — tools-only, no semantic resource URIs
- **No metering exposed** — Remote Script has it, MCP server doesn't surface it
- **Immature** — 7 weeks old, zero issues, zero releases, dormant for 5 weeks
- **No streaming** — all responses are synchronous, no progress callbacks for long operations

### For Your Agent Pipeline

If building agents that read/understand/write/give-feedback on Ableton projects:

1. **Reading:** Good coverage for structure (tracks, clips, devices, scenes). Poor for audio content (no waveform/spectral data). You'd need a complementary tool for audio analysis.

2. **Understanding:** You can reconstruct the project graph (tracks → clips → notes, tracks → devices → parameters), but there's no single "project snapshot" — you'd want to build a batch wrapper.

3. **Writing:** Strong for MIDI. Can create tracks, clips, add notes, load instruments. Can't write audio or manipulate arrangement clips.

4. **Feedback:** Can read mix state (volumes, pans, device params, sends). Can't do spectral analysis or metering. Mix feedback would be structural ("your kick and bass are on the same channel with no EQ") not perceptual ("your mix is muddy at 200Hz").

5. **Recommendation:** Fork the Remote Script and MCP server. Add: (a) batch `get_project_snapshot` tool, (b) surface metering tools, (c) arrangement clip read/write, (d) MCP resources for project state. The Remote Script already handles more commands than the MCP server exposes — the gap is just wiring.
