# ableton-mcp: Research Overview

> **Repo:** https://github.com/jpoindexter/ableton-mcp
> **Version:** 2.0.0 | **License:** MIT | **Python:** ≥3.10
> **Stars:** 7 | **Forks:** 2 | **Contributors:** 4 | **Last commit:** 2026-02-09
> **Researched:** 2026-03-20

## What It Is

An MCP server + Ableton Remote Script that exposes **128 MCP tools** (200+ commands at the
Remote Script level) for controlling Ableton Live via AI. Ships three integration paths:
MCP (Claude), REST API (any LLM), and a Max4Live device (in-DAW chat).

## Architecture

```
Claude / MCP Client
    │  stdio (MCP protocol, JSON-RPC)
    ▼
MCP Server (FastMCP, ~2828 lines Python)
    │  TCP socket (localhost:9877, JSON commands)
    ▼
Ableton Remote Script (Control Surface inside Live)
    │  Ableton Live Python API (LOM)
    ▼
Ableton Live Session
```

**Not AbletonOSC.** Custom Remote Script with its own TCP JSON protocol on port 9877.

**Thread safety:** Read commands run on client handler thread. Write commands scheduled to
Ableton's main thread via `schedule_message()`.

**Auto-reconnect:** `AbletonConnection` class manages persistent TCP socket, buffered
responses (up to 1MB), configurable timeouts (15s default).

### Alternative Paths

| Path | Transport | Use Case |
|------|-----------|----------|
| MCP Server | stdio → TCP:9877 | Claude Desktop, Claude Code, Cursor |
| REST API | HTTP:8000 → TCP:9877 | Ollama, OpenAI, any LLM with function calling |
| Max4Live Device | Node for Max → LLM HTTP APIs | Self-contained "chat with DAW" inside Ableton |

The M4L device is standalone — talks directly to LLM providers, doesn't need the MCP server.
The REST API is optional (`pip install ableton-mcp[rest]`), adds auth, rate limiting, CORS.

## MCP Protocol Compliance

| Aspect | Status |
|--------|--------|
| Tool definitions | `@mcp.tool()` via FastMCP, well-typed, docstring descriptions |
| Input schemas | Python type hints (int, float, bool, str, List[Dict]) |
| Error handling | Structured error messages, auto-reconnect on connection loss |
| Resources | Not implemented |
| Prompts | Not implemented |
| Transport | stdio only (no SSE/WebSocket) |

Tools-only MCP server. No resource URIs, no prompt templates.

## Maturity Assessment

| Signal | Value |
|--------|-------|
| Age | ~7 weeks (created 2026-01-27) |
| Last commit | 2026-02-09 (5 weeks dormant) |
| Commit pattern | 2-day sprint (Jan 27-28), docs polish (Feb 9) |
| Contributors | jpoindexter (28), ahujasid (17), calclavia (3), Ronbalt (3) |
| Issues | 0 open, 0 closed |
| Releases | None |
| Tests | Unit + integration present, depth unclear |
| CI/CD | Dockerfile, no GitHub Actions |

**Verdict: Experimental.** Impressive scope built in a 2-day sprint (likely AI-assisted).
Zero community interaction, no releases, dormant. Worth studying and forking, not depending on.

## Security

- Remote Script (port 9877): **no auth**, raw TCP, no TLS
- REST API (port 8000): optional API key (off by default), rate limiting, CORS localhost-only
- Both localhost-only — exposed via tunnel = full DAW control open
- No input sanitization audit visible

## Setup (Minimum)

1. Copy `AbletonMCP_Remote_Script/__init__.py` → `~/Music/Ableton/User Library/Remote Scripts/AbletonMCP/`
2. Ableton: Preferences → Control Surface → AbletonMCP (I/O: None)
3. Claude config:
   ```json
   {"mcpServers": {"ableton-mcp": {"command": "uvx", "args": ["ableton-mcp"]}}}
   ```

Works with Claude Code out of the box (stdio transport, `uvx` launcher).
