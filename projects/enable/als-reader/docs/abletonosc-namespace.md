# AbletonOSC — Complete OSC Address Namespace

> Extracted from source: https://github.com/ideoforms/AbletonOSC
> Researched: 2026-03-20

For every property listed as R/W, four addresses exist:
- `/live/{domain}/get/{property}` — read
- `/live/{domain}/set/{property}` — write
- `/live/{domain}/start_listen/{property}` — subscribe to changes
- `/live/{domain}/stop_listen/{property}` — unsubscribe

For read-only properties, only `get`, `start_listen`, `stop_listen` exist.

---

## Application

| Address | Type | R/W | Description |
|---------|------|-----|-------------|
| `/live/test` | Action | — | Returns `"ok"` (health check) |
| `/live/api/reload` | Action | — | Hot-reload all handler modules |
| `/live/api/get/log_level` | GET | R | Current log level |
| `/live/api/set/log_level` | SET | W | debug/info/warning/error/critical |
| `/live/api/show_message` | Action | — | Show message in Ableton status bar |
| `/live/application/get/version` | GET | R | Returns (major, minor) |
| `/live/application/get/average_process_usage` | GET | R | CPU usage float |
| `/live/startup` | Notification | — | Sent on init (outbound only) |
| `/live/error` | Notification | — | Sent on error (outbound only) |

---

## Song — Transport & Global

### Methods (fire-and-forget, no return)

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

### Read-Write Properties

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

### Read-Only Properties

| Property | Type |
|----------|------|
| `is_playing` | bool |
| `can_undo` | bool |
| `can_redo` | bool |
| `song_length` | float |
| `session_record_status` | int |

### Special Song Queries

| Address | Args | Returns |
|---------|------|---------|
| `/live/song/get/num_tracks` | — | count |
| `/live/song/get/num_scenes` | — | count |
| `/live/song/get/track_names` | `[start, end]` | name, name, ... |
| `/live/song/get/scenes/name` | `[start, end]` | name, name, ... |
| `/live/song/get/cue_points` | — | name, time, name, time, ... (interleaved) |
| `/live/song/get/track_data` | `track_min, track_max, prop_specs...` | Flattened property values |
| `/live/song/export/structure` | — | Writes JSON to `{tmpdir}/abletonosc-song-structure.json` |

### Cue Points

| Address | Args |
|---------|------|
| `/live/song/cue_point/jump` | index OR name (string) |
| `/live/song/cue_point/add_or_delete` | — (at current cursor) |
| `/live/song/cue_point/set/name` | index, new_name |

### Beat Listener

| Address | Description |
|---------|-------------|
| `/live/song/start_listen/beat` | Subscribe to beat events |
| `/live/song/stop_listen/beat` | Unsubscribe |
| `/live/song/get/beat` | Response: beat_number (int, floor of current_song_time) |

---

## Track

All take `track_index` as first arg. Use `"*"` as track_index to query all tracks.

### Methods

| Address | Args |
|---------|------|
| `/live/track/stop_all_clips` | track_index |
| `/live/track/delete_device` | track_index, device_index |
| `/live/track/delete_clip` | track_index, clip_index |

### Read-Write Properties

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

### Read-Only Properties

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

### Mixer (Read-Write)

| Property | Args | Value | Listen? |
|----------|------|-------|---------|
| `volume` | track_index | float 0.0–1.0 | Yes |
| `panning` | track_index | float -1.0–1.0 | Yes |
| `send` | track_index, send_index | float | No |

### I/O Routing

| Address Pattern | R/W |
|-----------------|-----|
| `/live/track/{get,set}/output_routing_type` | R/W |
| `/live/track/{get,set}/output_routing_channel` | R/W |
| `/live/track/{get,set}/input_routing_type` | R/W |
| `/live/track/{get,set}/input_routing_channel` | R/W |
| `/live/track/get/available_output_routing_types` | R |
| `/live/track/get/available_output_routing_channels` | R |
| `/live/track/get/available_input_routing_types` | R |
| `/live/track/get/available_input_routing_channels` | R |

### Batch Queries (Read-Only)

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
| `/live/track/get/devices/class_name` | e.g. "Operator", "Reverb", "AuPluginDevice" |
| `/live/track/get/devices/can_have_chains` | bool per device |

---

## Clip

All take `track_index, clip_index` as first two args. Returns prepend both indices.

### Methods

| Address | Extra Args |
|---------|------------|
| `/live/clip/fire` | — |
| `/live/clip/stop` | — |
| `/live/clip/duplicate_loop` | — |
| `/live/clip/remove_notes_by_id` | note_id |

### Read-Write Properties

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

### Read-Only Properties

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

### MIDI Note Operations

| Address | Direction | Args | Returns |
|---------|-----------|------|---------|
| `/live/clip/get/notes` | GET | [pitch_start, pitch_span, time_start, time_span] | pitch, start, duration, velocity, mute (×N, 5 values per note) |
| `/live/clip/add/notes` | WRITE | pitch, start, duration, velocity, mute (×N) | — |
| `/live/clip/remove/notes` | WRITE | [pitch_start, pitch_span, time_start, time_span] | — |

Default range for get/remove: pitch 0–127, time -8192 to 8192.

### Clip Filtering

| Address | Args |
|---------|------|
| `/live/clips/filter` | note_name, ... (e.g. "C", "E", "G" — mutes clips missing these notes) |
| `/live/clips/unfilter` | [track_start, track_end] — unmutes all clips in range |

---

## Clip Slot

All take `track_index, clip_index`.

### Methods

| Address | Extra Args |
|---------|------------|
| `/live/clip_slot/fire` | — |
| `/live/clip_slot/stop` | — |
| `/live/clip_slot/create_clip` | length |
| `/live/clip_slot/delete_clip` | — |
| `/live/clip_slot/duplicate_clip_to` | target_track, target_clip |

### Read-Only Properties

`has_clip`, `controls_other_clips`, `is_group_slot`, `is_playing`, `is_triggered`, `playing_status`, `will_record_on_start`

### Read-Write Properties

`has_stop_button`

---

## Device

All take `track_index, device_index`.

### Read-Only Properties

`class_name`, `name`, `type` (0=audio_effect, 1=instrument, 2=midi_effect)

### Bulk Parameter Queries

| Address | Direction | Returns |
|---------|-----------|---------|
| `/live/device/get/num_parameters` | R | count |
| `/live/device/get/parameters/name` | R | name per param |
| `/live/device/get/parameters/value` | R | value per param |
| `/live/device/get/parameters/min` | R | min per param |
| `/live/device/get/parameters/max` | R | max per param |
| `/live/device/get/parameters/is_quantized` | R | bool per param |
| `/live/device/set/parameters/value` | W | set all values at once |

### Individual Parameter Access

| Address | Direction | Extra Args |
|---------|-----------|------------|
| `/live/device/get/parameter/value` | R | param_index |
| `/live/device/get/parameter/value_string` | R | param_index (returns display string, e.g. "2500 Hz") |
| `/live/device/set/parameter/value` | W | param_index, value |
| `/live/device/get/parameter/name` | R | param_index |
| `/live/device/start_listen/parameter/value` | LISTEN | param_index (sends value + value_string on change) |
| `/live/device/stop_listen/parameter/value` | UNLISTEN | param_index |

---

## Scene

All take `scene_index`.

### Methods

| Address | Args |
|---------|------|
| `/live/scene/fire` | scene_index |
| `/live/scene/fire_as_selected` | scene_index |
| `/live/scene/fire_selected` | — (fires currently selected scene) |

### Read-Write Properties

`name`, `color`, `color_index`, `tempo`, `tempo_enabled`, `time_signature_numerator`, `time_signature_denominator`, `time_signature_enabled`

### Read-Only Properties

`is_empty`, `is_triggered`

---

## View

| Address | R/W | Listen? |
|---------|-----|---------|
| `/live/view/{get,set}/selected_scene` | R/W | Yes |
| `/live/view/{get,set}/selected_track` | R/W | Yes |
| `/live/view/{get,set}/selected_clip` | R/W | No |
| `/live/view/{get,set}/selected_device` | R/W | No |

---

## MIDI Map

| Address | Args |
|---------|------|
| `/live/midimap/map_cc` | track_index, device_index, param_index, midi_channel, cc_number |
