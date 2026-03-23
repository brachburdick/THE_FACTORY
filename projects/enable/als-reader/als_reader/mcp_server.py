"""MCP server for als_reader — lets AI agents read Ableton Live Sets."""
from __future__ import annotations

import json
from pathlib import Path

from fastmcp import FastMCP

from . import load
from .analysis.summary import summarize

mcp = FastMCP(
    "als-reader",
    instructions=(
        "Read and analyze Ableton Live Set (.als) files. "
        "Use `parse_live_set` for a full project dump, or `summarize_live_set` "
        "for a compact overview that fits easily in context."
    ),
)


@mcp.tool()
def parse_live_set(file_path: str) -> str:
    """Parse an Ableton Live Set (.als) file and return the full project data as JSON.

    Returns complete data across all tiers: tracks, clips, MIDI notes, mixer state,
    devices, automation, and more. Can be large for complex projects (1-4MB).
    Use `summarize_live_set` first for an overview.

    Args:
        file_path: Absolute path to the .als file.
    """
    project = load(file_path)
    return project.to_json()


@mcp.tool()
def summarize_live_set(file_path: str) -> str:
    """Get a compact summary of an Ableton Live Set (.als) file.

    Returns an overview with track listing (names, types, clip counts, devices),
    tempo, time signature, markers, scenes, and mix snapshot. Much smaller than
    the full parse — use this for initial assessment before drilling into specifics.

    Args:
        file_path: Absolute path to the .als file.
    """
    project = load(file_path)
    return json.dumps(summarize(project), indent=2)


@mcp.tool()
def get_track_details(file_path: str, track_name: str) -> str:
    """Get full details for a specific track by name.

    Returns the complete track data including all clips, MIDI notes, devices
    with parameters, mixer state, routing, and automation envelopes.

    Args:
        file_path: Absolute path to the .als file.
        track_name: Name of the track to retrieve (case-insensitive).
    """
    project = load(file_path)
    for track in project.all_tracks:
        if track.name and track.name.lower() == track_name.lower():
            from dataclasses import asdict
            from .models import _clean_dict
            return json.dumps(_clean_dict(asdict(track)), indent=2)

    available = [t.name for t in project.all_tracks if t.name]
    return json.dumps({"error": f"Track '{track_name}' not found", "available_tracks": available})


@mcp.tool()
def get_midi_notes(file_path: str, track_name: str, clip_index: int = 0) -> str:
    """Get MIDI notes from a specific clip on a track.

    Returns all notes with pitch, time, duration, velocity, and probability.
    Useful for analyzing melodies, chord progressions, and rhythmic patterns.

    Args:
        file_path: Absolute path to the .als file.
        track_name: Name of the track (case-insensitive).
        clip_index: Index of the arrangement clip (default: 0 = first clip).
    """
    project = load(file_path)
    for track in project.tracks:
        if track.name and track.name.lower() == track_name.lower():
            if not track.midi_clips:
                return json.dumps({"error": f"Track '{track_name}' has no MIDI clips"})
            if clip_index >= len(track.midi_clips):
                return json.dumps({
                    "error": f"Clip index {clip_index} out of range",
                    "clip_count": len(track.midi_clips),
                    "clip_names": [c.name for c in track.midi_clips],
                })
            clip = track.midi_clips[clip_index]
            from dataclasses import asdict
            from .models import _clean_dict
            return json.dumps(_clean_dict(asdict(clip)), indent=2)

    available = [t.name for t in project.tracks if t.name and t.midi_clips]
    return json.dumps({"error": f"Track '{track_name}' not found", "tracks_with_midi": available})


@mcp.tool()
def analyze_live_set(
    file_path: str,
    include_track_details: bool = False,
) -> str:
    """Analyze an Ableton Live Set and generate structured feedback.

    Runs four analyzers (arrangement, mix, MIDI, devices) and returns a unified
    report with findings sorted by severity (warnings, suggestions, info).

    This is the primary tool for giving production feedback on a project.
    Call this after `summarize_live_set` to get actionable insights.

    Args:
        file_path: Absolute path to the .als file.
        include_track_details: If True, include per-track detail data for deep
            dives. Makes the response much larger. Default: False.
    """
    from .analysis.report import generate_feedback_report, feedback_to_json
    project = load(file_path)
    report = generate_feedback_report(project, include_track_details=include_track_details)
    return feedback_to_json(report)


@mcp.tool()
def view_arrangement(
    file_path: str,
    max_width: int = 120,
) -> str:
    """Render an ASCII arrangement view of an Ableton Live Set.

    Shows a horizontal timeline with tracks as rows and clips as blocks,
    similar to Ableton's arrangement view. Includes bar numbers, markers,
    track types (M=MIDI, A=audio, G=group), and mix state (S=solo, m=muted).

    Best tool for understanding the spatial layout and structure of a project.

    Args:
        file_path: Absolute path to the .als file.
        max_width: Target line width in characters (default: 120).
    """
    from .analysis.arrangement_view import render_arrangement
    project = load(file_path)
    return render_arrangement(project, max_width=max_width)


# ---------------------------------------------------------------------------
# Write tools
# ---------------------------------------------------------------------------

@mcp.tool()
def rename_track(file_path: str, old_name: str, new_name: str, output_path: str = "") -> str:
    """Rename a track in an Ableton Live Set.

    Args:
        file_path: Absolute path to the .als file.
        old_name: Current track name (case-insensitive).
        new_name: New name for the track.
        output_path: Where to save. Empty string = overwrite original (with .bak backup).
    """
    from .writer import ALSWriter
    writer = ALSWriter(file_path)
    ok = writer.rename_track(old_name, new_name)
    if not ok:
        names = writer._list_track_names()
        return json.dumps({"error": f"Track '{old_name}' not found", "available_tracks": names})
    out = writer.save(output_path or None)
    return json.dumps({"success": True, "changes": writer.changes, "saved_to": str(out)})


@mcp.tool()
def set_track_volume(file_path: str, track_name: str, volume: float, output_path: str = "") -> str:
    """Set a track's volume level.

    Ableton uses linear scale: 0.0 = -inf dB, 1.0 ≈ 0 dB, ~1.99 ≈ +6 dB.

    Args:
        file_path: Absolute path to the .als file.
        track_name: Track name (case-insensitive).
        volume: New volume (linear, 0.0 to ~1.99).
        output_path: Where to save. Empty = overwrite original (with .bak backup).
    """
    from .writer import ALSWriter
    writer = ALSWriter(file_path)
    ok = writer.set_track_volume(track_name, volume)
    if not ok:
        return json.dumps({"error": f"Could not set volume on '{track_name}'"})
    out = writer.save(output_path or None)
    return json.dumps({"success": True, "changes": writer.changes, "saved_to": str(out)})


@mcp.tool()
def set_track_pan(file_path: str, track_name: str, pan: float, output_path: str = "") -> str:
    """Set a track's pan position.

    Args:
        file_path: Absolute path to the .als file.
        track_name: Track name (case-insensitive).
        pan: Pan position (-1.0 = full left, 0.0 = center, 1.0 = full right).
        output_path: Where to save. Empty = overwrite original (with .bak backup).
    """
    from .writer import ALSWriter
    writer = ALSWriter(file_path)
    ok = writer.set_track_pan(track_name, pan)
    if not ok:
        return json.dumps({"error": f"Could not set pan on '{track_name}'"})
    out = writer.save(output_path or None)
    return json.dumps({"success": True, "changes": writer.changes, "saved_to": str(out)})


@mcp.tool()
def set_midi_velocities(
    file_path: str,
    track_name: str,
    velocity: float | None = None,
    scale: float | None = None,
    clip_index: int | None = None,
    output_path: str = "",
) -> str:
    """Modify MIDI note velocities on a track.

    Provide exactly one of `velocity` or `scale`:
    - velocity: Set all notes to this fixed value (1-127).
    - scale: Multiply existing velocities (e.g., 0.8 = 20% softer, 1.2 = 20% louder).

    Args:
        file_path: Absolute path to the .als file.
        track_name: Track name (case-insensitive).
        velocity: Fixed velocity value (1-127).
        scale: Velocity multiplier.
        clip_index: Only modify this clip (0-indexed). None = all clips.
        output_path: Where to save. Empty = overwrite original (with .bak backup).
    """
    from .writer import ALSWriter
    writer = ALSWriter(file_path)
    try:
        n = writer.set_midi_velocities(track_name, velocity=velocity, scale=scale, clip_index=clip_index)
    except ValueError as e:
        return json.dumps({"error": str(e)})
    if n == 0:
        return json.dumps({"error": f"No MIDI notes found on '{track_name}'"})
    out = writer.save(output_path or None)
    return json.dumps({"success": True, "notes_modified": n, "changes": writer.changes, "saved_to": str(out)})


@mcp.tool()
def humanize_velocities(
    file_path: str,
    track_name: str,
    amount: float = 15,
    clip_index: int | None = None,
    output_path: str = "",
) -> str:
    """Add velocity variation to MIDI notes for a more human feel.

    Uses deterministic variation (reproducible, not random). Great for fixing
    flat velocity patterns flagged by the analyzer.

    Args:
        file_path: Absolute path to the .als file.
        track_name: Track name (case-insensitive).
        amount: Max velocity deviation in each direction (default: 15).
        clip_index: Only modify this clip (0-indexed). None = all clips.
        output_path: Where to save. Empty = overwrite original (with .bak backup).
    """
    from .writer import ALSWriter
    writer = ALSWriter(file_path)
    n = writer.humanize_velocities(track_name, amount=amount, clip_index=clip_index)
    if n == 0:
        return json.dumps({"error": f"No MIDI notes found on '{track_name}'"})
    out = writer.save(output_path or None)
    return json.dumps({"success": True, "notes_modified": n, "changes": writer.changes, "saved_to": str(out)})


@mcp.tool()
def set_tempo(file_path: str, bpm: float, output_path: str = "") -> str:
    """Set the project tempo.

    Args:
        file_path: Absolute path to the .als file.
        bpm: New tempo in beats per minute.
        output_path: Where to save. Empty = overwrite original (with .bak backup).
    """
    from .writer import ALSWriter
    writer = ALSWriter(file_path)
    ok = writer.set_tempo(bpm)
    if not ok:
        return json.dumps({"error": "Could not find tempo element"})
    out = writer.save(output_path or None)
    return json.dumps({"success": True, "changes": writer.changes, "saved_to": str(out)})


if __name__ == "__main__":
    mcp.run()
