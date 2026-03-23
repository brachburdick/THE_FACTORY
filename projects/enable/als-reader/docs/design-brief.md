# ALS Reader: Custom Parser Design Brief

**Date:** 2026-03-20
**Context:** Research on pyableton and alternatives concluded that a custom gzip+xml.etree parser is the right approach for an agent-facing ALS reading tool.

---

## Goals

1. **Read .als files reliably** across Ableton versions (8+, targeting 11-12 primarily)
2. **Extract all data an agent needs** to give feedback on arrangement, mix, sound design, and MIDI writing
3. **Graceful degradation** -- missing/unknown XML elements should never crash, just produce None/empty
4. **Zero external dependencies** beyond Python stdlib
5. **Agent-friendly output** -- structured data suitable for LLM consumption (JSON-serializable)
6. **Write capability as a stretch goal** -- round-trip .als modification

---

## Priority Data to Extract

### Tier 1: Core (needed for basic project understanding)
- Track listing (type, name, color, group membership, arm/solo/mute state)
- Tempo (manual + automation envelope)
- Time signature
- Transport state (loop region, song length)
- Locators / markers

### Tier 2: Arrangement (needed for arrangement feedback)
- MIDI clips (position, length, name, color)
- MIDI notes (pitch, time, duration, velocity, probability)
- Audio clips (position, length, name, sample file path, warp mode, gain)
- Clip slots (session view) with launch settings
- Scenes

### Tier 3: Mix (needed for mix balance feedback)
- Volume (per-track, master)
- Pan (per-track, master)
- Send levels (per-track)
- I/O routing (audio + MIDI input/output targets)

### Tier 4: Sound Design (needed for sound design feedback)
- Device chains (ordered list of devices per track)
- Device types: native instruments, native effects, VST/AU plugins, Max4Live
- Device parameters (name + current value for key parameters)
- Racks (instrument, effect, drum) with chain structure
- Macro mappings

### Tier 5: Automation & Detail
- Per-track automation envelopes (parameter ID, breakpoints)
- Clip envelopes
- Groove pool settings
- Follow actions
- Warp markers on audio clips
- Freeze state

---

## Architecture Sketch

```
als_reader/
├── __init__.py          # Public API: load(), ALSProject
├── parser.py            # gzip decompress + ET parse, version detection
├── models.py            # Dataclasses for all domain objects
├── extractors/
│   ├── tracks.py        # Track listing, names, colors, groups
│   ├── clips.py         # MIDI clips, audio clips, clip slots
│   ├── midi.py          # MIDI notes from clips
│   ├── mixer.py         # Volume, pan, sends
│   ├── devices.py       # Device chains, plugins, racks
│   ├── automation.py    # Automation envelopes, clip envelopes
│   ├── transport.py     # Tempo, time sig, markers, locators
│   └── scenes.py        # Session view scenes
└── serialize.py         # to_json(), to_dict() for agent consumption
```

### Key Design Decisions

**Dataclasses, not custom base classes.** pyableton's `AbletonComponent` with annotation-driven parsing is clever but creates tight coupling between Python types and XML structure. Use plain dataclasses with explicit extractor functions that know how to safely navigate the XML tree.

**Optional everything.** Every field on every model should be `Optional[T]` or have a sensible default. An extractor that can't find an XML element returns None, never raises.

**Version detection first.** Read `root.attrib['Creator']` (e.g., `"Ableton Live 11.3.13"`) before parsing. Store it on the project object. Extractors can branch on version if needed.

**Flat access paths.** Unlike pyableton's 8-level nesting, provide convenience accessors:
```python
project = als_reader.load("song.als")
project.tracks          # list[Track]
project.tracks[0].clips # list[Clip] (arrangement + session merged)
project.tracks[0].devices  # list[Device]
project.tempo           # float (or TempoInfo with automation)
project.markers         # list[Marker]
```

**JSON-serializable output.** Every model has `to_dict()`. The top-level `project.to_json()` produces a single JSON document suitable for stuffing into an LLM context window.

---

## What pyableton Got Right (borrow these)

1. **Snake_case to CamelCase mapping** for XML element names -- useful convention
2. **muspy/pandas integration for MIDI** -- we should offer DataFrame export for note analysis
3. **KeyTrack grouping** -- organizing notes by pitch is useful for pattern analysis

## What pyableton Got Wrong (avoid these)

1. **No optional field handling** -- any missing XML element crashes
2. **Commented-out fields instead of proper stubs** -- half-implemented classes that look complete
3. **Heavy required dependencies** (muspy) for optional features
4. **No version detection** -- assumes one XML schema fits all
5. **Deep nesting without convenience accessors** -- 8 levels to reach a MIDI note

---

## Agent Use Cases This Enables

With a complete parser, an agent could:

| Feedback Area | Data Required | Tier |
|---|---|---|
| "Is this arrangement well-structured?" | Track list, clip positions, markers, tempo | 1-2 |
| "How's the mix balance?" | Volume, pan, sends per track | 3 |
| "What plugins are on the bass track?" | Device chains, plugin names | 4 |
| "Are the MIDI velocities too flat?" | MIDI notes with velocity data | 2 |
| "Is there sidechain compression?" | Device chains + routing | 4 |
| "Are there any empty tracks?" | Track list + clip count per track | 1-2 |
| "What key is this in?" | Scale info, or MIDI note analysis | 1-2 |
| "Is the low end muddy?" | Requires audio analysis -- outside parser scope | N/A |
| "Does this sound good?" | Requires audio playback -- outside parser scope | N/A |

### Out of Scope (requires audio analysis, not XML parsing)
- Spectral/frequency content assessment
- Audio quality evaluation
- Loudness measurement
- Actual sound of any track
