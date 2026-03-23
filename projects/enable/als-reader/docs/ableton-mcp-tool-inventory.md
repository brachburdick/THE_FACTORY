# ableton-mcp: Complete Tool Inventory

128 MCP tools across 19 domains. R = Read, W = Write, X = Execute.

## Summary by Domain

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
| System & Utility | 3 | 1 | 2 | 7 |
| AI Helpers | 1 | 2 | 0 | 3 |
| Groups | 0 | 0 | 3 | 3 |
| Groove | 1 | 1 | 1 | 3 |
| **TOTAL** | **~39** | **~41** | **~45** | **~128** |

---

## Transport & Session (10)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `health_check` | R | — | Check if Ableton is connected |
| `get_playback_position` | R | — | Current position + transport state |
| `get_session_info` | R | — | Tracks, scenes, tempo, time sig |
| `start_playback` | X | — | Play |
| `stop_playback` | X | — | Stop |
| `start_recording` | X | — | Start recording |
| `stop_recording` | X | — | Stop recording |
| `toggle_session_record` | X | — | Toggle session record |
| `toggle_arrangement_record` | X | — | Toggle arrangement record |
| `set_overdub` | W | `enabled: bool` | Enable/disable overdub |

## Track Management (18)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `get_track_info` | R | `track_index: int` | Name, type, devices, clips, vol/pan/mute/solo/arm |
| `get_track_color` | R | `track_index: int` | Color index |
| `get_track_monitoring` | R | `track_index: int` | Monitoring mode (in/auto/off) |
| `create_midi_track` | X | `index: int = -1` | Create MIDI track |
| `create_audio_track` | X | `index: int = -1` | Create audio track |
| `set_track_name` | W | `track_index: int, name: str` | Rename |
| `set_track_mute` | W | `track_index: int, mute: bool` | Mute/unmute |
| `set_track_solo` | W | `track_index: int, solo: bool` | Solo/unsolo |
| `set_track_arm` | W | `track_index: int, arm: bool` | Arm/disarm |
| `set_track_volume` | W | `track_index: int, volume: float` | Volume (0.0–1.0) |
| `set_track_pan` | W | `track_index: int, pan: float` | Pan (-1.0 to 1.0) |
| `set_track_color` | W | `track_index: int, color: int` | Color (0–69) |
| `set_track_monitoring` | W | `track_index: int, monitoring: str` | Monitoring mode |
| `delete_track` | X | `track_index: int` | Delete |
| `duplicate_track` | X | `track_index: int` | Duplicate with clips/devices |
| `freeze_track` | X | `track_index: int` | Freeze for CPU |
| `flatten_track` | X | `track_index: int` | Flatten frozen → audio |
| `unarm_all` | X | — | Unarm all tracks |

## Clip Operations (12)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `create_clip` | X | `track_index, clip_index, length=4.0` | Create MIDI clip |
| `delete_clip` | X | `track_index, clip_index` | Delete |
| `duplicate_clip` | X | `track_index, clip_index` | Duplicate → next empty slot |
| `fire_clip` | X | `track_index, clip_index` | Launch |
| `stop_clip` | X | `track_index, clip_index` | Stop |
| `select_clip` | X | `track_index, clip_index` | Select slot |
| `capture_midi` | X | — | Capture recently played MIDI |
| `set_clip_name` | W | `track_index, clip_index, name` | Rename |
| `set_clip_color` | W | `track_index, clip_index, color` | Set color |
| `set_clip_loop` | W | `track_index, clip_index, loop_start, loop_end, looping` | Loop settings |
| `get_clip_color` | R | `track_index, clip_index` | Get color |
| `get_clip_loop` | R | `track_index, clip_index` | Get loop settings |

## MIDI Note Editing (8)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `get_clip_notes` | R | `track_index, clip_index` | All MIDI notes |
| `add_notes_to_clip` | W | `track_index, clip_index, notes: List[Dict]` | Add notes |
| `remove_notes` | W | `track_index, clip_index, from_time, time_span, from_pitch, pitch_span` | Remove range |
| `remove_all_notes` | W | `track_index, clip_index` | Clear all |
| `transpose_notes` | W | `track_index, clip_index, semitones: int` | Transpose |
| `quantize_clip_notes` | W | `track_index, clip_index, grid=0.25` | Quantize to grid |
| `humanize_clip_timing` | W | `track_index, clip_index, amount=0.05` | Timing variation |
| `humanize_clip_velocity` | W | `track_index, clip_index, amount=0.1` | Velocity variation |

**Note format for `add_notes_to_clip`:**
```json
{"pitch": 60, "start_time": 0.0, "duration": 0.5, "velocity": 100, "mute": false}
```

## Audio Clip Editing (8)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `get_clip_gain` | R | `track_index, clip_index` | Clip gain |
| `set_clip_gain` | W | `track_index, clip_index, gain: float` | Gain in dB |
| `get_clip_pitch` | R | `track_index, clip_index` | Pitch shift |
| `set_clip_pitch` | W | `track_index, clip_index, pitch: int` | Pitch (-48 to +48 st) |
| `get_clip_warp_info` | R | `track_index, clip_index` | Warp mode + settings |
| `get_warp_markers` | R | `track_index, clip_index` | All warp markers |
| `set_clip_warp_mode` | W | `track_index, clip_index, warp_mode: str` | beats/tones/texture/repitch/complex/complex_pro |
| `add_warp_marker` | W | `track_index, clip_index, beat_time, sample_time=None` | Add marker |
| `delete_warp_marker` | W | `track_index, clip_index, beat_time` | Delete marker |

## Clip Automation (3)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `get_clip_automation` | R | `track_index, clip_index, parameter_name` | Read envelope |
| `set_clip_automation` | W | `track_index, clip_index, parameter_name, envelope_data` | Write envelope |
| `clear_clip_automation` | X | `track_index, clip_index, parameter_name` | Clear envelope |

## Device Management (8)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `get_device_parameters` | R | `track_index, device_index` | All parameters |
| `get_device_by_name` | R | `track_index, device_name` | Find device |
| `set_device_parameter` | W | `track_index, device_index, parameter_index, value` | Set param |
| `toggle_device` | W | `track_index, device_index` | On/off |
| `load_instrument_or_effect` | X | `track_index, uri` | Load by browser URI |
| `move_device_left` | X | `track_index, device_index` | Reorder |
| `move_device_right` | X | `track_index, device_index` | Reorder |
| `delete_device` | X | `track_index, device_index` | Remove |

## Rack Devices (2)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `get_rack_chains` | R | `track_index, device_index` | Chains from rack |
| `select_rack_chain` | X | `track_index, device_index, chain_index` | Select chain |

## Scene Management (9)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `get_all_scenes` | R | — | All scene info |
| `get_scene_color` | R | `scene_index` | Scene color |
| `create_scene` | X | `index=-1` | Create |
| `delete_scene` | X | `scene_index` | Delete |
| `duplicate_scene` | X | `scene_index` | Duplicate |
| `fire_scene` | X | `scene_index` | Launch |
| `stop_scene` | X | `scene_index` | Stop |
| `set_scene_name` | W | `scene_index, name` | Rename |
| `set_scene_color` | W | `scene_index, color` | Set color |
| `select_scene` | X | `scene_index` | Select |

## Return Tracks & Sends (6)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `get_return_tracks` | R | — | All return track info |
| `get_return_track_info` | R | `return_index` | Single return details |
| `get_send_level` | R | `track_index, send_index` | Send level |
| `set_send_level` | W | `track_index, send_index, level` | Set level (0.0–1.0) |
| `set_return_volume` | W | `return_index, volume` | Return volume |
| `set_return_pan` | W | `return_index, pan` | Return pan |

## I/O Routing (6)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `get_track_input_routing` | R | `track_index` | Current input routing |
| `get_track_output_routing` | R | `track_index` | Current output routing |
| `get_available_inputs` | R | `track_index` | Available inputs |
| `get_available_outputs` | R | `track_index` | Available outputs |
| `set_track_input_routing` | W | `track_index, routing_type, routing_channel=""` | Set input |
| `set_track_output_routing` | W | `track_index, routing_type, routing_channel=""` | Set output |

## Arrangement (6)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `get_arrangement_length` | R | — | Length + loop settings |
| `get_locators` | R | — | All locators/cue points |
| `set_arrangement_loop` | W | `start, end, enabled=True` | Set loop region |
| `jump_to_time` | X | `time: float` | Jump to beats position |
| `create_locator` | X | `time, name=""` | Create locator |
| `delete_locator` | X | `locator_index` | Delete locator |

## View & Navigation (4)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `get_current_view` | R | — | Current view state |
| `focus_view` | X | `view_name: str` | Session/Arranger/Detail |
| `select_track` | X | `track_index` | Select track |
| `set_tempo` | W | `tempo: float` | Set BPM |

## Master Track (3)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `get_master_info` | R | — | Volume, pan, devices |
| `set_master_volume` | W | `volume: float` | Volume (0.0–1.0) |
| `set_master_pan` | W | `pan: float` | Pan (-1.0 to 1.0) |

## Browser (7)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `get_browser_tree` | R | `category_type="all"` | Hierarchical categories |
| `get_browser_items_at_path` | R | `path: str` | Items at path |
| `search_browser` | R | `query, category="all"` | Search items |
| `browse_path` | R | `path: list` | Navigate by path list |
| `load_item_to_track` | X | `track_index, uri` | Load to track |
| `load_item_to_return` | X | `return_index, uri` | Load to return |
| `load_drum_kit` | X | `track_index, rack_uri, kit_path` | Load drum rack + kit |

## System & Utility (7)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `undo` | X | — | Undo |
| `redo` | X | — | Redo |
| `get_cpu_load` | R | — | CPU load |
| `get_session_path` | R | — | Session file path |
| `is_session_modified` | R | — | Unsaved changes? |
| `get_metronome_state` | R | — | Metronome on/off |
| `set_metronome` | W | `enabled: bool` | Toggle metronome |

## AI Music Helpers (3)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `get_scale_notes` | R | `root: int, scale_type="major"` | Notes in scale (13 types) |
| `generate_drum_pattern` | W | `track_index, clip_index, style="basic", length=4.0` | Generate pattern |
| `generate_bassline` | W | `track_index, clip_index, root=36, scale_type="minor", length=4.0` | Generate bassline |

**Scale types:** major, minor, dorian, phrygian, lydian, mixolydian, locrian,
harmonic_minor, melodic_minor, pentatonic_major, pentatonic_minor, blues, chromatic

**Drum styles:** basic, house, hiphop, dnb, random

## Group Tracks (3)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `create_group_track` | X | `track_indices: list, name="Group"` | Group tracks |
| `fold_track` | X | `track_index` | Collapse group |
| `unfold_track` | X | `track_index` | Expand group |

## Groove (3)

| Tool | R/W/X | Params | Description |
|------|-------|--------|-------------|
| `get_groove_pool` | R | — | Available grooves |
| `apply_groove` | W | `track_index, clip_index, groove_index` | Apply groove |
| `commit_groove` | X | `track_index, clip_index` | Commit permanently |

---

## Unsurfaced Remote Script Commands

The Remote Script handles 200+ commands. These are NOT exposed as MCP tools but exist
in the TCP protocol:

- **Drum Rack Pads:** mute/solo/get pad name
- **Simpler/Sampler:** sample info, parameters
- **Clip Launch Modes:** get/set launch mode, follow actions
- **Clip Fades:** get/set fade in/out
- **Crossfader:** get/set assignment, position
- **Song Properties:** root note, scale name, swing amount
- **Punch In/Out:** enable/disable
- **Count-In:** get/set duration
- **Exclusive Modes:** solo/arm exclusivity
- **Track Metering:** output meter values (peak/RMS)
- **Clip Properties:** RAM mode, velocity amount
- **Grid Quantization:** get/set grid size
- **Draw Mode / Follow / Zoom:** arrangement view controls
