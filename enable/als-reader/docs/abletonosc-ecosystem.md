# AbletonOSC — Ecosystem & Integration

> Researched: 2026-03-20

## MCP Servers Built on (or Inspired by) AbletonOSC

| Project | Stars | Uses AbletonOSC? | Transport | Notes |
|---------|-------|-------------------|-----------|-------|
| [ahujasid/ableton-mcp](https://github.com/ahujasid/ableton-mcp) | 2,330 | **No** — custom Remote Script | JSON/TCP (threaded) | Dominant MCP project. Threading proves viable in Live 11/12. |
| [Simon-Kansara/ableton-live-mcp-server](https://github.com/Simon-Kansara/ableton-live-mcp-server) | 369 | **Yes** | python-osc → AbletonOSC | Primary MCP that actually uses AbletonOSC. Futures-based async, 5s timeout. |
| [uisato/ableton-mcp-extended](https://github.com/uisato/ableton-mcp-extended) | 139 | **No** — extends ahujasid | JSON/TCP + UDP hybrid | Adds ElevenLabs voice, low-latency parameter control. |
| [nozomi-koborinai/ableton-osc-mcp](https://github.com/nozomi-koborinai/ableton-osc-mcp) | 7 | **Yes** | Go + AbletonOSC | |
| [ursaayush/ableton-mcp](https://github.com/ursaayush/ableton-mcp) | 0 | **Yes** | AbletonOSC + ClyphX Pro | 143 tools |

**Key finding:** The dominant MCP project bypasses AbletonOSC entirely with its own threaded Remote Script. Only one significant MCP (Simon-Kansara, 369 stars) uses AbletonOSC as transport.

## Related Projects

| Project | Stars | Relationship |
|---------|-------|-------------|
| [pylive](https://github.com/ideoforms/pylive) | 617 | Pythonic OOP wrapper around AbletonOSC (same author). Excludes MIDI note ops. |
| [willrjmarshall/AbletonOSC](https://github.com/willrjmarshall/AbletonOSC) | 34 | Older, unrelated OSC implementation |
| [DrivenByMoss](https://github.com/git-moss/DrivenByMoss) | 738 | Java controller extensions (Bitwig/Ableton). Different paradigm. |
| [codex-live-bridge](https://github.com/sunflower-of-parchman/codex-live-bridge) | 8 | OpenAI Codex-to-Live via M4L device. Routes via JS, not Remote Script. |

## Two Architectural Paradigms

1. **Remote Script** (AbletonOSC, ahujasid): Python runs inside Ableton, exposes LOM directly
2. **Max for Live** (codex-live-bridge): M4L device receives messages, routes to LiveAPI via JS

Remote Scripts have deeper LOM access and don't require M4L/Suite.

## Direct python-osc Integration

A Python agent can talk to AbletonOSC directly with `python-osc` (pure Python, no deps, Python 3.10+):

```python
# Send command
from pythonosc.udp_client import SimpleUDPClient
client = SimpleUDPClient("127.0.0.1", 11000)
client.send_message("/live/song/set/tempo", [128.0])

# Receive responses
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.dispatcher import Dispatcher

dispatcher = Dispatcher()
dispatcher.map("/live/song/get/tempo", lambda addr, *args: print(args))
server = ThreadingOSCUDPServer(("127.0.0.1", 11001), dispatcher)
```

**Production pattern** (from Simon-Kansara's MCP):
- `asyncio.Future` per query for async request/response
- `AsyncIOOSCUDPServer` for response handling
- 5-second timeout
- Fire-and-forget for set commands

## AbletonOSC vs MCP Wrapper

| Factor | Direct AbletonOSC | MCP Wrapper |
|--------|-------------------|-------------|
| Latency | ~100–200ms (1 hop) | ~200–400ms (2 hops) |
| Complexity | Low (UDP) | Higher (MCP protocol layer) |
| Error handling | Manual (no request IDs) | Wrapper can add correlation |
| Tool discoverability | OSC addresses are flat | MCP provides tool schemas |
| Multi-client | Broken (single client) | Wrapper can multiplex |
| State caching | None | Wrapper can cache |

## "Read Full Project State" — Three Approaches

### 1. OSC `export/structure` (fastest live snapshot)
- Single call: `/live/song/export/structure`
- Writes JSON to temp dir with full track/clip/device hierarchy
- Includes all device parameter metadata (name, value, min, max, is_quantized)
- ~200ms

### 2. OSC sequential queries (selective live data)
- `get/num_tracks` → per-track `get/clips/*`, `get/devices/*` → per-device `get/parameters/*`
- 1–5 seconds for medium project
- More control over what you fetch

### 3. Parse .als offline (deepest, read-only)
- `.als` = gzipped XML
- Complete fidelity: arrangement, automation, racks, browser refs, warp markers
- No Ableton running required
- Much richer than OSC can ever provide

### Recommended Hybrid
- Parse `.als` for deep analysis (arrangement, automation, device chains)
- Use `export/structure` for quick live state snapshot
- Use OSC queries + listeners for real-time monitoring and write operations

## Strategic Assessment

**For a production agent pipeline, build a thin Python adapter on `python-osc`** rather than going through MCP. The adapter should add:
- Request correlation IDs (AbletonOSC has none)
- Response caching for stable properties
- Retry logic with backoff
- Multi-query batching via OSC bundles

**Consider forking/extending AbletonOSC** (or building a custom Remote Script) with:
- Threading for lower latency (proven viable by ahujasid)
- Multi-client support
- Coverage for racks/chains, master/return tracks, automation
