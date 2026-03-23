# als-reader

A custom Ableton Live Set (`.als`) parser, analyzer, and editor for AI agent pipelines. Lets agents read, understand, visualize, critique, and modify Ableton projects — without Ableton running.

**Zero required dependencies** for the core parser (Python stdlib only). Optional `fastmcp` dependency for the MCP server.

## Why

Existing libraries (pyableton, dawtool, loive) cover ~20% of the ALS schema and crash on real-world files. als-reader parses **all 5 data tiers** reliably — tested against 69 real Ableton Live 12.x projects with zero failures.

## Quick Start

### Python API

```python
import als_reader

project = als_reader.load("song.als")

print(project.tempo)              # 128.0
print(project.time_signature)     # TimeSignature(numerator=4, denominator=4)
print(project.version.creator)    # "Ableton Live 12.3.2"

# Tracks
for track in project.tracks:
    print(f"{track.name} ({track.track_type}) — {len(track.clips)} clips, {len(track.devices)} devices")

# MIDI notes
for clip in project.midi_tracks[0].midi_clips:
    for note in clip.notes:
        print(f"  pitch={note.pitch} time={note.time} vel={note.velocity}")

# Mix state
for track in project.tracks:
    m = track.mixer
    print(f"{track.name}: vol={m.volume} pan={m.pan}")

# Devices
for dev in project.tracks[0].devices:
    print(f"{dev.name} ({dev.device_type}) on={dev.is_on}")

# JSON for LLM context
print(project.to_json())
```

### CLI

```bash
python -m als_reader song.als              # Full JSON dump
python -m als_reader song.als -s           # Compact summary
python -m als_reader song.als -a           # ASCII arrangement view
python -m als_reader song.als -a -w 200    # Wide arrangement view
python -m als_reader song.als -f           # Feedback analysis report
python -m als_reader song.als --compact    # Minified JSON
```

### Write Operations

```python
from als_reader.writer import ALSWriter

writer = ALSWriter("song.als")
writer.rename_track("3-Serum", "Lead Synth")
writer.set_track_volume("Lead Synth", 0.7)
writer.set_track_pan("Lead Synth", 0.2)
writer.humanize_velocities("Drums", amount=20)
writer.set_tempo(125)
writer.save("song_v2.als")  # save to new file; or writer.save() to overwrite with .bak backup
```

### MCP Server (for AI agents)

```bash
# Install with MCP server support
pip install als-reader

# Run the MCP server (stdio transport)
python -m als_reader.mcp_server
```

Or configure in Claude Code (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "als-reader": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "als_reader.mcp_server"],
      "cwd": "/path/to/als-reader"
    }
  }
}
```

## MCP Tools

12 tools available for AI agents:

### Read

| Tool | Description |
|------|-------------|
| `summarize_live_set` | Compact overview — tracks, tempo, devices, mix snapshot |
| `view_arrangement` | ASCII timeline — tracks as rows, clips as blocks |
| `analyze_live_set` | Structured feedback with findings by severity |
| `parse_live_set` | Full project JSON dump (can be large) |
| `get_track_details` | Deep dive on one track by name |
| `get_midi_notes` | MIDI notes from a specific clip |

### Write

| Tool | Description |
|------|-------------|
| `rename_track` | Rename a track |
| `set_track_volume` | Set volume (linear: 0.0–~1.99) |
| `set_track_pan` | Set pan (-1.0 left to 1.0 right) |
| `set_midi_velocities` | Set fixed velocity or scale existing |
| `humanize_velocities` | Add deterministic velocity variation |
| `set_tempo` | Change project tempo |

## What It Extracts

| Tier | Data | Examples |
|------|------|---------|
| 1 — Core | Tracks, tempo, time sig, markers, scale, version | Track names, types, colors, group membership |
| 2 — Arrangement | MIDI clips + notes, audio clips + samples, clip slots, scenes | Note pitch/velocity/duration/probability, sample file paths, warp markers |
| 3 — Mix | Volume, pan, sends, I/O routing, solo/mute | Per-track levels, send amounts, routing targets |
| 4 — Sound Design | Device chains, VST/AU/native plugins, racks, macros | Plugin names + vendors, rack chains, on/off state, key parameters |
| 5 — Detail | Automation envelopes, clip envelopes, groove pool, follow actions | Breakpoints, groove timing/quantize, follow action chains |

## Feedback Analyzers

The `analyze_live_set` tool runs four analyzers:

- **Arrangement** — Empty tracks, clip density, marker placement, section structure, naming
- **Mix** — Volume distribution, hot tracks, panning spread, sends, master level, routing
- **MIDI** — Velocity dynamics, pitch distribution, key detection, single-note parts
- **Devices** — Bypassed plugins, empty racks, heavy chains, missing master limiter, plugin census

Findings are severity-sorted: `warning` → `suggestion` → `info`.

## Arrangement View

The ASCII arrangement view renders the project timeline:

```
             1...............9...............17..............25..
             V               V               V
             Intro           Build           Drop
-------------+---------------------------------------------------
M Bass Synth |::::[Bass=][Fill]::::::::::::::[Bass=][Bass=][Bass=]
A Drums      |::::[Break_120bpm==============][Break_120bpm======]
M Lead       |:::::::::::::::::::::::[Lead (24n)===]:::::::::::::
A FX Riser   |:::::::::::::::::::::[riser=]::::::::::::::::::::::
-------------+---------------------------------------------------
128 BPM | 4/4 | C Major | 52 bars | 1.6 min
```

Track types: `M`=MIDI, `A`=audio, `G`=group. State: `S`=solo, `m`=muted.

## Design

- **Every field `Optional[T]`** — missing XML elements produce `None`, never crash
- **Flat access**: `project.tempo`, `track.clips`, `track.devices`
- **Modular extractors** in `als_reader/extractors/` — each tier independent
- **JSON serialization** strips None values for compact LLM context
- **Write safety** — `.bak` backup before overwrite, optional `output_path`
- **Ableton 11 + 12 compatible** — handles `MasterTrack`/`MainTrack`, `ClipTimeable`/`Sample`, scale enum differences

## Project Structure

```
als_reader/
├── __init__.py              # Public API: load()
├── __main__.py              # CLI entry point
├── parser.py                # gzip decompress + XML parse + version detection
├── models.py                # 25+ dataclasses for all domain objects
├── writer.py                # Write operations (decompress → modify → recompress)
├── mcp_server.py            # FastMCP server with 12 tools
├── extractors/
│   ├── _xml_helpers.py      # Safe XML navigation (never raises)
│   ├── tracks.py            # Track assembly from sub-extractors
│   ├── clips.py             # MIDI/audio clips, notes, clip slots
│   ├── mixer.py             # Volume, pan, sends, routing
│   ├── devices.py           # Device chains, plugins, racks
│   ├── automation.py        # Track + clip automation envelopes
│   ├── transport.py         # Tempo, time sig, markers, scale, grooves
│   └── scenes.py            # Session view scenes
└── analysis/
    ├── arrangement.py       # Arrangement structure analysis
    ├── arrangement_view.py  # ASCII timeline renderer
    ├── mix.py               # Mix balance analysis
    ├── midi.py              # MIDI content analysis
    ├── devices.py           # Device chain analysis
    └── report.py            # Unified feedback report
```

## Installation

### From source (core parser only — no external deps)

```bash
git clone https://github.com/yourusername/als-reader.git
cd als-reader
python -m als_reader song.als
```

### With MCP server support

```bash
pip install als-reader          # installs fastmcp dependency
# or from source:
pip install -e .
```

## Testing

```bash
# Generate test fixture
python tests/create_fixture.py

# Unit tests (83 tests)
python -m unittest tests.test_parser -v

# Stress test against real .als files (update path in script)
python tests/stress_test.py
```

## How .als Files Work

An `.als` file is gzip-compressed XML containing the full Ableton Live project state. The format is undocumented but self-describing — element and attribute names map directly to Ableton's internal data model. Key structural differences exist between Ableton versions (e.g., Live 12 uses `MainTrack` instead of `MasterTrack`, `Sample` instead of `ClipTimeable` for audio tracks).

See `docs/` for detailed research on the format, existing libraries, and design decisions.

## License

MIT
