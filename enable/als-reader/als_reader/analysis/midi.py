"""MIDI analysis: velocity distribution, note density, pitch patterns."""
from __future__ import annotations

from collections import Counter
from ..models import ALSProject, MidiClip, MidiNote

_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def _note_name(pitch: int) -> str:
    return f"{_NOTE_NAMES[pitch % 12]}{pitch // 12 - 1}"


def _analyze_clip_notes(notes: list[MidiNote]) -> dict | None:
    """Analyze a list of MIDI notes."""
    if not notes:
        return None

    velocities = [n.velocity for n in notes if n.velocity is not None]
    pitches = [n.pitch for n in notes if n.pitch is not None]
    durations = [n.duration for n in notes if n.duration is not None]
    times = [n.time for n in notes if n.time is not None]

    result = {"note_count": len(notes)}

    if velocities:
        vel_min = min(velocities)
        vel_max = max(velocities)
        vel_avg = sum(velocities) / len(velocities)
        vel_range = vel_max - vel_min

        result["velocity"] = {
            "min": round(vel_min, 1),
            "max": round(vel_max, 1),
            "avg": round(vel_avg, 1),
            "range": round(vel_range, 1),
        }

    if pitches:
        pitch_counter = Counter(pitches)
        most_common_pitch = pitch_counter.most_common(1)[0][0]
        unique_pitches = sorted(set(pitches))
        pitch_range = max(pitches) - min(pitches)

        # Key/scale detection: count note classes
        note_classes = Counter(p % 12 for p in pitches)

        result["pitch"] = {
            "lowest": _note_name(min(pitches)),
            "highest": _note_name(max(pitches)),
            "range_semitones": pitch_range,
            "unique_pitches": len(unique_pitches),
            "most_common": _note_name(most_common_pitch),
            "note_class_distribution": {
                _NOTE_NAMES[nc]: count
                for nc, count in note_classes.most_common()
            },
        }

    if durations:
        result["duration"] = {
            "min": round(min(durations), 4),
            "max": round(max(durations), 4),
            "avg": round(sum(durations) / len(durations), 4),
        }

    if times and len(times) > 1:
        sorted_times = sorted(times)
        gaps = [sorted_times[i + 1] - sorted_times[i] for i in range(len(sorted_times) - 1)]
        gaps = [g for g in gaps if g > 0]  # filter simultaneous notes (chords)
        if gaps:
            result["timing"] = {
                "span_beats": round(sorted_times[-1] - sorted_times[0], 4),
                "avg_gap": round(sum(gaps) / len(gaps), 4),
                "min_gap": round(min(gaps), 4),
            }

    # Probability usage
    probabilities = [n.probability for n in notes if n.probability is not None]
    non_full_prob = [p for p in probabilities if p < 1.0]
    if non_full_prob:
        result["probability"] = {
            "notes_with_probability": len(non_full_prob),
            "min_probability": round(min(non_full_prob), 2),
        }

    return result


def analyze_midi(project: ALSProject) -> dict:
    """Analyze MIDI content across the project.

    Returns:
    - summary: project-wide MIDI stats
    - findings: observations and issues
    - tracks: per-track MIDI analysis
    """
    findings = []
    track_analyses = []

    total_notes = 0
    all_velocities = []
    all_pitches = []

    for track in project.tracks:
        if not track.midi_clips:
            continue

        track_notes = []
        clip_analyses = []
        for clip in track.midi_clips:
            if not clip.notes:
                continue
            track_notes.extend(clip.notes)
            analysis = _analyze_clip_notes(clip.notes)
            if analysis:
                analysis["clip_name"] = clip.name
                analysis["clip_time"] = clip.time
                clip_analyses.append(analysis)

        if not track_notes:
            continue

        track_analysis = _analyze_clip_notes(track_notes)
        if track_analysis:
            track_analysis["track_name"] = track.name
            track_analysis["clip_count"] = len(track.midi_clips)

            # Per-track findings
            vel = track_analysis.get("velocity", {})
            vel_range = vel.get("range", 127)
            if vel_range < 10 and len(track_notes) > 8:
                findings.append({
                    "type": "flat_velocity",
                    "severity": "suggestion",
                    "message": f"'{track.name}' — velocity range is only {vel_range:.0f} across {len(track_notes)} notes. Consider adding dynamics.",
                    "track": track.name,
                })

            if vel.get("max", 0) > 126 and vel.get("min", 0) > 120:
                findings.append({
                    "type": "all_max_velocity",
                    "severity": "info",
                    "message": f"'{track.name}' — all notes near max velocity ({vel.get('min', 0):.0f}-{vel.get('max', 0):.0f}). Intentional or needs humanization?",
                    "track": track.name,
                })

            # Check for single-note parts
            pitch = track_analysis.get("pitch", {})
            if pitch.get("unique_pitches", 0) == 1 and len(track_notes) > 4:
                findings.append({
                    "type": "single_pitch",
                    "severity": "info",
                    "message": f"'{track.name}' — all {len(track_notes)} notes are {pitch.get('most_common', '?')}",
                    "track": track.name,
                })

            if clip_analyses:
                track_analysis["clips"] = clip_analyses
            track_analyses.append(track_analysis)

            total_notes += len(track_notes)
            all_velocities.extend(n.velocity for n in track_notes if n.velocity is not None)
            all_pitches.extend(n.pitch for n in track_notes if n.pitch is not None)

    # --- Project-wide findings ---
    if all_velocities:
        project_vel_range = max(all_velocities) - min(all_velocities)
        if project_vel_range < 20 and total_notes > 50:
            findings.append({
                "type": "project_flat_velocity",
                "severity": "suggestion",
                "message": f"Project-wide velocity range is only {project_vel_range:.0f} — the overall dynamics feel flat",
            })

    # --- Key detection hint ---
    key_hint = None
    if all_pitches:
        note_classes = Counter(p % 12 for p in all_pitches)
        top_notes = [_NOTE_NAMES[nc] for nc, _ in note_classes.most_common(7)]
        root_candidates = note_classes.most_common(3)
        key_hint = {
            "most_used_notes": top_notes,
            "likely_root": _NOTE_NAMES[root_candidates[0][0]] if root_candidates else None,
        }
        # Compare with project scale setting
        if project.scale and project.scale.root_note is not None:
            set_root = _NOTE_NAMES[project.scale.root_note]
            detected_root = _NOTE_NAMES[root_candidates[0][0]] if root_candidates else None
            if detected_root and set_root != detected_root:
                findings.append({
                    "type": "key_mismatch",
                    "severity": "info",
                    "message": f"Project scale is set to {set_root} {project.scale.name}, but MIDI data suggests {detected_root} as root",
                })

    summary = {
        "tracks_with_midi": len(track_analyses),
        "total_notes": total_notes,
        "total_clips": sum(len(t.midi_clips) for t in project.tracks),
    }
    if all_velocities:
        summary["velocity_range"] = {
            "min": round(min(all_velocities), 1),
            "max": round(max(all_velocities), 1),
        }
    if key_hint:
        summary["key_hint"] = key_hint

    return {
        "summary": summary,
        "findings": findings,
        "tracks": track_analyses,
    }
