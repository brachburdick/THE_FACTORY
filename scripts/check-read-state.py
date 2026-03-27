#!/usr/bin/env python3
"""Check read-state.jsonl against current file hashes.

Reports which previously-read files are still fresh (unchanged) vs stale.
Agents use this at session start to skip re-reading unchanged files.

Usage:
    python scripts/check-read-state.py              # Human-readable
    python scripts/check-read-state.py --json       # Machine-readable
    python scripts/check-read-state.py --stale-only # Only show stale files
"""

import hashlib
import json
import sys
from pathlib import Path

AGENT_DIR = Path(__file__).parent.parent / ".agent"
PROJECT_ROOT = Path(__file__).parent.parent
READ_STATE = AGENT_DIR / "read-state.jsonl"


def load_read_state() -> dict[str, dict]:
    """Load read state, keeping latest entry per path."""
    if not READ_STATE.exists():
        return {}
    latest: dict[str, dict] = {}
    for line in READ_STATE.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        entry = json.loads(line)
        path = entry.get("path", "")
        if path:
            latest[path] = entry
    return latest


def check_freshness(entries: dict[str, dict]) -> tuple[list[dict], list[dict]]:
    """Return (fresh, stale) file lists."""
    fresh, stale = [], []
    for path, entry in entries.items():
        full_path = PROJECT_ROOT / path
        if not full_path.exists():
            stale.append({**entry, "reason": "deleted"})
            continue

        try:
            content = full_path.read_text()
        except (OSError, UnicodeDecodeError):
            stale.append({**entry, "reason": "unreadable"})
            continue

        current_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
        if current_hash == entry.get("hash"):
            fresh.append(entry)
        else:
            stale.append({**entry, "reason": "modified", "new_hash": current_hash})

    return fresh, stale


def main():
    args = set(sys.argv[1:])
    as_json = "--json" in args
    stale_only = "--stale-only" in args

    entries = load_read_state()
    if not entries:
        if as_json:
            print(json.dumps({"fresh": [], "stale": [], "message": "No read state found"}))
        else:
            print("No read state found. This is the first session or read-state.jsonl is empty.")
        sys.exit(0)

    fresh, stale = check_freshness(entries)

    if as_json:
        output = {"stale": stale} if stale_only else {"fresh": fresh, "stale": stale}
        print(json.dumps(output, indent=2))
    else:
        if not stale_only:
            print(f"Fresh ({len(fresh)} files — skip re-reading):")
            for f in fresh:
                print(f"  {f['path']}")
        print(f"\nStale ({len(stale)} files — re-read these):")
        for s in stale:
            print(f"  {s['path']} ({s.get('reason', 'unknown')})")

    sys.exit(0)


if __name__ == "__main__":
    main()
