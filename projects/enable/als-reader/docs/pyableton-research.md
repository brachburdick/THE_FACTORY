# pyableton Research Report

**Date:** 2026-03-20
**Library:** pyableton v0.0.15
**Repo:** https://github.com/maranedah/pyableton
**PyPI:** https://pypi.org/project/pyableton/
**Verdict:** Not fit for production use. Build a custom parser instead.

---

## 1. Capabilities & Coverage

### What it parses (confirmed from source code)

| .als XML Element | Parsed? | Depth | Notes |
|---|---|---|---|
| MIDI Tracks | Yes | Deep | MidiTrack with ID, name, color, device chain, freeze state, track group, pitchbend range |
| Audio Tracks | Partial | Shallow | AudioTrack class exists but `name` and `device_chain` are commented out. Essentially a stub. |
| Return Tracks | Partial | Shallow | ReturnTrack exists but `device_chain` is commented out |
| Master Track | Yes | Deep | Automation envelopes, device chain, mixer with tempo |
| Pre-Hear Track | Stub | None | `__init__` returns None |
| Scenes | Yes | Shallow | Scene class with tempo, time_signature_id, follow_action |
| MIDI Clips | Yes | Deep | MidiClip with time, start/end, name, color, launch mode, quantization, legato, warp, notes |
| MIDI Notes | Yes | Deep | MidiNoteEvent: time, duration, velocity, velocity_deviation, off_velocity, probability, is_enabled, note_id |
| KeyTracks | Yes | Deep | Groups notes by MIDI key, provides get_notes() returning muspy.Note objects |
| Mixer (per-track) | Partial | Medium | Pan (manual value only), split stereo pan L/R. Volume is commented out. No send levels. |
| Mixer (master) | Partial | Medium | Tempo (manual value), but volume, sends, speaker, pan commented out |
| Tempo | Yes | Shallow | Only `manual` value from master track mixer. No tempo automation. |
| Time Signature | Yes | Via automation | Parsed from master track automation envelopes using constants lookup (4/ and 8/ denominators only) |
| Automation Envelopes | Partial | Medium | AutomationEnvelope with events (time + value). Master track only. Per-track automation commented out. |
| Device Chain | Partial | Medium | Routing (audio/MIDI in/out), mixer, sequencers. But `devices` list is **commented out**. |
| I/O Routing | Yes | Medium | IORouting with target, display strings, MPE settings |
| Grid | Yes | Full | fixed_numerator, fixed_denominator, grid_interval_pixel, ntoles, snap_to_grid, fixed |
| Follow Actions | Yes | Full | follow_time, is_linked, loop_iterations, enabled, action A/B with chance and jump index |
| Transport | Yes | Full | loop on/off, loop start/length, current_time, punch in/out, metronome, draw mode |
| Scale Information | Yes | Shallow | root_note, name |
| Groove Pool | Stub | None | lom_id only, Grooves list commented out |
| Locators | Stub | None | Placeholder returning None |
| Linked Track Groups | Stub | None | Placeholder |
| View/UI State | Yes | Full | Session/arranger view states, navigator positions, track header width |

### What it does NOT parse (confirmed absent or commented out)

- **Audio clip references / sample file paths** (open issue #22)
- **Devices / Plugins** -- `devices: List[InstrumentGroupDevice]` commented out in DeviceChain
- **Device Racks** (instrument, effect, drum racks)
- **Max4Live devices**
- **Warp markers**
- **Audio clip properties** (sample rate, file path, warp mode, gain)
- **Send levels** -- commented out in Mixer
- **Volume** -- commented out in Mixer
- **Clip envelopes** -- commented out in MidiClip
- **Per-track automation** -- commented out in MidiTrack and AudioTrack
- **Take lanes** -- commented out
- **Groove settings** -- commented out
- **Loop settings on clips** -- commented out
- **Crossfade state** -- commented out
- **Clip slots (session view)** -- commented out in sequencers
- **Grouped tracks** -- track_group_id parsed but no GroupTrack class

### Read/Write

**Read-only with MIDI export.** Can:
1. Parse .als -> Python objects
2. Export to MIDI via muspy (`to_midi()`)
3. Export to muspy Music object (`to_muspy()`)
4. Dump raw XML (`to_xml()` -- just gunzip, not reconstruction)

**Cannot write .als files.** No serialization from object model back to XML.

### Ableton version compatibility

Not documented. Generic XML parsing should work with any gzip+XML version (Ableton 8+), but hardcoded attribute expectations mean newer versions crash with `AttributeError: 'NoneType' object has no attribute 'attrib'` when expected nodes are missing. **No version detection or graceful fallback.**

---

## 2. API Surface

### Object Model

```
Ableton (top-level entry point)
  └── LiveSet
        ├── tracks: list[Track]  (MidiTrack | AudioTrack | ReturnTrack)
        │     └── MidiTrack
        │           ├── name: MidiName (effective_name, user_name, annotation)
        │           ├── device_chain: DeviceChain
        │           │     ├── audio_input_routing: IORouting
        │           │     ├── midi_input_routing: IORouting
        │           │     ├── audio_output_routing: IORouting
        │           │     ├── midi_output_routing: IORouting
        │           │     ├── mixer: Mixer (pan, split_stereo_pan)
        │           │     ├── main_sequencer: MainSequencer
        │           │     │     └── clip_timeable: ClipTimeable
        │           │     │           └── arranger_automation: ArrangerAutomation
        │           │     │                 └── events: list[MidiClip]
        │           │     │                       └── notes: Notes
        │           │     │                             └── key_tracks: list[KeyTrack]
        │           │     │                                   └── notes: list[MidiNoteEvent]
        │           │     └── freeze_sequencer: FreezeSequencer
        │           ├── color: int
        │           ├── track_group_id: int
        │           └── freeze: bool
        ├── master_track: MasterTrack
        │     ├── automation_envelopes: AutomationEnvelopes
        │     │     └── envelopes: list[AutomationEnvelope]
        │     │           └── automation: Automation -> events: list[EnumEvent]
        │     └── device_chain: MasterTrackDeviceChain
        │           └── mixer: MasterTrackMixer -> tempo: Tempo
        ├── scenes: list[Scene]
        ├── transport: Transport
        ├── grid: Grid
        └── scale_information: ScaleInformation
```

### Architecture

All classes inherit from `AbletonComponent`, which uses **type annotations as a declarative schema**. The base `__init__` iterates `self.__annotations__`, converts snake_case to CamelCase XML element names, and auto-parses:
- `int`, `str`, `float` -> XML attribute values
- `bool` -> attribute value == "true"
- `dict` -> JSON.loads from attribute
- `list[SomeComponent]` -> find child elements, instantiate each
- `AbletonComponent` subclass -> find child element, instantiate

Clever but fragile: missing XML elements cause unhandled `AttributeError` on NoneType.

### Usage Examples

```python
from pyableton import Ableton

# Load a project
project = Ableton("path/to/project.als")

# Access tracks
for track in project.live_set.tracks:
    print(type(track).__name__)  # MidiTrack, AudioTrack, or ReturnTrack

# Get MIDI track names
midi_tracks = [t for t in project.live_set.tracks if isinstance(t, MidiTrack)]
for t in midi_tracks:
    print(t.name.effective_name)

# Get MIDI notes from first clip of first MIDI track
clip = t.device_chain.main_sequencer.clip_timeable.arranger_automation.events[0]
for kt in clip.notes.key_tracks:
    for note in kt.notes:
        print(f"Key={kt.midi_key} Time={note.time} Dur={note.duration} Vel={note.velocity}")

# Export notes as pandas DataFrame
df = clip.notes.to_pandas()  # columns: time, pitch, duration, velocity

# Get tempo
bpm = project.live_set.master_track.device_chain.mixer.tempo.manual

# Export to MIDI
project.to_midi("output.midi")
```

### Data Structures

All data returned as **custom objects** (AbletonComponent subclasses) with typed attributes. Notes convertible to `muspy.Note` or `pandas.DataFrame`. No dicts or dataclasses.

### Dependencies

- `muspy>=0.5.0` (required, not optional)
- `pandas>=2.0.0`
- Python >= 3.10

---

## 3. Gaps & Limitations

### Critical Gaps

1. **No device/plugin parsing.** `devices` list commented out. Cannot discover instruments or effects on any track.
2. **No audio file references.** Sample paths, audio clip properties, warp markers -- nothing.
3. **No volume or send levels.** Both commented out in Mixer. Cannot assess mix balance.
4. **AudioTrack is a stub.** `name` and `device_chain` commented out.
5. **No clip slots / session view clips.** Commented out in sequencers.
6. **No graceful error handling.** Missing XML = `AttributeError` crash.

### Maintenance Status: STALE

- Last commit: 2024-02-08 (2+ years ago)
- Last PyPI release: 2024-02-08 (v0.0.15)
- Open issues: 3 (all unanswered)
- Contributors: 1 person (maranedah)
- Version 0.0.15 -- pre-alpha by semver
- Dev burst: 15 versions in ~7 weeks (Dec 2023 - Feb 2024), then silence

### Edge Cases NOT Handled

- Frozen tracks: `freeze` parsed but FreezeSequencer has no clip data
- Grouped tracks: `track_group_id` exists but no GroupTrack type
- Max4Live devices: not parsed
- Nested racks: not parsed
- Audio clips in arrangement: not parsed
- Multiple Ableton versions: no version-aware parsing

### Known Bugs

- **Issue #21:** `AttributeError: 'NoneType'` -- crashes on many real-world .als files
- **Issue #23:** numpy/muspy compatibility + same crash
- **Issue #22:** Feature request for audio file locations (not implemented)

---

## 4. Integration Fitness

### As an MCP Tool or Agent Skill

**Feasibility: Low-Medium.** Reliability is the blocker:
- Crash rate on real-world files is likely high due to rigid parsing
- Access path to useful data is 8 levels deep
- muspy dependency is heavy for what it provides

### What an Agent COULD Assess (if reliable)

- MIDI note content: pitch distribution, velocity patterns, note density, rhythmic patterns
- Arrangement structure: clip placement in timeline (MIDI only)
- Track count and naming
- Tempo and time signature
- Basic pan positions
- Scale/key information
- Follow action configurations

### What an Agent Could NOT Assess

- Sound design / timbre (no device data)
- Mix balance (no volume/sends)
- Audio content (no audio clips/samples)
- Effects chains (no device parsing)
- Sidechain routing
- Frequency content / spectral balance
- Master chain processing
- Session view arrangement
- Per-track automation curves
