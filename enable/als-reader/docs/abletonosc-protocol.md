# AbletonOSC Protocol & Architecture

> **Source:** https://github.com/ideoforms/AbletonOSC
> **Version:** Beta | **Stars:** 707 | **License:** MIT | **Last push:** 2025-11-19
> **Researched:** 2026-03-20

## What It Actually Is

AbletonOSC is a **MIDI Remote Script** (Python `ControlSurface` subclass), NOT a Max4Live device. It runs inside Ableton's embedded Python runtime with no Max4Live dependency. Works with Live Standard — no Suite required.

## Port Configuration

| Port | Direction | Binding |
|------|-----------|---------|
| **11000** | Client → AbletonOSC | Binds `0.0.0.0` (all interfaces) |
| **11001** | AbletonOSC → Client | Sends to `(sender_ip, 11001)` |

## Message Flow

```
Client (UDP:11000)  ──►  OSCServer.process()  ──►  Callback dispatch
                                                        │
Client (UDP:11001)  ◄──  Response (same OSC address)  ◄─┘
```

1. Client sends UDP datagram to port 11000
2. `OSCServer.process()` reads from non-blocking socket during `Manager.tick()`
3. Message parsed as `OscMessage` or `OscBundle` (bundles recursively unpacked)
4. Address matched against callback dict (exact match or `*` wildcard → `[^/]+` regex)
5. Callback invoked, return value sent back to sender on port 11001
6. Responses echo the same OSC address, prepended with object indices

## Address Convention

```
/live/{domain}/{verb}/{property}  [args...]
```

**Verbs:** `get`, `set`, `start_listen`, `stop_listen`, or method name directly.

**Examples:**
- `/live/song/get/tempo` → returns `(tempo_float)`
- `/live/song/set/tempo 128.0` → sets tempo, no response
- `/live/track/get/volume 0` → returns `(0, volume_float)` (track index echoed)
- `/live/clip/get/notes 0 2` → returns MIDI notes from track 0, clip 2

## Tick-Based Processing

Live's embedded Python does NOT support threading (historically). `Manager.tick()` is called every **~100ms** via `self.schedule_message(1, self.tick)`, processing all queued UDP datagrams synchronously in a non-blocking loop.

**Implications:**
- Maximum polling rate: 10 Hz
- Round-trip latency: 100–200ms typical
- All queued messages per tick are processed, but responses all emit in the same tick
- The ahujasid/ableton-mcp project proves threaded Remote Scripts work in Live 11/12

## Listener/Subscription Mechanism

Any property supporting `get` also supports `start_listen` and `stop_listen`:

```
# Subscribe to tempo changes
/live/song/start_listen/tempo

# AbletonOSC immediately sends current value, then on every change:
# → /live/song/get/tempo  [128.0]

# Unsubscribe
/live/song/stop_listen/tempo
```

- `start_listen` registers via `add_{property}_listener()`. Sends current value immediately, then on every change.
- `stop_listen` removes via `remove_{property}_listener()`.
- Listener responses use the same address as `get` responses (`/live/{domain}/get/{property}`).

## Wildcard Support

Any OSC address containing `*` matches `[^/]+` (any chars except `/`).

```
/live/track/get/*        → triggers ALL track property getters
/live/song/get/*         → triggers ALL song property getters
```

## Bundled Python Client

`client/client.py` provides `AbletonOSCClient`:

| Method | Description |
|--------|-------------|
| `send_message(address, params)` | Fire-and-forget |
| `query(address, params, timeout=0.150)` | Send and block for response |
| `send_bundle(messages)` | Send OSC bundle |
| `set_handler(address, fn)` | Register callback for incoming messages |
| `await_message(address, timeout)` | Block until specific address received |

Default timeout is 150ms (`TICK_DURATION`), accounting for one Ableton tick plus processing overhead.

## Automatic Messages

| Address | When | Payload |
|---------|------|---------|
| `/live/startup` | On AbletonOSC initialization | (none) |
| `/live/error` | On error | error_message (string) |

## Special Capabilities

### Hot Reload
`/live/api/reload` uses `importlib.reload()` on all handler modules, clears all handlers and listeners, and re-initializes. Useful during development.

### Song Structure Export
`/live/song/export/structure` writes a JSON file to `{tmpdir}/abletonosc-song-structure.json` with full track/clip/device hierarchy including all device parameter metadata (name, value, min, max, is_quantized). Single call, ~200ms.

### Bulk Query
`/live/song/get/track_data track_min track_max prop_specs...` returns flattened property values. Property specs use dotted notation: `track.name`, `clip.name`, `clip.length`, `clip_slot.has_clip`, `device.name`.

## Installation

### Requirements
- **Minimum:** Ableton Live 11
- **Live 12:** Confirmed working (maintainer uses it regularly)
- **No Max4Live dependency** — works with Live Standard

### Paths
- **macOS:** `~/Music/Ableton/User Library/Remote Scripts/AbletonOSC/`
- **Windows:** `~\Documents\Ableton\User Library\Remote Scripts\AbletonOSC\`

### Activation
`Preferences → Link / Tempo / MIDI → Control Surface → AbletonOSC`

### OS Gotchas
- macOS firewall may block UDP 11000/11001
- Live 12: OSC may pause while Ableton's menu bar is open (unconfirmed — issue #121)
