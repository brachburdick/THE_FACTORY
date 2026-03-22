# pyableton Technical Research Report

**Date:** 2026-03-20
**Library:** pyableton v0.0.15
**Repo:** https://github.com/maranedah/pyableton
**PyPI:** https://pypi.org/project/pyableton/

---

## 1. Capabilities & Coverage

### What it parses (confirmed from source code)

| .als XML Element | Parsed? | Depth | Notes |
|---|---|---|---|
| **MIDI Tracks** | Yes | Deep | Full MidiTrack class with ID, name, color, device chain, freeze state, track group, pitchbend range |
| **Audio Tracks** | Partial | Shallow | AudioTrack class exists but `name` and `device_chain` are commented out. Essentially a stub. |
| **Return Tracks** | Partial | Shallow | ReturnTrack exists but `device_chain` is commented out |
| **Master Track** | Yes | Deep | Automation envelopes, device chain, mixer with tempo |
| **Pre-Hear Track** | Stub | None | `__init__` returns None |
| **Scenes** | Yes | Shallow | Scene class with tempo, time_signature_id, follow_action |
| **MIDI Clips** | Yes | Deep | MidiClip with time, start/end, name, color, launch mode, quantization, legato, warp, notes |
| **MIDI Notes** | Yes | Deep | MidiNoteEvent: time, duration, velocity, velocity_deviation, off_velocity, probability, is_enabled, note_id |
| **KeyTracks** | Yes | Deep | Groups notes by MIDI key, provides get_notes() returning muspy.Note objects |
| **Mixer (per-track)** | Partial | Medium | Pan (manual value only), split stereo pan L/R. Volume is commented out. No send levels. |
| **Mixer (master)** | Partial | Medium | Tempo (manual value), but volume, sends, speaker, pan commented out |
| **Tempo** | Yes | Shallow | Only `manual` value from master track mixer. No tempo automation points as note events. |
| **Time Signature** | Yes | Via automation | Parsed from master track automation envelopes using a constants lookup table (4/ and 8/ denominators only) |
| **Automation Envelopes** | Partial | Medium | AutomationEnvelope with events (time + value). Used for time signature on master track. Per-track automation commented out. |
| **Device Chain** | Partial | Medium | Routing (audio/MIDI in/out), mixer, main sequencer, freeze sequencer. But `devices` list is **commented out** -- no actual device/plugin parsing. |
| **I/O Routing** | Yes | Medium | IORouting with target, display strings, MPE settings |
| **Grid** | Yes | Full | fixed_numerator, fixed_denominator, grid_interval_pixel, ntoles, snap_to_grid, fixed |
| **Follow Actions** | Yes | Full | follow_time, is_linked, loop_iterations, enabled, action A/B with chance and jump index |
| **Transport** | Yes | Full | loop on/off, loop start/length, current_time, punch in/out, metronome, draw mode |
| **Scale Information** | Yes | Shallow | root_note, name |
| **Groove Pool** | Stub | None | lom_id only, Grooves list commented out |
| **Locators** | Stub | None | Placeholder `__init__` returning None |
| **Linked Track Groups** | Stub | None | Placeholder |
| **View/UI State** | Yes | Full | Session/arranger view states, navigator positions, track header width, video window rect |

### What it does NOT parse (confirmed absent or commented out)

- **Audio clip references / sample file paths** -- not parsed at all (open issue #22 requests this)
- **Devices / Plugins** -- `devices: List[InstrumentGroupDevice]` is commented out in DeviceChain. No Instrument, AudioEffect, MidiEffect, or plugin parsing whatsoever.
- **Device Racks** (instrument racks, effect racks, drum racks) -- not implemented
- **Max4Live devices** -- not implemented
- **Warp markers** -- not parsed from audio clips
- **Audio clip properties** (sample rate, file path, warp mode, gain)
- **Send levels** -- commented out in Mixer
- **Volume** -- commented out in Mixer
- **Clip envelopes** -- commented out in MidiClip
- **Per-track automation** -- commented out in MidiTrack and AudioTrack
- **Take lanes** -- commented out
- **Groove settings** -- commented out
- **Loop settings on clips** -- commented out
- **Crossfade state** -- commented out
- **Clip slots (session view)** -- ClipSlotList commented out in sequencers
- **Grouped tracks** -- track_group_id is parsed but no GroupTrack class exists

### Read/Write capability

**Read-only with MIDI export.** The library can:
1. Parse .als -> Python objects (read)
2. Export to MIDI via muspy (`to_midi()`)
3. Export to muspy Music object (`to_muspy()`)
4. Dump raw XML (`to_xml()` -- just gunzip, not reconstruction)

It **cannot write .als files**. The `to_xml()` method simply decompresses the gzip to a temp file -- there is no serialization from the object model back to XML. The object model is one-way: XML -> Python objects.

### Ableton version compatibility

Not explicitly documented. The library does generic XML parsing with `xml.etree.ElementTree`, so it should work with any version that uses the gzip+XML format (Ableton 8+). However, the hardcoded attribute expectations mean newer Ableton versions with additional XML elements will cause `AttributeError: 'NoneType' object has no attribute 'attrib'` when expected nodes are missing -- this is exactly what open issue #21 reports. There is **no version detection or graceful fallback** for missing elements.

---

## 2. API Surface

### Key Classes

```
Ableton (top-level, entry point)
  └── LiveSet
        ├── tracks: list[Track]  (factory: MidiTrack | AudioTrack | ReturnTrack)
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

### Object model architecture

All classes inherit from `AbletonComponent`, which uses **Python type annotations as a declarative schema**. The base class `__init__` iterates `self.__annotations__`, converts snake_case attribute names to CamelCase XML element names, and auto-parses:
- `int`, `str`, `float` -> from XML attribute values
- `bool` -> attribute value == "true"
- `dict` -> JSON.loads from attribute value
- `list[SomeComponent]` -> finds child elements, instantiates each
- `AbletonComponent` subclass -> finds child element, instantiates

This is clever but fragile: any XML element that is missing or has unexpected structure causes an unhandled `AttributeError` on NoneType.

### Usage examples

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

# Export to muspy Music object
music = project.to_muspy()
```

### Data structures

All data is returned as **custom objects** (AbletonComponent subclasses) with typed attributes. Notes can be converted to `muspy.Note` objects or `pandas.DataFrame`. There are no dicts or dataclasses -- everything is custom classes with `__init__` driven by annotations.

### Dependencies

- `muspy>=0.5.0` (music processing library -- required, not optional)
- `pandas>=2.0.0` (for DataFrame export)
- Python >= 3.10

---

## 3. Gaps & Limitations

### Critical gaps

1. **No device/plugin parsing.** The `devices` list in DeviceChain is commented out. You cannot discover what instruments or effects are on any track. This is a major gap for any music analysis use case.

2. **No audio file references.** Sample paths, audio clip properties, warp markers -- none of this is parsed. Open issue #22 requests this.

3. **No volume or send levels.** Both are commented out in the Mixer class. You cannot assess mix balance.

4. **AudioTrack is a stub.** `name` and `device_chain` are commented out -- you can read the track exists and its color, but not its clips, routing, or any meaningful data.

5. **No clip slots / session view clips.** `clip_slot_list` is commented out in both MainSequencer and FreezeSequencer.

6. **No graceful error handling.** Missing XML elements cause `AttributeError: 'NoneType' object has no attribute 'attrib'` with no fallback. This is the subject of the most common open bug reports.

### Maintenance status: STALE

- **Last commit:** 2024-02-08 (over 2 years ago)
- **Last PyPI release:** 2024-02-08 (v0.0.15)
- **Open issues:** 3 (all unanswered, oldest from April 2024)
- **Contributors:** 1 person (maranedah) + GitHub Actions bot
- **PR activity:** All 20 PRs are from the single maintainer, all merged, last one Feb 2024
- **No responses to any open issues**
- **Version 0.0.15** -- still pre-alpha by semver conventions
- **Development burst:** 15 versions released in ~7 weeks (Dec 2023 - Feb 2024), then complete silence

### Edge cases NOT handled

- **Frozen tracks:** `freeze` attribute is parsed but FreezeSequencer has no clip data
- **Grouped tracks:** `track_group_id` exists but no GroupTrack type, no hierarchy reconstruction
- **Max4Live devices:** Not parsed (no device parsing at all)
- **Nested racks:** Not parsed
- **Audio clips in arrangement:** Not parsed (only MIDI clips via ArrangerAutomation)
- **Multiple Ableton versions:** No version-aware parsing; newer .als files with additional elements crash

### Known bugs (from issues)

- **Issue #21:** `AttributeError: 'NoneType' object has no attribute 'attrib'` -- crashes on many real-world .als files because the parser expects all XML elements to exist
- **Issue #23:** numpy/muspy compatibility warning, same crash as #21
- **Issue #22:** Feature request for audio file locations (not implemented)

---

## 4. Integration Fitness

### As an MCP tool or agent skill

**Feasibility: Low-Medium.** The library could be wrapped, but reliability is the blocker:

- **Crash rate on real-world files is likely high.** The rigid parsing with no fallback means any .als file with elements the library doesn't expect (which is most files with audio tracks, certain plugin configurations, or newer Ableton versions) will crash.
- **The access path to useful data is deeply nested.** Getting MIDI notes requires: `project.live_set.tracks[i].device_chain.main_sequencer.clip_timeable.arranger_automation.events[j].notes.key_tracks[k].notes[l]` -- 8 levels deep.
- **muspy dependency is heavy** for what amounts to a MIDI export convenience.

If wrapped, the tool would need significant error handling around every access path.

### What an agent COULD assess (if the library worked reliably)

- MIDI note content: pitch distribution, velocity patterns, note density, rhythmic patterns
- Arrangement structure: clip placement in timeline (MIDI only)
- Track count and naming
- Tempo and time signature
- Basic pan positions
- Scale/key information
- Follow action configurations

### What an agent could NOT assess using pyableton alone

- **Sound design / timbre:** No device or plugin data parsed
- **Mix balance:** No volume levels, no send levels
- **Audio content:** No audio clips, no sample references, no warp markers
- **Effects chains:** No device parsing at all
- **Sidechain routing:** No detailed routing beyond basic I/O strings
- **Frequency content / spectral balance:** Would need audio analysis
- **Master chain processing:** No devices parsed on master
- **Session view arrangement:** No clip slots parsed
- **Automation curves:** Only time signature automation on master; per-track automation commented out

---

## 5. Alternatives Comparison

### Raw gzip + xml.etree (DIY)

```python
import gzip
import xml.etree.ElementTree as ET

with gzip.open("project.als", "rb") as f:
    tree = ET.parse(f)
root = tree.getroot()

# You now have full access to every XML element
for track in root.find('.//Tracks'):
    print(track.tag, track.attrib.get('Id'))
```

**Advantages over pyableton:**
- Access to ALL XML elements, not just the subset pyableton models
- No crash on unexpected elements
- No muspy/pandas dependency
- Can read device chains, audio clips, sample paths, volume, sends -- everything
- Can be version-aware by checking `root.attrib['Creator']`
- Trivial to implement: .als is just gzip'd XML

**Disadvantages:**
- No typed object model (working with raw ElementTree)
- Must know the XML schema yourself
- No MIDI export convenience

**Verdict:** For an MCP tool or agent skill, DIY gzip+xml.etree is strictly superior. pyableton adds a typed object model for ~20% of the schema while introducing crash-prone rigidity and a heavy dependency (muspy). The XML schema is well-structured and consistent -- a custom parser for the specific elements you need would take a day to write and would be more reliable.

### dawtool (offlinemark/dawtool)

- **Stars:** 210 (10x pyableton)
- **Focus:** Time marker extraction with tempo automation support
- **Supports:** Ableton 8-12, FL Studio 10-20, .cue files
- **Maturity:** Production-tested on 10,000+ files since 2020
- **Limitation:** Only officially exposes markers. Internal APIs have more but are unstable.
- **Last activity:** March 2021 (also stale, but more proven)
- **Best for:** DJ mix tracklist generation, podcast chapters, cue point extraction
- **Not useful for:** General arrangement/MIDI/device analysis

### loive (naglalakk/loive)

- **Stars:** 41
- **Last updated:** February 2021 (effectively 2013-era code)
- **Focus:** Plugin/device detection, project summary
- **Unique strength:** Actually lists VST/AU plugins and Ableton native devices
- **Limitation:** Tested only on Ableton 8.1.3 and 9.0.4. Ancient. Python 2 era.
- **Not viable** for modern use without significant modernization

### abelsonlive/ableton

- **Stars:** 11
- **Status:** 1 commit, exploratory. Not a real library.

### Other notable repos

- **jbremz/als-parser** (1 star): CLI tool, recently updated (2025), worth monitoring
- **Alerion/blendals** (3 stars): Parses .als to JSON, updated 2024
- **MartinBarker/Ableton-To-Cue-Tracklist-Generator** (2 stars): Specific to tracklist/cue generation

### Recommendation

**For an MCP tool or agent skill: write a custom parser using gzip + xml.etree.ElementTree.**

Rationale:
1. The .als format is straightforward gzip'd XML. The schema is consistent and self-documenting.
2. pyableton covers only ~20% of the useful schema and crashes on real-world files.
3. A custom parser can target exactly the elements needed (devices, audio refs, volumes, sends, automation) and handle missing elements gracefully.
4. No external dependencies beyond Python stdlib.
5. Can be built incrementally: start with track listing and MIDI notes, add device parsing, add audio clip refs, etc.
6. Total implementation effort for a comprehensive read-only parser: 2-3 days.

pyableton's main value -- the declarative annotation-to-XML mapping pattern in `AbletonComponent` -- is a good idea but poorly executed (no error handling, no optional fields). That pattern could be borrowed and improved in a custom implementation.

---

## Summary Table

| Criterion | pyableton | DIY gzip+ET | dawtool | loive |
|---|---|---|---|---|
| MIDI notes | Yes | Yes (manual) | No | No |
| Audio clips/refs | No | Yes | No | No |
| Devices/plugins | No | Yes | No | Yes (old) |
| Volume/sends | No | Yes | No | No |
| Tempo | Yes | Yes | Yes | No |
| Time markers | No | Yes | Yes (best) | No |
| Automation | Partial | Yes | Partial | No |
| Crash resilience | Poor | You control | Good | Unknown |
| Maintenance | Stale (2024-02) | N/A | Stale (2021) | Dead (2013) |
| Dependencies | muspy, pandas | None | None | colorama |
| Write .als | No | Possible | No | No |
