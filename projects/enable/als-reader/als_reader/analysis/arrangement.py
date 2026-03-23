"""Arrangement analysis: structure, clip density, markers, empty tracks."""
from __future__ import annotations

from ..models import ALSProject, Track


def _track_clip_coverage(track: Track) -> dict | None:
    """Analyze how much of the arrangement a track's clips cover."""
    clips = track.midi_clips + track.audio_clips
    if not clips:
        return None

    starts = [c.time for c in clips if c.time is not None]
    ends = [c.end for c in clips if c.end is not None]
    if not starts or not ends:
        return None

    first = min(starts)
    last = max(ends)
    total_clip_beats = sum(
        (c.end - c.time) for c in clips
        if c.time is not None and c.end is not None
    )
    span = last - first
    density = total_clip_beats / span if span > 0 else 0

    return {
        "first_beat": round(first, 2),
        "last_beat": round(last, 2),
        "span_beats": round(span, 2),
        "clip_count": len(clips),
        "total_clip_beats": round(total_clip_beats, 2),
        "density": round(density, 3),
    }


def analyze_arrangement(project: ALSProject) -> dict:
    """Analyze arrangement structure and produce findings.

    Returns a dict with:
    - summary: high-level stats
    - findings: list of observations/issues with severity
    - track_coverage: per-track clip density data
    """
    findings = []
    track_coverage = {}

    # --- Empty tracks ---
    empty_tracks = []
    for t in project.tracks:
        n_clips = len(t.midi_clips) + len(t.audio_clips)
        n_session = sum(1 for s in t.clip_slots if s.clip is not None)
        if n_clips == 0 and n_session == 0 and t.track_type != "group":
            empty_tracks.append(t.name or f"Track {t.index}")

    if empty_tracks:
        findings.append({
            "type": "empty_tracks",
            "severity": "info",
            "message": f"{len(empty_tracks)} tracks have no clips",
            "tracks": empty_tracks,
        })

    # --- Track count assessment ---
    n_tracks = project.track_count
    n_groups = len(project.group_tracks)
    ungrouped = [
        t.name for t in project.tracks
        if t.track_type != "group" and (t.group_id is None or t.group_id < 0)
    ]

    if n_tracks > 40 and n_groups == 0:
        findings.append({
            "type": "no_grouping",
            "severity": "suggestion",
            "message": f"{n_tracks} tracks with no group tracks — consider organizing into groups",
        })
    elif n_tracks > 20 and len(ungrouped) > n_tracks * 0.7:
        findings.append({
            "type": "low_grouping",
            "severity": "info",
            "message": f"{len(ungrouped)} of {n_tracks} tracks are ungrouped",
        })

    # --- Marker/locator analysis ---
    markers = project.locators
    if not markers:
        findings.append({
            "type": "no_markers",
            "severity": "suggestion",
            "message": "No arrangement markers/locators — consider adding section markers (intro, verse, chorus, drop, etc.)",
        })
    elif len(markers) < 3:
        findings.append({
            "type": "few_markers",
            "severity": "info",
            "message": f"Only {len(markers)} markers — more markers help identify sections",
            "markers": [{"name": m.name, "time": m.time} for m in markers],
        })

    # --- Arrangement length & structure ---
    all_clip_ends = []
    for t in project.tracks:
        for c in t.midi_clips + t.audio_clips:
            if c.end is not None:
                all_clip_ends.append(c.end)

    arrangement_length = max(all_clip_ends) if all_clip_ends else 0
    tempo = project.tempo or 120

    if arrangement_length > 0:
        bars = arrangement_length / (project.time_signature.numerator if project.time_signature else 4)
        minutes = arrangement_length / tempo

        # Check for very short or very long arrangements
        if minutes < 0.5 and arrangement_length > 0:
            findings.append({
                "type": "very_short",
                "severity": "info",
                "message": f"Arrangement is only {minutes:.1f} minutes ({bars:.0f} bars) — sketch or loop?",
            })
        elif minutes > 8:
            findings.append({
                "type": "very_long",
                "severity": "info",
                "message": f"Arrangement is {minutes:.1f} minutes ({bars:.0f} bars) — check for trim opportunities",
            })
    else:
        arrangement_length = 0
        bars = 0
        minutes = 0

    # --- Per-track clip density ---
    for t in project.tracks:
        coverage = _track_clip_coverage(t)
        if coverage:
            track_coverage[t.name or f"Track {t.index}"] = coverage

    # --- Clip naming ---
    unnamed_clips = 0
    total_clips = 0
    for t in project.tracks:
        for c in t.midi_clips + t.audio_clips:
            total_clips += 1
            if not c.name or c.name.strip() == "":
                unnamed_clips += 1

    if total_clips > 10 and unnamed_clips > total_clips * 0.5:
        findings.append({
            "type": "unnamed_clips",
            "severity": "info",
            "message": f"{unnamed_clips} of {total_clips} clips are unnamed — naming clips helps navigation",
        })

    # --- Section analysis from markers ---
    sections = []
    if markers and arrangement_length > 0:
        sorted_markers = sorted(markers, key=lambda m: m.time or 0)
        for i, m in enumerate(sorted_markers):
            start = m.time or 0
            end = sorted_markers[i + 1].time if i + 1 < len(sorted_markers) else arrangement_length
            section_bars = (end - start) / (project.time_signature.numerator if project.time_signature else 4)
            sections.append({
                "name": m.name,
                "start_beat": round(start, 2),
                "end_beat": round(end, 2),
                "bars": round(section_bars, 1),
            })

    summary = {
        "track_count": n_tracks,
        "group_count": n_groups,
        "return_count": len(project.return_tracks),
        "total_midi_clips": sum(len(t.midi_clips) for t in project.tracks),
        "total_audio_clips": sum(len(t.audio_clips) for t in project.tracks),
        "arrangement_beats": round(arrangement_length, 2),
        "arrangement_bars": round(bars, 1),
        "arrangement_minutes": round(minutes, 2),
        "marker_count": len(markers),
        "tempo": tempo,
    }
    if sections:
        summary["sections"] = sections

    return {
        "summary": summary,
        "findings": findings,
        "track_coverage": track_coverage,
    }
