# AbletonOSC — LOM Coverage & Known Gaps

> Researched: 2026-03-20

## What's Covered (~40-50% of full LOM)

| LOM Area | Coverage | R/W | Notes |
|----------|----------|-----|-------|
| Song (transport, tempo, time sig, cues) | Full | R/W | |
| Tracks (audio, MIDI, group) | Good | R/W | |
| Track mixer (volume, pan, sends) | Full | R/W | Send has no listen support |
| Track routing (I/O) | Full | R/W | |
| Clips (session view) | Good | R/W | |
| MIDI notes | Full | R/W | 5-value tuple: pitch, start, duration, velocity, mute |
| Clip slots | Full | R/W | |
| Devices & parameters | Good | R/W | Flat list only, no rack traversal |
| Scenes | Good | R/W | |
| View/selection | Good | R/W | |

## What's Missing

| LOM Area | Impact | Issue/PR | Why It Matters for Agents |
|----------|--------|----------|---------------------------|
| **Master Track** | High | #47, PR #84, #189 | Cannot read/set master volume, insert, or EQ |
| **Return Tracks** | High | #47, PR #84, #189 | Cannot read/set return effects (reverb, delay sends) |
| **Rack Devices / Chains / DrumPads** | High | #169, #170 | Cannot navigate into Instrument/Effect Racks — only see top-level device |
| **Browser** | High | #66, #183 | Cannot load instruments, effects, or samples programmatically |
| **Automation Envelopes** | High | #112 | Cannot read/write automation curves |
| **Arrangement View clips** | Medium | #124 | Only batch name/length/start_time via track queries — no full clip access |
| **Sidechain routing** | Medium | PR #191 | Cannot configure sidechain sources |
| **Device Variations** (Live 12) | Low | PR #167 | Cannot switch between saved device presets |
| **GroovePool / Groove** | Low | — | Cannot assign or configure groove templates |
| **TuningSystem** (Live 12) | Low | — | Cannot configure microtonality |
| **SimplerDevice / WavetableDevice** | Low | — | No specialized APIs for sampler/synth devices |
| **View scroll/zoom** | Low | PR #153 | Cannot control UI viewport |

## Known Bugs & Stability Issues

| Issue | Severity | Detail | GitHub |
|-------|----------|--------|--------|
| Single-client only | **High** | Second client steals responses from first. No multi-client support. | #73 |
| Listener index drift | **High** | Track listeners break when tracks are created/deleted/reordered. Indices captured in closures go stale. | #31 |
| No request/response correlation | **Medium** | No call IDs. Concurrent queries cannot be reliably matched. | #108 |
| UDP message overflow | **Medium** | Clips with many MIDI notes exceed UDP datagram size limit. | #88 |
| MIDI track meter error | **Low** | `start_listen/output_meter_level` fails on MIDI tracks. | #116 |
| Note 127 deletion bug | **Low** | `/live/clip/remove/notes` without args skips MIDI note 127 (G9). | #190 |

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Tick interval | ~100ms (10 Hz) |
| Client default timeout | 150ms |
| Typical round-trip | 100–200ms |
| Listener delivery | Next tick after state change |
| `export/structure` | ~200ms for full project snapshot |
| Sequential full-project dump | 1–5 seconds (medium project, 10-50 tracks) |

## What .als Parsing Gives You That OSC Cannot

The `.als` file (gzipped XML) contains everything AbletonOSC exposes plus:

- Full arrangement view with all clips positioned on timeline
- Automation envelopes (every breakpoint)
- Device chains and rack hierarchy (nested arbitrarily deep)
- Browser references (which preset/sample each device uses)
- Groove assignments
- Undo history metadata
- Warp markers for audio clips
- Frozen/flattened clip data
- Plugin state (VST/AU chunk data)
- Complete sidechain routing configuration

This is why a **hybrid approach** (`.als` parsing + live OSC) is recommended for a comprehensive agent pipeline.
