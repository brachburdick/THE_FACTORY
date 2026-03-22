"""Mix analysis: volume distribution, panning, sends, routing issues."""
from __future__ import annotations

import math
from ..models import ALSProject, Track


def _db_from_linear(linear: float) -> float:
    """Convert linear volume (0-1+ range) to dB. Ableton uses a curved mapping."""
    if linear <= 0:
        return -70.0
    return 20 * math.log10(linear)


def analyze_mix(project: ALSProject) -> dict:
    """Analyze mix state and produce findings.

    Returns:
    - summary: mix overview stats
    - findings: list of observations/issues
    - track_levels: per-track volume/pan data
    """
    findings = []
    track_levels = []

    active_tracks = [t for t in project.tracks if t.track_type != "group"]
    tracks_with_mixer = [t for t in active_tracks if t.mixer is not None]

    # --- Per-track level data ---
    volumes = []
    pans = []
    for t in tracks_with_mixer:
        m = t.mixer
        vol = m.volume
        pan = m.pan

        entry = {
            "name": t.name or f"Track {t.index}",
            "type": t.track_type,
        }
        if vol is not None:
            entry["volume"] = round(vol, 4)
            entry["volume_db"] = round(_db_from_linear(vol), 1)
            volumes.append(vol)
        if pan is not None:
            entry["pan"] = round(pan, 3)
            pans.append(pan)
        if m.solo:
            entry["solo"] = True
        if m.speaker is False:
            entry["muted"] = True
        if m.sends:
            entry["sends"] = [round(s.value, 3) for s in m.sends if s.value is not None]

        track_levels.append(entry)

    # --- Volume distribution analysis ---
    if volumes:
        max_vol = max(volumes)
        min_vol = min(v for v in volumes if v > 0) if any(v > 0 for v in volumes) else 0
        avg_vol = sum(volumes) / len(volumes)

        # Check for tracks at unity or above
        hot_tracks = [
            tl["name"] for tl in track_levels
            if tl.get("volume", 0) > 1.0 and not tl.get("muted")
        ]
        if hot_tracks:
            findings.append({
                "type": "hot_tracks",
                "severity": "warning",
                "message": f"{len(hot_tracks)} tracks above unity gain",
                "tracks": hot_tracks,
            })

        # Check for tracks near zero
        quiet_tracks = [
            tl["name"] for tl in track_levels
            if 0 < tl.get("volume", 1) < 0.05 and not tl.get("muted")
        ]
        if quiet_tracks:
            findings.append({
                "type": "very_quiet_tracks",
                "severity": "info",
                "message": f"{len(quiet_tracks)} active tracks are nearly silent (below -26dB)",
                "tracks": quiet_tracks,
            })

    # --- Muted tracks with clips ---
    muted_with_content = []
    for t in active_tracks:
        if t.mixer and t.mixer.speaker is False:
            n_clips = len(t.midi_clips) + len(t.audio_clips)
            if n_clips > 0:
                muted_with_content.append(t.name or f"Track {t.index}")

    if muted_with_content:
        findings.append({
            "type": "muted_with_content",
            "severity": "info",
            "message": f"{len(muted_with_content)} muted tracks contain clips — intentional or forgotten?",
            "tracks": muted_with_content,
        })

    # --- Solo check ---
    soloed = [tl["name"] for tl in track_levels if tl.get("solo")]
    if soloed:
        findings.append({
            "type": "solo_engaged",
            "severity": "warning",
            "message": f"{len(soloed)} tracks are soloed — was this intentional?",
            "tracks": soloed,
        })

    # --- Panning analysis ---
    if pans:
        hard_left = [tl["name"] for tl in track_levels if (tl.get("pan") or 0) < -0.9]
        hard_right = [tl["name"] for tl in track_levels if (tl.get("pan") or 0) > 0.9]
        center = [tl["name"] for tl in track_levels if abs(tl.get("pan") or 0) < 0.05]

        if len(center) == len(pans) and len(pans) > 3:
            findings.append({
                "type": "all_center",
                "severity": "suggestion",
                "message": "All tracks are centered — consider panning some elements for stereo width",
            })
        elif len(center) > len(pans) * 0.8 and len(pans) > 5:
            findings.append({
                "type": "mostly_center",
                "severity": "info",
                "message": f"{len(center)} of {len(pans)} tracks are centered — room for more stereo spread",
            })

        if hard_left and not hard_right:
            findings.append({
                "type": "panning_imbalance",
                "severity": "info",
                "message": f"Tracks panned hard left ({hard_left}) but nothing hard right",
            })
        elif hard_right and not hard_left:
            findings.append({
                "type": "panning_imbalance",
                "severity": "info",
                "message": f"Tracks panned hard right ({hard_right}) but nothing hard left",
            })

    # --- Send usage ---
    n_returns = len(project.return_tracks)
    tracks_using_sends = 0
    for t in tracks_with_mixer:
        if t.mixer.sends and any(s.value and s.value > 0.01 for s in t.mixer.sends):
            tracks_using_sends += 1

    if n_returns > 0 and tracks_using_sends == 0:
        findings.append({
            "type": "unused_returns",
            "severity": "info",
            "message": f"{n_returns} return tracks exist but no tracks are sending to them",
        })
    elif n_returns == 0 and len(tracks_with_mixer) > 5:
        findings.append({
            "type": "no_returns",
            "severity": "suggestion",
            "message": "No return tracks — consider adding shared reverb/delay for cohesion and CPU efficiency",
        })

    # --- Routing check ---
    tracks_to_master = 0
    tracks_to_group = 0
    for t in active_tracks:
        if t.audio_output_routing:
            target = t.audio_output_routing.target or ""
            if "Master" in target or "Main" in target:
                tracks_to_master += 1
            elif "GroupTrack" in target or "Group" in target:
                tracks_to_group += 1

    # --- Master track ---
    master_info = None
    if project.master_track and project.master_track.mixer:
        master_vol = project.master_track.mixer.volume
        master_info = {
            "volume": round(master_vol, 4) if master_vol else None,
            "volume_db": round(_db_from_linear(master_vol), 1) if master_vol else None,
            "devices": [d.plugin_name or d.class_name for d in project.master_track.devices],
        }
        if master_vol and master_vol > 1.0:
            findings.append({
                "type": "master_above_unity",
                "severity": "warning",
                "message": f"Master track is above unity ({_db_from_linear(master_vol):.1f} dB) — risk of clipping",
            })

    summary = {
        "tracks_analyzed": len(tracks_with_mixer),
        "tracks_muted": len(muted_with_content),
        "tracks_soloed": len(soloed),
        "tracks_using_sends": tracks_using_sends,
        "return_tracks": n_returns,
        "routing_to_master": tracks_to_master,
        "routing_to_groups": tracks_to_group,
    }
    if master_info:
        summary["master"] = master_info

    return {
        "summary": summary,
        "findings": findings,
        "track_levels": track_levels,
    }
