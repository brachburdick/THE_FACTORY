"""Unified feedback report combining all analyzers."""
from __future__ import annotations

import json
from ..models import ALSProject
from .arrangement import analyze_arrangement
from .mix import analyze_mix
from .midi import analyze_midi
from .devices import analyze_devices


def generate_feedback_report(
    project: ALSProject,
    include_track_details: bool = False,
) -> dict:
    """Generate a comprehensive feedback report for an Ableton project.

    Args:
        project: Parsed ALSProject.
        include_track_details: If True, include per-track detail data
            (clip coverage, MIDI per-clip, device chains). Makes the report
            much larger but more useful for deep dives.

    Returns:
        Dict with project overview, all findings sorted by severity,
        and section-specific analysis data.
    """
    arrangement = analyze_arrangement(project)
    mix = analyze_mix(project)
    midi_analysis = analyze_midi(project)
    device_analysis = analyze_devices(project)

    # --- Collect and sort all findings ---
    severity_order = {"warning": 0, "suggestion": 1, "info": 2}
    all_findings = []
    for section, analysis in [
        ("arrangement", arrangement),
        ("mix", mix),
        ("midi", midi_analysis),
        ("devices", device_analysis),
    ]:
        for f in analysis.get("findings", []):
            f["section"] = section
            all_findings.append(f)

    all_findings.sort(key=lambda f: severity_order.get(f.get("severity", "info"), 99))

    # --- Project overview ---
    overview = {
        "file": project.file_path,
        "ableton_version": project.version.ableton_version() if project.version else None,
        "tempo": project.tempo,
    }
    if project.time_signature:
        overview["time_signature"] = f"{project.time_signature.numerator}/{project.time_signature.denominator}"
    if project.scale and project.scale.name:
        _NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        root = _NOTE_NAMES[project.scale.root_note] if project.scale.root_note is not None else "?"
        overview["scale"] = f"{root} {project.scale.name}"

    overview["track_count"] = project.track_count
    overview["return_count"] = len(project.return_tracks)

    # --- Section summaries ---
    report = {
        "overview": overview,
        "findings": all_findings,
        "finding_counts": {
            "warning": sum(1 for f in all_findings if f.get("severity") == "warning"),
            "suggestion": sum(1 for f in all_findings if f.get("severity") == "suggestion"),
            "info": sum(1 for f in all_findings if f.get("severity") == "info"),
        },
        "arrangement": arrangement["summary"],
        "mix": mix["summary"],
        "midi": midi_analysis["summary"],
        "devices": device_analysis["summary"],
    }

    if include_track_details:
        report["arrangement_tracks"] = arrangement.get("track_coverage", {})
        report["mix_tracks"] = mix.get("track_levels", [])
        report["midi_tracks"] = midi_analysis.get("tracks", [])
        report["device_tracks"] = device_analysis.get("tracks", [])

    return report


def feedback_to_json(report: dict, indent: int = 2) -> str:
    """Serialize a feedback report to JSON."""
    return json.dumps(report, indent=indent)
