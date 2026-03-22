# AbletonOSC Deep-Dive Research Report

> **Date:** 2026-03-20
> **Source:** https://github.com/ideoforms/AbletonOSC
> **Stars:** 707 | **Forks:** 123 | **License:** MIT | **Last push:** 2025-11-19
> **Status:** Beta (active community, slow merge cadence)

---

## 1. Protocol & Architecture

### What It Actually Is

AbletonOSC is a **MIDI Remote Script** (Python `ControlSurface` subclass), NOT a Max4Live device. It runs inside Ableton's embedded Python runtime with no Max4Live dependency.

### Port Configuration

| Port | Direction | Binding |
|------|-----------|---------|
| **11000** | Client → AbletonOSC | Binds `0.0.0.0` (all interfaces) |
| **11001** | AbletonOSC → Client | Sends to `(sender_ip, 11001)` |

### Message Flow

1. Client sends UDP datagram to port 11000
2. `OSCServer.process()` reads from non-blocking socket in a loop during `Manager.tick()`
3. Message parsed as `OscMessage` or `OscBundle` (bundles recursively unpacked)
4. Address matched against callback dict (exact match or `*` wildcard → `[^/]+` regex)
5. Callback invoked, return value sent back to sender on port 11001
6. Responses echo the same OSC address, prepended with object indices

### Tick-Based Processing

Live's embedded Python does NOT support threading (historically). `Manager.tick()` is called every **~100ms** via `self.schedule_message(1, self.tick)`, processing all queued UDP datagrams synchronously in a non-blocking loop.

### Address Convention

```
/live/{domain}/{verb}/{property}  [args...]
```

Verbs: `get`, `set`, `start_listen`, `stop_listen`, or method name directly.

### Listener/Subscription Mechanism

Any property supporting `get` also supports `start_listen` and `stop_listen`:
- **`/live/{domain}/start_listen/{property} [args]`** — registers via `add_{property}_listener()`. Sends current value immediately, then on every change.
- **`/live/{domain}/stop_listen/{property} [args]`** — removes via `remove_{property}_listener()`.
- Listener responses are sent to `/live/{domain}/get/{property}` (same as a query response).

### Wildcard Support

Any OSC address containing `*` matches `[^/]+`. Example: `/live/track/get/*` triggers all matching handlers.

### Bundled Python Client

`client/client.py` provides `AbletonOSCClient`:
- `send_message(address, params)` — fire-and-forget
- `query(address, params, timeout=0.150)` — send and block for response
- `send_bundle(messages)` — send OSC bundle
- `set_handler(address, fn)` — register callback for incoming messages
- `await_message(address, timeout)` — block until specific address received

---

## 2. Complete OSC Address Namespace

### Application

| Address | Type | R/W | Description |
|---------|------|-----|-------------|
| `/live/test` | Action | — | Returns `"ok"` (health check) |
| `/live/api/reload` | Action | — | Hot-reload all handler modules |
| `/live/api/get/log_level` | GET | R | Current log level |
| `/live/api/set/log_level` | SET | W | Set log level (debug/info/warning/error/critical) |
| `/live/api/show_message` | Action | — | Show message in Ableton status bar |
| `/live/application/get/version` | GET | R | Returns (major, minor) |
| `/live/application/get/average_process_usage` | GET | R | CPU usage float |
| `/live/startup` | Notification | — | Sent automatically on init |
| `/live/error` | Notification | — | Sent on error with message string |

### Song — Transport & Global

**Methods (fire-and-forget):**

| Address | Args |
|---------|------|
| `/live/song/start_playing` | — |
| `/live/song/stop_playing` | — |
| `/live/song/continue_playing` | — |
| `/live/song/stop_all_clips` | — |
| `/live/song/tap_tempo` | — |
| `/live/song/undo` | — |
| `/live/song/redo` | — |
| `/live/song/jump_by` | `beats` (float) |
| `/live/song/jump_to_prev_cue` | — |
| `/live/song/jump_to_next_cue` | — |
| `/live/song/capture_midi` | — |
| `/live/song/capture_and_insert_scene` | — |
| `/live/song/trigger_session_record` | — |
| `/live/song/re_enable_automation` | — |
| `/live/song/set_or_delete_cue` | — |
| `/live/song/force_link_beat_time` | — |
| `/live/song/create_audio_track` | `index` |
| `/live/song/create_midi_track` | `index` |
| `/live/song/create_return_track` | — |
| `/live/song/create_scene` | `index` |
| `/live/song/delete_track` | `index` |
| `/live/song/delete_return_track` | `index` |
| `/live/song/delete_scene` | `index` |
| `/live/song/duplicate_track` | `index` |
| `/live/song/duplicate_scene` | `index` |

**Read-Write Properties** (get/set/start_listen/stop_listen):

| Property | Type |
|----------|------|
| `tempo` | float (BPM) |
| `current_song_time` | float (beats) |
| `loop` | bool |
| `loop_start` | float |
| `loop_length` | float |
| `metronome` | bool |
| `record_mode` | bool |
| `session_record` | bool |
| `arrangement_overdub` | bool |
| `back_to_arranger` | bool |
| `clip_trigger_quantization` | int (enum) |
| `midi_recording_quantization` | int (enum) |
| `groove_amount` | float |
| `signature_numerator` | int |
| `signature_denominator` | int |
| `root_note` | int (0-11) |
| `scale_name` | string |
| `nudge_up` | bool |
| `nudge_down` | bool |
| `punch_in` | bool |
| `punch_out` | bool |
| `is_ableton_link_enabled` | bool |

**Read-Only Properties** (get/start_listen/stop_listen):

| Property | Type |
|----------|------|
| `is_playing` | bool |
| `can_undo` | bool |
| `can_redo` | bool |
| `song_length` | float |
| `session_record_status` | int |

**Special Queries:**

| Address | Args | Returns |
|---------|------|---------|
| `/live/song/get/num_tracks` | — | count |
| `/live/song/get/num_scenes` | — | count |
| `/live/song/get/track_names` | `[start, end]` | name, name, ... |
| `/live/song/get/scenes/name` | `[start, end]` | name, name, ... |
| `/live/song/get/cue_points` | — | name, time, name, time, ... (interleaved) |
| `/live/song/get/track_data` | `track_min, track_max, prop_specs...` | Flattened property values (bulk) |
| `/live/song/export/structure` | — | Writes JSON to `{tmpdir}/abletonosc-song-structure.json` |

**Cue Points:**

| Address | Args |
|---------|------|
| `/live/song/cue_point/jump` | index OR name |
| `/live/song/cue_point/add_or_delete` | — |
| `/live/song/cue_point/set/name` | index, new_name |

**Beat Listener:**

| Address | Description |
|---------|-------------|
| `/live/song/start_listen/beat` | Start sending beat events |
| `/live/song/stop_listen/beat` | Stop beat events |
| `/live/song/get/beat` | Response: beat_number (int) |

### Track

All take `track_index` as first arg. Use `"*"` to query all tracks.

**Methods:**

| Address | Args |
|---------|------|
| `/live/track/stop_all_clips` | track_index |
| `/live/track/delete_device` | track_index, device_index |
| `/live/track/delete_clip` | track_index, clip_index |

**Read-Write Properties** (get/set/start_listen/stop_listen):

| Property | Type |
|----------|------|
| `name` | string |
| `arm` | bool |
| `mute` | bool |
| `solo` | bool |
| `color` | int (RGB) |
| `color_index` | int |
| `current_monitoring_state` | int (0=In, 1=Auto, 2=Off) |
| `fold_state` | int |

**Read-Only Properties** (get/start_listen/stop_listen):

| Property | Type |
|----------|------|
| `can_be_armed` | bool |
| `fired_slot_index` | int |
| `has_audio_input` | bool |
| `has_audio_output` | bool |
| `has_midi_input` | bool |
| `has_midi_output` | bool |
| `is_foldable` | bool |
| `is_grouped` | bool |
| `is_visible` | bool |
| `output_meter_level` | float |
| `output_meter_left` | float |
| `output_meter_right` | float |
| `playing_slot_index` | int |

**Mixer (Read-Write, get/set/start_listen/stop_listen):**

| Property | Args | Value |
|----------|------|-------|
| `volume` | track_index | float 0.0–1.0 |
| `panning` | track_index | float -1.0–1.0 |
| `send` | track_index, send_index | float (no listen support) |

**I/O Routing (get/set per property):**

| Address Pattern | Type |
|-----------------|------|
| `/live/track/{get,set}/output_routing_type` | R/W |
| `/live/track/{get,set}/output_routing_channel` | R/W |
| `/live/track/{get,set}/input_routing_type` | R/W |
| `/live/track/{get,set}/input_routing_channel` | R/W |
| `/live/track/get/available_output_routing_types` | R |
| `/live/track/get/available_output_routing_channels` | R |
| `/live/track/get/available_input_routing_types` | R |
| `/live/track/get/available_input_routing_channels` | R |

**Batch Queries (Read-Only):**

| Address | Returns |
|---------|---------|
| `/live/track/get/clips/name` | name_or_None per slot |
| `/live/track/get/clips/length` | length_or_None per slot |
| `/live/track/get/clips/color` | color_or_None per slot |
| `/live/track/get/arrangement_clips/name` | name per arrangement clip |
| `/live/track/get/arrangement_clips/length` | length per arrangement clip |
| `/live/track/get/arrangement_clips/start_time` | start_time per arrangement clip |
| `/live/track/get/num_devices` | count |
| `/live/track/get/devices/name` | name per device |
| `/live/track/get/devices/type` | 0=audio_effect, 1=instrument, 2=midi_effect |
| `/live/track/get/devices/class_name` | e.g. "Operator", "Reverb" |
| `/live/track/get/devices/can_have_chains` | bool per device |

### Clip

All take `track_index, clip_index` as first two args.

**Methods:**

| Address | Args |
|---------|------|
| `/live/clip/fire` | track_index, clip_index |
| `/live/clip/stop` | track_index, clip_index |
| `/live/clip/duplicate_loop` | track_index, clip_index |
| `/live/clip/remove_notes_by_id` | track_index, clip_index, note_id |

**Read-Write Properties** (get/set/start_listen/stop_listen):

| Property | Type |
|----------|------|
| `name` | string |
| `color` | int (RGB) |
| `color_index` | int |
| `muted` | bool |
| `looping` | bool |
| `loop_start` | float |
| `loop_end` | float |
| `start_marker` | float |
| `end_marker` | float |
| `position` | float |
| `gain` | float |
| `pitch_coarse` | int (semitones) |
| `pitch_fine` | float (cents) |
| `warping` | bool |
| `warp_mode` | int (enum) |
| `launch_mode` | int (enum) |
| `launch_quantization` | int (enum) |
| `legato` | bool |
| `ram_mode` | bool |
| `velocity_amount` | float |

**Read-Only Properties** (get/start_listen/stop_listen):

| Property | Type |
|----------|------|
| `is_midi_clip` | bool |
| `is_audio_clip` | bool |
| `is_playing` | bool |
| `is_recording` | bool |
| `is_triggered` | bool |
| `is_overdubbing` | bool |
| `will_record_on_start` | bool |
| `length` | float (beats) |
| `start_time` | float |
| `end_time` | float |
| `playing_position` | float |
| `file_path` | string |
| `sample_length` | int |
| `gain_display_string` | string |
| `has_groove` | bool |

**MIDI Note Operations:**

| Address | Direction | Args | Returns |
|---------|-----------|------|---------|
| `/live/clip/get/notes` | GET | track, clip, [pitch_start, pitch_span, time_start, time_span] | pitch, start, duration, velocity, mute (×N) |
| `/live/clip/add/notes` | WRITE | track, clip, pitch, start, duration, velocity, mute (×N) | — |
| `/live/clip/remove/notes` | WRITE | track, clip, [pitch_start, pitch_span, time_start, time_span] | — |

**Clip Filtering:**

| Address | Args |
|---------|------|
| `/live/clips/filter` | note_name, ... (mutes clips missing these notes) |
| `/live/clips/unfilter` | [track_start, track_end] |

### Clip Slot

All take `track_index, clip_index`.

**Methods:**

| Address | Args |
|---------|------|
| `/live/clip_slot/fire` | track_index, clip_index |
| `/live/clip_slot/stop` | track_index, clip_index |
| `/live/clip_slot/create_clip` | track_index, clip_index, length |
| `/live/clip_slot/delete_clip` | track_index, clip_index |
| `/live/clip_slot/duplicate_clip_to` | track, clip, target_track, target_clip |

**Read-Only Properties:** `has_clip`, `controls_other_clips`, `is_group_slot`, `is_playing`, `is_triggered`, `playing_status`, `will_record_on_start`

**Read-Write Properties:** `has_stop_button`

### Device

All take `track_index, device_index`.

**Read-Only Properties:** `class_name`, `name`, `type` (0=audio_effect, 1=instrument, 2=midi_effect)

**Bulk Parameter Queries:**

| Address | Direction |
|---------|-----------|
| `/live/device/get/num_parameters` | R |
| `/live/device/get/parameters/name` | R |
| `/live/device/get/parameters/value` | R |
| `/live/device/get/parameters/min` | R |
| `/live/device/get/parameters/max` | R |
| `/live/device/get/parameters/is_quantized` | R |
| `/live/device/set/parameters/value` | W (set all at once) |

**Individual Parameter Access:**

| Address | Direction |
|---------|-----------|
| `/live/device/get/parameter/value` | R |
| `/live/device/get/parameter/value_string` | R (display string, e.g. "2500 Hz") |
| `/live/device/set/parameter/value` | W |
| `/live/device/get/parameter/name` | R |
| `/live/device/start_listen/parameter/value` | LISTEN (sends value + value_string) |
| `/live/device/stop_listen/parameter/value` | UNLISTEN |

### Scene

All take `scene_index`.

**Methods:** `fire`, `fire_as_selected`, `fire_selected` (no arg, fires current selection)

**Read-Write Properties:** `name`, `color`, `color_index`, `tempo`, `tempo_enabled`, `time_signature_numerator`, `time_signature_denominator`, `time_signature_enabled`

**Read-Only Properties:** `is_empty`, `is_triggered`

### View

| Address | R/W |
|---------|-----|
| `/live/view/{get,set}/selected_scene` | R/W + listen |
| `/live/view/{get,set}/selected_track` | R/W + listen |
| `/live/view/{get,set}/selected_clip` | R/W |
| `/live/view/{get,set}/selected_device` | R/W |

### MIDI Map

| Address | Args |
|---------|------|
| `/live/midimap/map_cc` | track, device, param, channel, cc |

---

## 3. Live Object Model Coverage

### What's Covered (~40-50% of LOM)

| LOM Area | Coverage | R/W |
|----------|----------|-----|
| Song (transport, tempo, time sig, cues) | Full | R/W |
| Tracks (audio, MIDI, group) | Good | R/W |
| Track mixer (volume, pan, sends) | Full | R/W |
| Track routing (I/O) | Full | R/W |
| Clips (session view) | Good | R/W |
| MIDI notes | Full | R/W |
| Clip slots | Full | R/W |
| Devices & parameters | Good | R/W |
| Scenes | Good | R/W |
| View/selection | Good | R/W |

### What's Missing

| LOM Area | Impact | Issue/PR |
|----------|--------|----------|
| **Master Track** | Cannot read/set master volume, devices | #47, PR #84, #189 |
| **Return Tracks** | Cannot read/set return track properties | #47, PR #84, #189 |
| **Rack Devices / Chains / DrumPads** | Cannot navigate into Instrument/Effect Racks | #169, #170 |
| **Browser** | Cannot load instruments, effects, samples | #66, #183 |
| **Automation Envelopes** | Cannot read/write automation curves | #112 |
| **Arrangement View clips** | Limited to batch name/length/start_time queries | #124 |
| **Device Variations** (Live 12) | — | PR #167 |
| **Sidechain routing** | — | PR #191 |
| **GroovePool / Groove** | — | — |
| **TuningSystem** (Live 12 microtonality) | — | — |
| **SimplerDevice / WavetableDevice** | No specialized device APIs | — |
| **View scroll/zoom** | — | PR #153 |

---

## 4. Installation & Requirements

### Ableton Version
- **Minimum:** Ableton Live 11
- **Live 12:** Confirmed working by maintainer (ideoforms uses it regularly)
- **No Max4Live dependency** — works with Live Standard

### Installation Path
- **macOS:** `~/Music/Ableton/User Library/Remote Scripts/AbletonOSC/`
- **Windows:** `~\Documents\Ableton\User Library\Remote Scripts\AbletonOSC\`

### Activation
`Preferences → Link / Tempo / MIDI → Control Surface → AbletonOSC`

### OS-Specific Gotchas
- macOS firewall may block UDP 11000/11001
- Known Live 12 quirk: OSC pauses while Ableton's menu bar is open (could not reproduce — #121)

---

## 5. Performance & Reliability

### Latency
- **Tick interval:** ~100ms (10 Hz processing)
- **Client timeout:** 150ms default (one tick + overhead)
- **Round-trip latency:** 100–200ms typical for request/response
- **Listener latency:** Same tick-bound — state changes delivered on next tick

### Rapid-Fire Query Behavior
- Non-blocking socket processes all queued datagrams per tick
- Multiple messages per tick are processed, but all responses emit in the same tick
- **UDP datagram size limit:** Clips with many MIDI notes cause `OSError: Message too long` (#88)
- **No request/response correlation:** No call IDs. Concurrent queries cannot be reliably matched (#108)

### Known Stability Issues

| Issue | Severity | Detail |
|-------|----------|--------|
| Single-client only | High | Second client steals responses from first (#73) |
| Listener index drift | High | Track listeners break on track create/delete/reorder (#31) |
| UDP message overflow | Medium | Large MIDI clips exceed UDP datagram limit (#88) |
| No request IDs | Medium | Cannot correlate responses under concurrent load (#108) |
| MIDI track meter error | Low | `start_listen/output_meter_level` fails on MIDI tracks (#116) |
| Note 127 deletion bug | Low | `/live/clip/remove/notes` without args skips G9 (#190) |

### Threading Note
The maintainer acknowledged threading "could be a gamechanger for latency." The ahujasid/ableton-mcp project proves threaded Remote Scripts work fine in Live 11/12.

---

## 6. Integration Fitness

### Direct python-osc Communication

A Python agent can talk to AbletonOSC directly with `python-osc`:

```python
# Send
from pythonosc.udp_client import SimpleUDPClient
client = SimpleUDPClient("127.0.0.1", 11000)
client.send_message("/live/song/set/tempo", [128.0])

# Receive
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
dispatcher = Dispatcher()
dispatcher.map("/live/song/get/tempo", lambda addr, *args: print(args))
server = ThreadingOSCUDPServer(("127.0.0.1", 11001), dispatcher)
```

### AbletonOSC vs MCP Wrapper

| Factor | Direct AbletonOSC | MCP Wrapper |
|--------|-------------------|-------------|
| Latency | ~100-200ms (1 hop) | ~200-400ms (2 hops) |
| Complexity | Low (UDP fire-and-forget) | Higher (MCP protocol layer) |
| Error handling | Manual (no request IDs) | Wrapper can add correlation |
| Tool discoverability | OSC addresses are flat | MCP provides tool schemas |
| Multi-client | Broken (single client) | Wrapper can multiplex |
| State caching | None | Wrapper can cache |

**Recommendation for agent pipeline:** Build a thin Python adapter layer on `python-osc` rather than going through MCP. The adapter can add request correlation, response caching, and retry logic that AbletonOSC lacks natively.

### "Read Full Project State" Comparison

**Over OSC (live session, ~10-50 tracks):**
1. `/live/song/export/structure` → writes JSON to temp dir (single call, returns full hierarchy including all device parameters)
2. OR sequential: `get/num_tracks` → per-track `get/clips/*`, `get/devices/*` → per-device `get/parameters/*`
3. Estimated time: 1-5 seconds for a medium project via sequential queries, or ~200ms via `export/structure`

**Parsing .als offline:**
- `.als` = gzipped XML
- Contains full arrangement, all clips, automation, device presets, everything
- No Ableton running required
- Complete fidelity — includes automation envelopes, browser references, undo history metadata
- **Much richer** than OSC can ever provide, but read-only

**Hybrid approach for agent pipeline:**
- Parse `.als` for deep analysis (arrangement structure, automation, device chains)
- Use OSC for live queries, state monitoring, and write operations
- Use `export/structure` for quick live snapshot

---

## 7. Ecosystem Role

### MCP Servers

| Project | Stars | Uses AbletonOSC? | Transport |
|---------|-------|-------------------|-----------|
| [ahujasid/ableton-mcp](https://github.com/ahujasid/ableton-mcp) | 2,330 | **No** — custom Remote Script | JSON/TCP (threaded) |
| [Simon-Kansara/ableton-live-mcp-server](https://github.com/Simon-Kansara/ableton-live-mcp-server) | 369 | **Yes** | python-osc → AbletonOSC |
| [uisato/ableton-mcp-extended](https://github.com/uisato/ableton-mcp-extended) | 139 | **No** — extends ahujasid | JSON/TCP + UDP hybrid |
| [nozomi-koborinai/ableton-osc-mcp](https://github.com/nozomi-koborinai/ableton-osc-mcp) | 7 | **Yes** | Go + AbletonOSC |
| [ursaayush/ableton-mcp](https://github.com/ursaayush/ableton-mcp) | 0 | **Yes** | AbletonOSC + ClyphX Pro |

**Key insight:** The dominant MCP project bypasses AbletonOSC entirely with its own threaded Remote Script. This suggests AbletonOSC's tick-based architecture is a liability for agent workloads.

### Related Projects

| Project | Stars | Relationship |
|---------|-------|-------------|
| [pylive](https://github.com/ideoforms/pylive) | 617 | Pythonic OOP wrapper around AbletonOSC (same author) |
| [willrjmarshall/AbletonOSC](https://github.com/willrjmarshall/AbletonOSC) | 34 | Older, unrelated OSC implementation |
| [DrivenByMoss](https://github.com/git-moss/DrivenByMoss) | 738 | Java controller extensions (different paradigm) |

### Is AbletonOSC the Canonical OSC Interface?

**Yes** — it is the most mature, best-maintained, and most widely used OSC interface for Ableton Live. No serious competitor exists in the OSC space. However, the MCP ecosystem has shown that the Remote Script approach (with threading and JSON/TCP) may be a better foundation for AI agent workloads than OSC/UDP.

---

## 8. Strategic Assessment for Agent Pipeline

### Strengths
- Battle-tested OSC namespace covering core LOM operations
- Listener mechanism enables reactive agent patterns
- `export/structure` provides fast full-project snapshot
- MIDI note read/write enables generative composition agents
- Device parameter access enables mixing/sound-design agents

### Weaknesses
- 100ms tick latency is high for rapid agent queries
- Single-client limitation breaks multi-agent scenarios
- No request correlation makes concurrent queries unreliable
- ~50% LOM coverage — missing racks, browser, automation, master/returns
- UDP datagram size limit on large MIDI clips

### Recommendation

For a production agent pipeline, consider a **hybrid architecture**:

1. **Offline analysis:** Parse `.als` files (gzipped XML) for deep project understanding — arrangement structure, automation curves, device chains, browser references. This gives 100% LOM fidelity with no latency concerns.

2. **Live control:** Fork or extend AbletonOSC (or build a custom Remote Script like ahujasid) with:
   - Threading for lower latency
   - Request correlation IDs
   - Multi-client support
   - Coverage for racks/chains, master/return tracks

3. **Transport layer:** Use `python-osc` directly rather than adding an MCP layer. The agent already knows the OSC namespace — MCP adds latency and complexity without proportional benefit for a single-purpose pipeline.

4. **State sync:** Use `export/structure` for periodic full snapshots. Use listeners for real-time delta tracking of playing state, selection, and parameter changes.
