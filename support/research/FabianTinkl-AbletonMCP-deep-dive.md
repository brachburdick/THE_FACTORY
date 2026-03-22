# Deep Dive: FabianTinkl/AbletonMCP

**Date:** 2026-03-20
**Repo:** https://github.com/FabianTinkl/AbletonMCP
**Stars:** 7 | **Forks:** 1 | **Language:** Python | **License:** None
**Created:** 2025-09-15 | **Last pushed:** 2025-09-16 | **Last metadata update:** 2026-03-17
**Status:** Effectively abandoned (1 day of active development, no commits in 6 months)

---

## 1. MIDI Composition Capabilities (Primary Focus)

### 1.1 What MIDI Tools Are Exposed

The MCP server exposes three MIDI-specific tools via FastMCP:

| MCP Tool | Handler Method | What It Does |
|---|---|---|
| `create_midi_clip` | `MIDIHandler.create_midi_clip()` | Creates empty clip with scale constraints |
| `generate_melody` | `MIDIHandler.generate_melody()` | Algorithmic melody within scale/density params |
| `generate_drum_pattern` | `MIDIHandler.drum_pattern()` | Style-based drum pattern generation |

Under the hood, the `AbletonTools` class also exposes `add_notes_to_clip()` which is used internally but **is registered as an MCP tool** in `main.py` for direct note-level control.

### 1.2 Granularity of Control

**Note-level operations (via OSC):**

```python
# Add a single note — this is the atomic operation
await osc_client.add_notes(
    track_idx=0,       # track index
    clip_idx=0,        # clip slot index
    pitch=60,          # MIDI note (C4)
    start_time=0.0,    # position in beats
    duration=0.5,      # length in beats
    velocity=100,      # 0-127
    mute=False         # note mute flag
)

# Read notes back (with optional range filtering)
notes = await osc_client.get_notes(
    track_idx=0, clip_idx=0,
    start_time=0.0, time_span=4.0,    # beat range
    start_pitch=36, pitch_span=84      # pitch range
)

# Remove specific notes
await osc_client.remove_notes(track_idx=0, clip_idx=0, pitch=60, start_time=0.0, duration=0.5)

# Clear all notes
await osc_client.clear_all_notes(track_idx=0, clip_idx=0)
```

**MCP tool call example — adding notes via the `add_notes_to_clip` tool:**

```json
{
  "tool": "add_notes_to_clip",
  "arguments": {
    "track_idx": 0,
    "clip_idx": 0,
    "notes": [
      {"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100},
      {"pitch": 64, "start_time": 0.5, "duration": 0.5, "velocity": 90},
      {"pitch": 67, "start_time": 1.0, "duration": 1.0, "velocity": 80},
      {"pitch": 72, "start_time": 2.0, "duration": 0.25, "velocity": 110}
    ]
  }
}
```

**Verdict:** Full note-level granularity — pitch, start_time, duration, velocity, mute. An agent can compose MIDI programmatically at the individual note level. Notes are added one at a time via OSC (no batch send), which means high note counts will be slow but functional.

### 1.3 AI/Generative Features

The `music_ai/generators/` and `music_ai/analyzers/` directories are **empty stubs** (`__init__.py` only). All "AI" composition lives in the handlers:

**`generate_melody` (MIDIHandler):**
- Scale-constrained algorithmic generation using `music21` library
- Stepwise motion logic (biases toward small intervals)
- Configurable density (notes per beat)
- Genre parameter influences pattern selection
- **Not a neural model** — it's rule-based random generation with music theory constraints

**`generate_chord_progression` (CompositionHandler):**
- Hardcoded progressions per key (Am, Dm, Em only)
- Random selection from a small library (~5 progressions per key)
- Returns text description, does NOT write MIDI notes to clips
- Techno/industrial genre focus

**`generate_drum_pattern` (MIDIHandler):**
- 6 style presets: four-on-floor, breakbeat, latin, funk, industrial, jungle
- Uses GM drum mapping (kick=36, snare=38, hh=42/46, etc.)
- Swing timing support via helper method
- Actually writes MIDI notes to clips (unlike chord progression)

**`create_techno_song` (CompositionHandler):**
- Creates track structure (Kick, Bass, Lead Synth, Pad, Percussion, Reverb, Delay returns)
- Sets tempo and defines section layout (intro/buildup/drop/breakdown/outro)
- Does NOT populate clips with MIDI — only creates the scaffolding and returns text instructions

### 1.4 Critical Assessment of MIDI Composition

**What works:**
- Individual note add/remove/read — full CRUD on MIDI notes
- Scale-aware melody generation (basic but functional)
- Drum pattern generation with multiple styles
- Clip creation with configurable length

**What's missing or fake:**
- `generate_chord_progression` only returns text, doesn't write notes
- `create_techno_song` creates tracks but doesn't populate them
- No quantize implementation (tool is declared but handler may be incomplete)
- No note editing (modify velocity/timing of existing notes) — only add/remove
- No CC/automation writing
- No MPE support
- No chord voicing generation (no actual chord-to-MIDI-notes mapping)
- `music_ai/` module is an empty skeleton — the "AI composition engine" marketing is aspirational

---

## 2. Full Tool Inventory

### 2.1 MCP Tools (18 registered)

| Category | Tool | Parameters | Actually Works? |
|---|---|---|---|
| **Transport** | `play` | — | Yes |
| | `stop` | — | Yes |
| | `set_tempo` | `bpm: float` | Yes |
| **Connectivity** | `ping` | — | Yes |
| **Tracks** | `create_track` | `track_type, name` | Yes |
| **Composition** | `generate_chord_progression` | `key, genre, length` | Text only (no MIDI output) |
| | `create_techno_song` | `bpm, bars, style, key` | Partial (creates tracks, no MIDI) |
| **MIDI** | `create_midi_clip` | `track_idx, clip_idx, length, scale` | Yes |
| | `generate_melody` | `track_idx, clip_idx, scale, density, genre` | Yes (rule-based) |
| | `generate_drum_pattern` | `track_idx, clip_idx, style, length` | Yes |
| **Instruments** | `list_instruments` | `category` | Yes (local database) |
| | `load_instrument` | `track_idx, name` | **No** — returns manual instructions |
| **Effects** | `list_effects` | `category` | Yes (local database) |
| | `load_effect` | `track_idx, name, position` | **No** — returns manual instructions |
| **Samples** | `browse_samples` | `category, bpm, key, genre` | Yes (local database) |
| | `load_sample` | `track_idx, path` | **No** — returns manual instructions |

### 2.2 OSC Client Operations (not all exposed as MCP tools)

The `AbletonOSCClient` has ~60 methods. Many are NOT exposed as MCP tools but are available to handlers:

**Exposed only internally (not MCP tools):**
- `add_notes_to_clip` (available as MCP tool via `main.py`)
- `get_notes` — read MIDI notes from a clip
- `set_device_parameter` / `get_device_parameters_name` / `get_device_parameters_value`
- `set_track_volume` / `set_track_panning` / `set_track_mute` / `set_track_solo` / `set_track_arm`
- `fire_clip` / `stop_clip` / `set_clip_name` / `get_clip_length`
- `fire_scene` / `create_scene` / `delete_scene`
- `undo` / `redo`
- `get_current_song_time` / `set_current_song_time`
- `start_listen_beat` / `start_listen_parameter_value` (real-time listeners)
- `get_track_data` / `get_track_names` (bulk queries)

### 2.3 Unique vs Common

**Unique to this implementation:**
- Built-in composition handlers (chord progressions, song structures, drum patterns)
- Music theory knowledge base (hardcoded genre progressions, style characteristics)
- `music21` integration for scale-aware generation
- Genre-specific drum pattern library (6 styles)
- Instrument/effect recommendation engine
- Validation framework for MCP tools
- Effect chain optimization logic (signal flow ordering)

**Common across ableton-mcp variants (also in jpoindexter's):**
- AbletonOSC as the transport layer
- Transport control (play/stop/tempo)
- Track CRUD
- Clip creation and note manipulation
- Device parameter read/write
- Same port pair (11000/11001)

---

## 3. Architecture

### 3.1 Stack

```
┌─────────────────────────────┐
│     Claude Desktop          │
│  (MCP client, natural lang) │
└──────────┬──────────────────┘
           │ stdio (MCP protocol)
┌──────────▼──────────────────┐
│   FastMCP Server (Python)   │
│   mcp_server/main.py        │
│   ├── handlers/              │
│   │   ├── transport.py       │
│   │   ├── track.py           │
│   │   ├── composition.py     │  ← chord/song generation
│   │   ├── midi.py            │  ← melody/drum generation
│   │   ├── instruments.py     │
│   │   ├── effects.py         │
│   │   ├── samples.py         │
│   │   └── project.py         │
│   └── tools/                 │
│       └── ableton_tools.py   │  ← high-level wrapper
└──────────┬──────────────────┘
           │ python-osc (UDP)
┌──────────▼──────────────────┐
│   AbletonOSCClient          │
│   ableton_control/osc_client│
│   Send: 127.0.0.1:11000     │
│   Recv: 127.0.0.1:11001     │
└──────────┬──────────────────┘
           │ OSC over UDP
┌──────────▼──────────────────┐
│   AbletonOSC Remote Script  │
│   (installed in Live's      │
│    MIDI Remote Scripts dir)  │
└──────────┬──────────────────┘
           │ Live Object Model
┌──────────▼──────────────────┐
│   Ableton Live 11+          │
└─────────────────────────────┘
```

### 3.2 Connection Method

**AbletonOSC** — the same Remote Script used by jpoindexter's version. It's the de facto standard for OSC control of Ableton Live. Bidirectional UDP: commands sent to port 11000, responses received on 11001.

The `send_and_wait` pattern implements request-response by clearing a pending response buffer, sending the OSC message, then polling at 10ms intervals until a response arrives or timeout (2s default).

### 3.3 Claude Desktop Configuration

```json
{
  "mcpServers": {
    "ableton": {
      "command": "/path/to/python",
      "args": ["-m", "mcp_server.main"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/AbletonMCP"
      }
    }
  }
}
```

Key requirement: absolute paths only. The server uses FastMCP framework and runs via stdio transport.

---

## 4. Parameter Manipulation

### 4.1 Device Parameter Control Depth

**Read operations:**
```python
# Get all parameter names for device 0 on track 0
names = await osc_client.get_device_parameters_name(track_idx=0, device_idx=0)
# Returns: list of parameter name strings

# Get all current values
values = await osc_client.get_device_parameters_value(track_idx=0, device_idx=0)
# Returns: list of float values (0.0-1.0 normalized)

# Get device name and class
name = await osc_client.get_device_name(track_idx=0, device_idx=0)
class_name = await osc_client.get_device_class_name(track_idx=0, device_idx=0)
```

**Write operations:**
```python
# Set parameter by index (normalized 0.0-1.0)
await osc_client.set_device_parameter(
    track_idx=0,
    device_idx=0,
    parameter_idx=3,   # e.g., filter cutoff
    value=0.75          # 75% of range
)
```

**What this means:** An agent can enumerate every parameter on every device, read its current value, and set it to any value. The addressing is by numeric index (track → device → parameter), not by name. The `EffectsHandler` adds a name-based lookup layer on top.

### 4.2 Rack/Chain Navigation

**Not supported.** AbletonOSC's device addressing is flat: `track_idx, device_idx, parameter_idx`. There is no API for:
- Navigating into instrument/effect racks
- Addressing chains within racks
- Accessing macro controls separately from device parameters
- Drum rack pad addressing

Devices on a track are indexed sequentially (0, 1, 2...). If a rack is at device index 1, you can read/write its macro parameters, but you cannot drill into individual chains or devices within the rack.

### 4.3 Real-Time Parameter Listening

```python
# Subscribe to parameter changes
await osc_client.start_listen_parameter_value(track_idx=0, device_idx=0, param_idx=3)
```

This uses AbletonOSC's listener feature to receive callbacks when a parameter changes. The client has handlers set up for this, but it's **not exposed as an MCP tool** — only available internally.

---

## 5. Agent Fitness for Production Feedback

### 5.1 MIDI Content Analysis Potential

**Could an agent analyze MIDI quality? Partially.**

Available data via `get_notes`:
- All note pitches → can compute: note density, pitch range, interval distribution
- All velocities → can compute: velocity dynamics, accent patterns, dynamic range
- All start times + durations → can compute: rhythmic patterns, note lengths, groove analysis
- Combined → chord detection (simultaneous notes), voice leading analysis

**Example analysis flow:**
```
1. get_notes(track=0, clip=0)           → raw MIDI data
2. Agent processes note list             → compute metrics
3. Agent applies music theory knowledge  → assess quality
4. Return feedback as text
```

**Limitations:**
- No API for reading clip-level metadata (scale, key signature)
- No API for reading automation lanes
- Analysis computation happens in the agent (Claude), not in the tool — the tool only provides raw data
- Note data format from `get_notes` may need parsing (AbletonOSC returns it in a specific format)

### 5.2 Sound Design Assessment Potential

**Could an agent assess device parameters? Yes, with caveats.**

Available:
- Read all parameter names and values for any device on any track
- Cross-reference parameter values against known presets/ranges
- Agent can interpret normalized values in context (e.g., "filter cutoff at 0.2 = very closed = dark sound")

Not available:
- No audio-level analysis (spectrum, RMS, frequency content)
- No way to read what instrument/effect is loaded by browser name (only device class name)
- Cannot navigate into racks to assess sound design chains
- No metering data (peak, RMS, loudness)

### 5.3 What's Missing for "Production Feedback" Use Case

| Gap | Impact | Workaround |
|---|---|---|
| No audio analysis | Can't assess mix quality, frequency balance | None via this tool |
| No automation reading | Can't see envelope shapes, filter sweeps | None |
| No rack navigation | Can't analyze complex sound design chains | Flat device enumeration only |
| No metering | Can't assess loudness, dynamics | None |
| No arrangement view access | Can't see macro structure | Scene operations only |
| No clip envelope access | Can't read modulation curves | None |
| No send levels | Can't assess reverb/delay balance | None via current tools |
| No group tracks | Can't understand track organization | Flat track list only |
| No marker/locator access | Can't understand song structure markers | None |

**Bottom line:** This tool is primarily a **writer** (create tracks, add notes, set parameters), not a **reader**. Its analysis capabilities are limited to: reading note data from clips, reading device parameter states, and reading basic session info (tempo, track count, track names). For a production feedback agent, you'd need to supplement this heavily with audio analysis tools.

---

## 6. Maturity Assessment

### 6.1 Maintenance Status

**Effectively abandoned.** One day of active development (Sept 15-16, 2025). No commits in ~6 months. One open issue. No releases. No license.

The codebase shows signs of rapid prototyping:
- `main_backup.py` and `main_fastmcp_simple.py` alongside `main.py` (multiple attempts)
- Diagnosis reports checked into the repo (debugging artifacts)
- Empty `music_ai/` module skeleton
- `VALIDATION_SYSTEM_SUMMARY.md` documents a validation framework but the actual validators may be incomplete

### 6.2 Documentation Quality

Better than average for the star count:
- `README.md` — solid setup instructions
- `CLAUDE.md` — project context for Claude Code
- `Feature_List.md` — comprehensive (if aspirational) feature listing
- `GETTING_STARTED.md` — step-by-step guide
- Two diagnosis reports documenting what works and what doesn't (unusually honest)

### 6.3 Known Issues (from self-diagnosis)

The repo's own `MIDI_TOOLS_FINAL_DIAGNOSIS.md` and `MCP_TOOLS_DIAGNOSIS_REPORT.md` reveal:
- **~25% of advertised features don't work** — device loading, preset loading, some clip operations
- OSC commands failed silently, returning success messages for operations that couldn't execute
- The fix was changing to "honest communication" (returning manual instructions instead of fake success)
- Device/instrument/effect loading is **impossible via OSC** — user must load manually in Live

### 6.4 Comparison to jpoindexter/ableton-mcp

| Dimension | FabianTinkl/AbletonMCP | jpoindexter/ableton-mcp |
|---|---|---|
| **Stars** | 7 | ~200+ |
| **Maintenance** | Abandoned (Sept 2025) | Actively maintained |
| **OSC Layer** | AbletonOSC | AbletonOSC |
| **MCP Framework** | FastMCP (Python) | TypeScript |
| **MIDI Composition** | Built-in generators (melody, drums, chords) | No built-in generation |
| **Note-level MIDI** | Full CRUD | Full CRUD |
| **Device Params** | Read/write | Read/write |
| **Tool Count** | 18 MCP tools | ~25+ MCP tools |
| **Rack Navigation** | No | No (same AbletonOSC limitation) |
| **Code Quality** | Prototype-grade with backup files | Production-grade |
| **Honestly Working** | ~75% of tools | ~90%+ of tools |
| **Genre Focus** | Techno/industrial specific | Genre-agnostic |
| **Music Theory** | music21 integration, scale awareness | None |

**Key differentiator:** FabianTinkl's version is the only one with built-in music theory and algorithmic composition. jpoindexter's is more reliable and complete as a control surface, but expects the LLM to generate MIDI data itself.

---

## 7. Key Takeaways for Agent Pipeline Design

### What to Steal

1. **The MIDI note CRUD pattern** — `add_notes`, `get_notes`, `remove_notes` via OSC is well-proven. The tool call schema (array of note dicts with pitch/start_time/duration/velocity) is a good contract.

2. **Scale-aware generation approach** — Using `music21` for scale degree calculations is sound. The implementation is basic but the pattern (constrain generation to scale, bias toward stepwise motion) is correct.

3. **Drum pattern library** — The GM-mapped, style-specific patterns are useful reference data even if you reimplement the generation.

4. **Honest capability reporting** — Their diagnosis reports are a good model. Knowing that AbletonOSC cannot load devices/presets is critical context for any agent in this space.

### What to Avoid

1. **Don't trust the feature list** — ~25% doesn't work. Always verify against AbletonOSC's actual capabilities.

2. **Don't rely on the composition handlers for real output** — `generate_chord_progression` and `create_techno_song` generate text descriptions, not MIDI data. This is a UX antipattern for an agent pipeline.

3. **Don't use this repo as-is** — It's abandoned, has no license, and ~25% of tools silently fail or return manual instructions.

4. **The `music_ai/` module is vapor** — Empty stubs. All composition logic lives in handlers.

### Architectural Recommendation

For your pipeline, the optimal approach is likely:

- **Use jpoindexter's as the control surface** (more reliable, better maintained)
- **Port FabianTinkl's music theory patterns** into your own skill/domain model (scale-aware generation, drum patterns, genre knowledge)
- **Build analysis on top of `get_notes` + `get_device_parameters`** — these OSC operations work reliably across both implementations
- **Accept the AbletonOSC limitations** — no device loading, no rack navigation, no audio analysis. These are protocol-level constraints, not implementation bugs.

---

## Appendix A: All OSC Addresses Used

### Transport
| Address | Direction | Purpose |
|---|---|---|
| `/live/song/start_playing` | Send | Play |
| `/live/song/stop_playing` | Send | Stop |
| `/live/song/set/tempo` | Send | Set BPM |
| `/live/song/get/tempo` | Request | Get BPM |
| `/live/song/get/current_song_time` | Request | Get playhead position |
| `/live/song/set/current_song_time` | Send | Set playhead position |

### Track
| Address | Direction | Purpose |
|---|---|---|
| `/live/song/create_audio_track` | Send | Create audio track |
| `/live/song/create_midi_track` | Send | Create MIDI track |
| `/live/song/create_return_track` | Send | Create return track |
| `/live/song/get/num_tracks` | Request | Track count |
| `/live/track/set/name` | Send | Rename track |
| `/live/track/get/name` | Request | Get track name |
| `/live/track/set/volume` | Send | Set volume |
| `/live/track/set/panning` | Send | Set pan |
| `/live/track/set/mute` | Send | Mute/unmute |
| `/live/track/set/solo` | Send | Solo/unsolo |
| `/live/track/set/arm` | Send | Arm/disarm |
| `/live/track/stop_all_clips` | Send | Stop clips on track |
| `/live/track/get/devices/name` | Request | List device names |
| `/live/track/get/num_devices` | Request | Device count |

### Clip
| Address | Direction | Purpose |
|---|---|---|
| `/live/clip_slot/create_clip` | Send | Create empty clip |
| `/live/clip_slot/fire` | Send | Launch clip |
| `/live/clip/set/name` | Send | Name clip |
| `/live/clip/get/name` | Request | Get clip name |
| `/live/clip/set/color` | Send | Set clip color |
| `/live/clip/get/length` | Request | Get clip length |
| `/live/clip/set/loop_start` | Send | Set loop start |
| `/live/clip/set/gain` | Send | Set clip gain |
| `/live/clip/get/is_playing` | Request | Playing state |

### MIDI
| Address | Direction | Purpose |
|---|---|---|
| `/live/clip/add/notes` | Send | Add MIDI note |
| `/live/clip/remove/notes` | Send | Remove MIDI note(s) |
| `/live/clip/get/notes` | Request | Read MIDI notes |

### Audio Clip
| Address | Direction | Purpose |
|---|---|---|
| `/live/clip/set/warp_mode` | Send | Set warp mode |
| `/live/clip/get/file_path` | Request | Get audio file path |
| `/live/clip/set/start_marker` | Send | Set start marker |
| `/live/clip/set/end_marker` | Send | Set end marker |

### Device
| Address | Direction | Purpose |
|---|---|---|
| `/live/device/set/parameter/value` | Send | Set parameter |
| `/live/device/get/name` | Request | Device name |
| `/live/device/get/class_name` | Request | Device class |
| `/live/device/get/parameters/name` | Request | All param names |
| `/live/device/get/parameters/value` | Request | All param values |
| `/live/device/start_listen/parameter/value` | Send | Subscribe to changes |

### Scene
| Address | Direction | Purpose |
|---|---|---|
| `/live/scene/fire` | Send | Launch scene |
| `/live/song/create_scene` | Send | Create scene |
| `/live/song/delete_scene` | Send | Delete scene |
| `/live/scene/get/name` | Request | Scene name |
| `/live/scene/set/name` | Send | Rename scene |

### Utility
| Address | Direction | Purpose |
|---|---|---|
| `/live/song/undo` | Send | Undo |
| `/live/song/redo` | Send | Redo |
| `/live/song/get/track_data` | Request | Bulk track data |
| `/live/song/get/track_names` | Request | All track names |
| `/live/song/start_listen/beat` | Send | Beat listener |
| `/live/song/stop_listen/beat` | Send | Stop beat listener |
