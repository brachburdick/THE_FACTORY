"""Arrangement view: text-based horizontal timeline visualization.

Renders an ASCII arrangement view similar to Ableton's arrangement window,
with tracks as rows and clips as blocks along a bar grid.
"""
from __future__ import annotations

from ..models import ALSProject, Track, MidiClip, AudioClip

_BLOCK_L = "["
_BLOCK_R = "]"
_BLOCK_FILL = "="
_EMPTY = " "
_MARKER_CHAR = "V"


def _beats_to_bars(beats: float, numerator: int = 4) -> float:
    return beats / numerator


def _clean_clip_name(clip_name: str, track_name: str) -> str:
    """Strip redundant prefixes from clip names.

    Ableton often names clips after the track or sample with appended suffixes.
    This strips common noise patterns to show cleaner labels.
    """
    name = clip_name
    # Strip leading track-index prefixes like "4-", "12-"
    parts = name.split("-", 1)
    if len(parts) == 2 and parts[0].strip().isdigit():
        name = parts[1].strip()

    # If the clip name starts with the track name, strip it
    if track_name and name.startswith(track_name):
        remainder = name[len(track_name):].lstrip(" _-")
        if remainder:
            name = remainder

    return name


def _clip_label(clip: MidiClip | AudioClip, available_width: int, track_name: str = "") -> str:
    """Produce a clip label that fits in available_width chars."""
    raw_name = clip.name or ""
    name = _clean_clip_name(raw_name, track_name)

    # Add note count for MIDI clips
    if isinstance(clip, MidiClip) and clip.notes:
        suffix = f" ({len(clip.notes)}n)"
    else:
        suffix = ""

    full = name + suffix

    if available_width <= 2:
        return ""
    if len(full) <= available_width:
        return full
    if len(name) <= available_width:
        return name
    if available_width >= 4:
        return name[: available_width - 1] + "~"
    return name[:available_width]


def render_arrangement(
    project: ALSProject,
    chars_per_bar: int = 0,
    max_width: int = 120,
    max_track_name_width: int = 22,
    show_markers: bool = True,
    show_empty_tracks: bool = False,
    show_groups: bool = False,
    bar_numbers_every: int = 8,
) -> str:
    """Render an ASCII arrangement view of the project.

    Args:
        project: Parsed ALSProject.
        chars_per_bar: Character width per bar. If 0 (default), auto-calculated
            from max_width to fit the whole arrangement.
        max_width: Target max line width (default 120). Used to auto-calculate
            chars_per_bar when it's 0.
        max_track_name_width: Max chars for track name column.
        show_markers: Show marker positions above the timeline.
        show_empty_tracks: Include tracks with no clips.
        show_groups: Show group track rows.
        bar_numbers_every: Show bar numbers at this interval.

    Returns:
        Multi-line string of the arrangement view.
    """
    numerator = project.time_signature.numerator if project.time_signature else 4

    # Find arrangement bounds
    all_ends = []
    for t in project.tracks:
        for c in t.midi_clips + t.audio_clips:
            if c.end is not None:
                all_ends.append(c.end)
    if not all_ends:
        return "(empty arrangement)"

    total_beats = max(all_ends)
    total_bars = int(_beats_to_bars(total_beats, numerator)) + 1

    # Filter tracks
    tracks_to_show = []
    for t in project.tracks:
        has_clips = bool(t.midi_clips or t.audio_clips)
        if t.track_type == "group":
            if show_groups:
                tracks_to_show.append(t)
        elif has_clips or show_empty_tracks:
            tracks_to_show.append(t)

    if not tracks_to_show:
        return "(no tracks with clips)"

    # Compute track name width
    name_width = min(
        max_track_name_width,
        max(len(t.name or "") for t in tracks_to_show) + 3,
    )
    name_width = max(name_width, 10)

    # Auto-calculate chars_per_bar to fit in max_width
    if chars_per_bar <= 0:
        available = max_width - name_width - 1  # -1 for separator
        chars_per_bar = max(1, available // total_bars)
        # Cap at a reasonable max
        chars_per_bar = min(chars_per_bar, 8)

    timeline_width = total_bars * chars_per_bar

    lines = []

    # --- Header: bar numbers ---
    bar_line = " " * name_width
    cursor = 0
    while cursor < total_bars:
        if cursor % bar_numbers_every == 0:
            label = str(cursor + 1)
            remaining = min(bar_numbers_every, total_bars - cursor)
            segment_width = remaining * chars_per_bar
            segment = label + "." * max(0, segment_width - len(label))
            bar_line += segment
            cursor += remaining
        else:
            bar_line += "." * chars_per_bar
            cursor += 1
    lines.append(bar_line[:name_width + timeline_width])

    # --- Markers row ---
    if show_markers and project.locators:
        marker_line = list(" " * (name_width + timeline_width))
        marker_labels = []
        for loc in sorted(project.locators, key=lambda l: l.time or 0):
            if loc.time is None:
                continue
            bar_pos = _beats_to_bars(loc.time, numerator)
            char_pos = name_width + int(bar_pos * chars_per_bar)
            if 0 <= char_pos < len(marker_line):
                marker_line[char_pos] = _MARKER_CHAR
                marker_labels.append((char_pos, loc.name or ""))

        lines.append("".join(marker_line).rstrip())

        if marker_labels:
            label_line = list(" " * (name_width + timeline_width))
            for pos, name in marker_labels:
                for i, ch in enumerate(name):
                    if pos + i < len(label_line):
                        label_line[pos + i] = ch
            lines.append("".join(label_line).rstrip())

    # --- Separator ---
    lines.append("-" * name_width + "+" + "-" * timeline_width)

    # --- Track rows ---
    for track in tracks_to_show:
        type_char = {
            "midi": "M", "audio": "A", "group": "G", "return": "R", "master": "X",
        }.get(track.track_type, "?")

        tname = track.name or f"Track {track.index}"
        if len(tname) > name_width - 3:
            tname = tname[: name_width - 4] + "~"

        # Mix state indicators
        state = ""
        if track.mixer:
            if track.mixer.solo:
                state = "S"
            elif track.mixer.speaker is False:
                state = "m"

        label = f"{type_char}{state} {tname}".ljust(name_width)

        # Build timeline
        timeline = list(_EMPTY * timeline_width)

        # Draw grid lines
        for bar in range(total_bars):
            pos = bar * chars_per_bar
            if pos < timeline_width and timeline[pos] == _EMPTY:
                timeline[pos] = ":"

        # Draw clips
        clips = sorted(
            track.midi_clips + track.audio_clips,
            key=lambda c: c.time or 0,
        )

        for clip in clips:
            if clip.time is None or clip.end is None:
                continue
            start_bar = _beats_to_bars(clip.time, numerator)
            end_bar = _beats_to_bars(clip.end, numerator)

            start_pos = int(start_bar * chars_per_bar)
            end_pos = int(end_bar * chars_per_bar)

            start_pos = max(0, min(start_pos, timeline_width - 1))
            end_pos = max(start_pos + 1, min(end_pos, timeline_width))

            width = end_pos - start_pos
            if width < 1:
                continue

            inner_width = width - 2
            if width == 1:
                block = _BLOCK_L
            elif width == 2:
                block = _BLOCK_L + _BLOCK_R
            else:
                clip_text = _clip_label(clip, inner_width, track.name or "")
                if len(clip_text) < inner_width:
                    fill = _BLOCK_FILL * (inner_width - len(clip_text))
                    block = _BLOCK_L + clip_text + fill + _BLOCK_R
                else:
                    block = _BLOCK_L + clip_text + _BLOCK_R

            for i, ch in enumerate(block):
                if start_pos + i < timeline_width:
                    timeline[start_pos + i] = ch

        line = label + "|" + "".join(timeline)
        lines.append(line.rstrip())

    # --- Footer ---
    footer_parts = []
    if project.tempo:
        footer_parts.append(f"{project.tempo:.0f} BPM")
    if project.time_signature:
        footer_parts.append(f"{project.time_signature.numerator}/{project.time_signature.denominator}")
    if project.scale and project.scale.name:
        _NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        root = _NOTES[project.scale.root_note] if project.scale.root_note is not None else "?"
        footer_parts.append(f"{root} {project.scale.name}")

    total_minutes = total_beats / (project.tempo or 120)
    footer_parts.append(f"{total_bars} bars")
    footer_parts.append(f"{total_minutes:.1f} min")

    lines.append("-" * name_width + "+" + "-" * timeline_width)
    lines.append(" | ".join(footer_parts))

    return "\n".join(lines)
