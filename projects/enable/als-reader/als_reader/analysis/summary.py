"""Compact project summary for quick overview."""
from __future__ import annotations

import json
from ..models import ALSProject

_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def summarize(project: ALSProject) -> dict:
    """Build a compact summary suitable for initial agent assessment."""
    tracks_summary = []
    for t in project.tracks:
        n_clips = len(t.midi_clips) + len(t.audio_clips)
        n_notes = sum(c.note_count for c in t.midi_clips)
        device_names = [d.plugin_name or d.class_name for d in t.devices]
        entry = {
            "name": t.name,
            "type": t.track_type,
            "color": t.color,
        }
        if t.group_id is not None and t.group_id >= 0:
            entry["group_id"] = t.group_id
        if t.mixer:
            entry["volume"] = t.mixer.volume
            entry["pan"] = t.mixer.pan
            if t.mixer.solo:
                entry["solo"] = True
            if t.mixer.speaker is False:
                entry["muted"] = True
        if n_clips > 0:
            entry["clips"] = n_clips
        if n_notes > 0:
            entry["midi_notes"] = n_notes
        if device_names:
            entry["devices"] = device_names
        tracks_summary.append(entry)

    returns_summary = []
    for t in project.return_tracks:
        entry = {"name": t.name}
        if t.mixer:
            entry["volume"] = t.mixer.volume
        device_names = [d.plugin_name or d.class_name for d in t.devices]
        if device_names:
            entry["devices"] = device_names
        returns_summary.append(entry)

    result = {
        "file": project.file_path,
        "ableton_version": project.version.ableton_version() if project.version else None,
        "tempo": project.tempo,
    }
    if project.time_signature:
        result["time_signature"] = f"{project.time_signature.numerator}/{project.time_signature.denominator}"
    if project.scale and (project.scale.name or project.scale.root_note is not None):
        root = _NOTE_NAMES[project.scale.root_note] if project.scale.root_note is not None else "?"
        result["scale"] = f"{root} {project.scale.name or 'unknown'}"
    if project.transport:
        if project.transport.loop_on:
            result["loop"] = {
                "start": project.transport.loop_start,
                "length": project.transport.loop_length,
            }

    result["track_count"] = project.track_count
    result["total_clips"] = sum(
        len(t.midi_clips) + len(t.audio_clips) for t in project.tracks
    )
    result["total_midi_notes"] = sum(
        sum(c.note_count for c in t.midi_clips) for t in project.tracks
    )

    if project.locators:
        result["markers"] = [
            {"name": l.name, "time": l.time} for l in project.locators
        ]
    if project.scenes:
        result["scenes"] = [
            {"name": s.name, "tempo": s.tempo} for s in project.scenes
        ]

    result["tracks"] = tracks_summary
    if returns_summary:
        result["return_tracks"] = returns_summary

    if project.master_track and project.master_track.mixer:
        master = {"volume": project.master_track.mixer.volume}
        master_devices = [d.plugin_name or d.class_name for d in project.master_track.devices]
        if master_devices:
            master["devices"] = master_devices
        result["master"] = master

    if project.grooves:
        result["grooves"] = [g.name for g in project.grooves]

    return result


def summarize_json(project: ALSProject, indent: int = 2) -> str:
    """Serialize a project summary to JSON."""
    return json.dumps(summarize(project), indent=indent)
