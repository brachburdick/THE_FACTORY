# ableton-mcp: Agent Workflow Fitness

Assessment of how well ableton-mcp supports the als-reader pipeline goals:
read, understand, write, and give feedback on Ableton Live projects.

## Capability Matrix

| Agent Goal | Support Level | Notes |
|------------|--------------|-------|
| Read project structure | Good | Tracks, clips, devices, scenes, arrangement |
| Read MIDI content | Good | Full note data (pitch, time, duration, velocity) |
| Read audio content | None | No waveform, spectral, or audio file access |
| Read mix state | Good | Volumes, pans, sends, device params |
| Read metering | Blocked | Remote Script has it, MCP server doesn't expose it |
| Write MIDI | Good | Full CRUD + quantize/humanize/transpose |
| Write arrangement | Partial | Scenes and locators only, no arrangement clips |
| Write devices | Good | Load instruments/effects, set parameters |
| Give mix feedback | Structural only | Can see settings, can't hear/analyze audio |
| Compare versions | None | No diffing, no version awareness |

## Reading a Project (What You Get)

An agent can reconstruct the full project graph:

```
Session
├── tempo, time_signature, key
├── Track[0..N]
│   ├── name, type, color, volume, pan, mute, solo, arm
│   ├── input_routing, output_routing
│   ├── Device[0..M]
│   │   ├── name, type, on/off
│   │   └── Parameter[0..P] (name, value, min, max)
│   └── Clip[0..S] (per scene slot)
│       ├── name, color, loop_start, loop_end
│       ├── Note[] (pitch, start, duration, velocity)  [MIDI only]
│       ├── gain, pitch, warp_mode, warp_markers        [audio only]
│       └── automation envelopes
├── Scene[0..S]
│   └── name, color
├── ReturnTrack[0..R]
│   └── name, volume, pan, devices
├── MasterTrack
│   └── volume, pan, devices
└── Arrangement
    ├── length, loop settings
    └── Locator[] (time, name)
```

**Cost:** One tool call per entity. Scanning a 30-track session with 5 devices each:
- 1 × `get_session_info`
- 30 × `get_track_info`
- 150 × `get_device_parameters`
- N × `get_clip_notes` (per populated clip slot)
- 1 × `get_all_scenes`
- 1 × `get_return_tracks`
- 1 × `get_master_info`
= **~200+ tool calls** for a full snapshot

No batch operations exist. This is the biggest gap for agent workflows.

## Writing MIDI (Example Workflow)

```json
// 1. Create clip
{"name": "create_clip", "arguments": {
  "track_index": 0, "clip_index": 0, "length": 8.0
}}

// 2. Add a C major chord (C4-E4-G4)
{"name": "add_notes_to_clip", "arguments": {
  "track_index": 0, "clip_index": 0,
  "notes": [
    {"pitch": 60, "start_time": 0.0, "duration": 2.0, "velocity": 80},
    {"pitch": 64, "start_time": 0.0, "duration": 2.0, "velocity": 75},
    {"pitch": 67, "start_time": 0.0, "duration": 2.0, "velocity": 70}
  ]
}}

// 3. Humanize it
{"name": "humanize_clip_timing", "arguments": {
  "track_index": 0, "clip_index": 0, "amount": 0.03
}}
{"name": "humanize_clip_velocity", "arguments": {
  "track_index": 0, "clip_index": 0, "amount": 0.08
}}
```

## Mix Feedback (What's Possible)

An agent CAN provide structural feedback:
- "Track 3 (Bass) and Track 7 (Sub) both output to Master with no EQ — potential low-end conflict"
- "Your reverb return has 4 sends but return volume is at 0 — dead signal path"
- "Kick is panned L 0.3 — unusual for a kick, likely unintentional"
- "Track 12 has a compressor with ratio 20:1 and threshold -5dB — effectively a limiter"

An agent CANNOT provide perceptual feedback:
- "Your mix is muddy at 200Hz" (no spectral analysis)
- "The snare is too quiet relative to the kick" (no metering)
- "The stereo image is unbalanced" (no correlation metering)

## Latency Estimates

| Operation | Estimated Latency |
|-----------|------------------|
| Simple read (get_track_info) | 5–50ms |
| Write operation (set_track_volume) | 50–200ms |
| Full 30-track scan | 1–5 seconds |
| Full project dump (large session) | 10–30 seconds |

All synchronous. No streaming, no progress callbacks.

## Critical Gaps for als-reader

1. **No batch/snapshot** — Need a `get_project_snapshot` wrapper to avoid 200+ tool calls
2. **No audio analysis** — Can't read waveforms, spectral content, or audio files
3. **No arrangement clips** — Session view only; can't read/write arrangement timeline
4. **No metering** — Remote Script has `get_output_meter` but MCP doesn't expose it
5. **No version comparison** — Can't diff two project states
6. **No clip content for audio tracks** — Can get gain/pitch/warp but not the audio itself

## Recommendations

### If using ableton-mcp as-is
- Build a wrapper that batches `get_track_info` + `get_device_parameters` into a single
  "scan project" operation on the agent side
- Accept that feedback will be structural (settings-based), not perceptual (audio-based)
- Use for MIDI writing workflows — that's where it shines

### If forking
1. Add `get_project_snapshot` — single command that returns full project graph
2. Surface metering tools (`get_output_meter` already in Remote Script)
3. Add arrangement clip read/write
4. Add MCP resources for project state (e.g., `ableton://session/tracks`)
5. Consider streaming transport for long operations
