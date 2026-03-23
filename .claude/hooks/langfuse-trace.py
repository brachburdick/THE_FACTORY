#!/usr/bin/env python3
"""
Stop hook: Send session trace to Langfuse.
Reads the transcript JSONL and creates a trace with key metrics.

Requires: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST env vars.
Install: pip install langfuse
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def main():
    input_data = json.loads(sys.stdin.read())
    session_id = input_data.get("session_id", "unknown")
    transcript_path = input_data.get("transcript_path", "")
    cwd = input_data.get("cwd", "")

    # Check if Langfuse is configured
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
    host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if not public_key or not secret_key:
        # Langfuse not configured yet — silently skip
        return

    try:
        from langfuse import Langfuse
    except ImportError:
        print("langfuse not installed. Run: pip install langfuse", file=sys.stderr)
        return

    # Parse transcript for metrics
    metrics = parse_transcript(transcript_path)

    # Determine project from cwd
    project = Path(cwd).name

    # Create Langfuse trace
    langfuse = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        host=host,
    )

    trace = langfuse.trace(
        name=f"claude-code-session",
        id=session_id,
        metadata={
            "project": project,
            "cwd": cwd,
            "transcript_path": transcript_path,
        },
        tags=[project],
    )

    # Add session metrics as a generation
    trace.generation(
        name="session-summary",
        metadata=metrics,
        usage_details={
            "input": metrics.get("user_messages", 0),
            "output": metrics.get("assistant_messages", 0),
        },
    )

    # Score the session on key dimensions
    if metrics.get("tool_calls", 0) > 0:
        reads_before_edit = metrics.get("reads_before_first_edit", 0)
        trace.score(
            name="ramp-up-reads",
            value=reads_before_edit,
            comment=f"{reads_before_edit} Read calls before first Edit",
        )

        trace.score(
            name="total-tool-calls",
            value=metrics.get("tool_calls", 0),
        )

        if metrics.get("subagent_count", 0) > 0:
            trace.score(
                name="subagent-count",
                value=metrics.get("subagent_count", 0),
            )

    langfuse.flush()


def parse_transcript(transcript_path: str) -> dict:
    """Extract key metrics from a Claude Code transcript JSONL."""
    metrics = {
        "user_messages": 0,
        "assistant_messages": 0,
        "tool_calls": 0,
        "subagent_count": 0,
        "reads_before_first_edit": 0,
        "tool_frequency": {},
    }

    if not transcript_path or not os.path.exists(transcript_path):
        return metrics

    first_edit_seen = False
    read_count = 0

    try:
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg = entry.get("message", {})
                role = msg.get("role", "")

                if role == "user":
                    metrics["user_messages"] += 1
                elif role == "assistant":
                    metrics["assistant_messages"] += 1

                    # Count tool uses
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "tool_use":
                                tool_name = block.get("name", "unknown")
                                metrics["tool_calls"] += 1
                                metrics["tool_frequency"][tool_name] = (
                                    metrics["tool_frequency"].get(tool_name, 0) + 1
                                )

                                # Track reads before first edit
                                if not first_edit_seen:
                                    if tool_name in ("Read", "Glob", "Grep"):
                                        read_count += 1
                                    elif tool_name in ("Edit", "Write"):
                                        first_edit_seen = True
                                        metrics["reads_before_first_edit"] = read_count

                                if tool_name == "Agent":
                                    metrics["subagent_count"] += 1
    except Exception:
        pass  # Best effort

    if not first_edit_seen:
        metrics["reads_before_first_edit"] = read_count

    return metrics


if __name__ == "__main__":
    main()
