# Mobile Operator Access — Spec

**Status:** Draft
**Date:** 2026-03-27
**Goal:** Let Brach interact with THE_FACTORY and CRUCIBLE from his phone via messaging, without opening a laptop.

---

## Problem

Everything requires a terminal. Checking task status, kicking off a run, reviewing results, answering agent questions — all laptop-bound. The phone sits idle.

## Use Cases

| # | From phone, I want to… | Priority |
|---|---|---|
| 1 | Check task queue status (`ready.py` equivalent) | Must |
| 2 | Answer agent questions from `.agent/questions.jsonl` | Must |
| 3 | Kick off a CRUCIBLE eval run with a variant | Should |
| 4 | Get notified when a run finishes (pass/fail + summary) | Must |
| 5 | Read the last run record | Should |
| 6 | Approve/reject a gated plan | Should |
| 7 | Check eval suite health (last CI result) | Nice |
| 8 | Quick natural-language command ("run the BPM fix task against baseline") | Nice |

## Architecture Options

### Option A: Telegram Bot (Recommended)

**Why Telegram:** Free bot API, rich formatting (markdown, inline keyboards), file sharing, no monthly fees, works on every phone, bot creation takes 30 seconds via BotFather. iMessage requires Apple Business, SMS requires Twilio + per-message cost, Discord/Slack are heavier than needed for one person.

```
Phone (Telegram)
    ↕ HTTPS (polling or webhook)
Lightweight bridge server (Node or Python)
    ↕ local filesystem / subprocess
THE_FACTORY repo + CRUCIBLE
```

**Bridge server** runs on your Mac (or any always-on machine). It:
- Polls Telegram for messages (long-polling, no public IP needed)
- Maps commands to local actions
- Sends results back as Telegram messages

**Commands:**

```
/status          → runs ready.py, returns next tasks + blocked count
/questions       → shows pending questions from questions.jsonl
/answer q-001 B  → writes answer to questions.jsonl
/run <variant>   → triggers CRUCIBLE run, streams progress
/lastrun         → last entry from runs.jsonl, formatted
/approve <plan>  → marks plan as approved
/ci              → fetches latest GitHub Actions run status via gh CLI
/ask <anything>  → free-form, routed to Claude API for interpretation
```

Inline keyboards for common actions (approve/reject buttons, question answer options).

**Notifications (push):**
- Run complete → summary + pass/fail
- New agent question → question text + answer buttons
- CI failure → which eval failed
- Gated plan waiting → plan summary + approve/reject buttons

### Option B: iMessage via Shortcuts + SSH

Use Apple Shortcuts to SSH into the Mac and run scripts, returning output as a message. Simpler but limited:
- No push notifications (you'd have to poll)
- No inline buttons
- Fragile (Shortcuts SSH is flaky)
- Good as a quick hack, bad as a real system

### Option C: GitHub Mobile + Actions

Trigger workflows via GitHub Mobile app, use issue comments for Q&A. Free, no server needed, but:
- Slow (Actions spin-up time)
- No real-time notifications
- Clunky UX for quick status checks
- Could supplement Option A for CI-related tasks

## Recommended: Option A (Telegram Bot)

### Components

```
specs/mobile-operator-spec.md    ← this file
scripts/mobile-bridge/
├── bridge.py                    ← Telegram bot + command router
├── commands/
│   ├── status.py                ← ready.py wrapper
│   ├── questions.py             ← questions.jsonl read/write
│   ├── run.py                   ← CRUCIBLE run trigger
│   ├── lastrun.py               ← runs.jsonl reader
│   ├── approve.py               ← plan approval
│   └── ci.py                    ← gh CLI wrapper
├── notifier.py                  ← watches for events, pushes to Telegram
├── config.yaml                  ← bot token (gitignored), chat ID, paths
└── requirements.txt             ← python-telegram-bot, watchdog
```

### Notification Engine

`notifier.py` uses filesystem watches (watchdog) on:
- `.agent/runs.jsonl` → new run record appended → push summary
- `.agent/questions.jsonl` → new question with status=pending → push with answer buttons
- `.claude/plans/` → new plan file → push with approve/reject

Plus a periodic check (every 5 min) on GitHub Actions via `gh run list`.

### Security

- **Single-user:** Bot only responds to your Telegram chat ID. All other messages ignored.
- **Bot token:** Stored in `config.yaml`, gitignored. Loaded from env var `TF_TELEGRAM_TOKEN` as fallback.
- **No secrets in messages:** Run results are summarized, not raw-dumped. File contents are never sent unprompted.
- **Rate limiting:** Max 1 CRUCIBLE run at a time. Debounce notifications (no spam on rapid file changes).

### Running It

```bash
# One-time setup
pip install python-telegram-bot watchdog pyyaml
# Create bot via @BotFather on Telegram, get token
# Add token + your chat ID to config.yaml

# Run (background, survives terminal close)
nohup python scripts/mobile-bridge/bridge.py &

# Or as a launchd service (recommended for always-on)
# template at scripts/mobile-bridge/com.thefactory.bridge.plist
```

### CRUCIBLE Integration

The bridge triggers CRUCIBLE runs via its CLI/API:
```
POST http://localhost:3100/api/runs
{ "variant": "baseline", "task": "fix-short-track-bpm" }
```

The bridge subscribes to CRUCIBLE's WebSocket (`ws://localhost:3100/ws`) for real-time progress, forwarding key events (started, phase change, pass/fail) to Telegram.

### What This Doesn't Do

- **Not a full Claude Code session.** You can't have a back-and-forth coding conversation from Telegram. The `/ask` command gives you one-shot Claude API calls for quick questions.
- **Not a CI replacement.** GitHub Actions still runs evals on push. This just gives you visibility from your phone.
- **No file editing.** You can read status and trigger actions, not write code. That's intentional — phone coding is a trap.

## Implementation Plan

| Phase | What | Effort |
|---|---|---|
| 1 | Bot skeleton + `/status` + `/questions` + `/answer` | ~2 hours |
| 2 | Notification engine (watchdog on runs.jsonl, questions.jsonl) | ~2 hours |
| 3 | CRUCIBLE integration (`/run`, WebSocket forwarding) | ~3 hours |
| 4 | Plan approval + CI status + `/ask` via Claude API | ~2 hours |
| 5 | launchd service + polish | ~1 hour |

## Open Questions

1. **Always-on machine?** The bridge needs to run somewhere. Your Mac works if it doesn't sleep. Alternatively: a cheap VPS or Raspberry Pi. Or run it only when you're away (launchd can start it on screen lock).
2. **Multiple projects?** Currently scoped to THE_FACTORY + CRUCIBLE. If you want DjTools/SCUE or Tinyshop commands, the command router is extensible.
3. **Voice notes?** Telegram supports voice messages. Could pipe through Whisper API → text → `/ask`. Overkill for v1 but cool.
