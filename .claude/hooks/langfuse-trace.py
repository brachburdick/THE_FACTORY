#!/usr/bin/env python3
"""
Stop hook: Send session trace to Langfuse.
Reads the transcript JSONL and creates a trace with key metrics.

Requires: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY env vars.
Accepts: LANGFUSE_HOST or LANGFUSE_BASE_URL for the endpoint.
Install: pip install langfuse (v4+)

If env vars aren't in the process environment (common when Claude Code
is launched from a GUI), falls back to sourcing them from the user's
interactive shell.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def _load_env_from_shell() -> None:
    """Load LANGFUSE_ env vars from user's interactive shell if not present.

    Claude Code hooks run in a non-interactive shell that doesn't source
    ~/.zshrc, so env vars set there aren't inherited.
    """
    if os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY"):
        return  # Already set

    try:
        shell = os.environ.get("SHELL", "/bin/zsh")
        result = subprocess.run(
            [shell, "-i", "-c", "env"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("LANGFUSE_"):
                    key, _, val = line.partition("=")
                    if key and val and key not in os.environ:
                        os.environ[key] = val
    except Exception:
        pass


def main():
    input_data = json.loads(sys.stdin.read())
    session_id = input_data.get("session_id", "unknown")
    transcript_path = input_data.get("transcript_path", "")
    cwd = input_data.get("cwd", "")

    # Load env vars from login shell if not inherited
    _load_env_from_shell()

    # Check if Langfuse is configured (accept both HOST and BASE_URL)
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
    host = (
        os.environ.get("LANGFUSE_HOST")
        or os.environ.get("LANGFUSE_BASE_URL")
        or "https://cloud.langfuse.com"
    )

    if not public_key or not secret_key:
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

    # Create Langfuse client (v4 API)
    langfuse = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        host=host,
    )

    # Create trace via v4 observation API
    # Use session_id as a seed for deterministic trace ID
    trace_id = langfuse.create_trace_id(seed=session_id)

    with langfuse.start_as_current_observation(
        name="claude-code-session",
        as_type="span",
        metadata={
            "project": project,
            "cwd": cwd,
            "session_id": session_id,
            "transcript_path": transcript_path,
            "tool_frequency": metrics.get("tool_frequency", {}),
        },
        input=f"Session in {project}",
        output=json.dumps({
            "user_messages": metrics.get("user_messages", 0),
            "assistant_messages": metrics.get("assistant_messages", 0),
            "tool_calls": metrics.get("tool_calls", 0),
            "subagent_count": metrics.get("subagent_count", 0),
            "reads_before_first_edit": metrics.get("reads_before_first_edit", 0),
        }),
    ):
        # Score the session on key dimensions
        if metrics.get("tool_calls", 0) > 0:
            reads_before_edit = metrics.get("reads_before_first_edit", 0)
            langfuse.score_current_trace(
                name="ramp-up-reads",
                value=float(reads_before_edit),
                comment=f"{reads_before_edit} Read calls before first Edit",
            )

            langfuse.score_current_trace(
                name="total-tool-calls",
                value=float(metrics.get("tool_calls", 0)),
            )

            if metrics.get("subagent_count", 0) > 0:
                langfuse.score_current_trace(
                    name="subagent-count",
                    value=float(metrics.get("subagent_count", 0)),
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

                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "tool_use":
                                tool_name = block.get("name", "unknown")
                                metrics["tool_calls"] += 1
                                metrics["tool_frequency"][tool_name] = (
                                    metrics["tool_frequency"].get(tool_name, 0) + 1
                                )

                                if not first_edit_seen:
                                    if tool_name in ("Read", "Glob", "Grep"):
                                        read_count += 1
                                    elif tool_name in ("Edit", "Write"):
                                        first_edit_seen = True
                                        metrics["reads_before_first_edit"] = read_count

                                if tool_name == "Agent":
                                    metrics["subagent_count"] += 1
    except Exception:
        pass

    if not first_edit_seen:
        metrics["reads_before_first_edit"] = read_count

    return metrics


if __name__ == "__main__":
    main()
