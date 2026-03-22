"""Device chain analysis: plugins, racks, bypassed devices, signal flow."""
from __future__ import annotations

from collections import Counter
from ..models import ALSProject, Track, Device


def _analyze_device_list(devices: list[Device], track_name: str) -> list[dict]:
    """Produce a summary of each device in a chain."""
    result = []
    for d in devices:
        entry = {
            "name": d.plugin_name or d.class_name or "Unknown",
            "type": d.device_type,
            "on": d.is_on,
        }
        if d.rack_type:
            entry["rack_type"] = d.rack_type
            entry["chain_count"] = len(d.chains)
            if d.macros:
                entry["macros"] = len(d.macros)
        if d.plugin_vendor:
            entry["vendor"] = d.plugin_vendor
        if d.parameters:
            entry["parameters"] = {p.name: p.value for p in d.parameters}
        result.append(entry)
    return result


def analyze_devices(project: ALSProject) -> dict:
    """Analyze device chains across the project.

    Returns:
    - summary: device counts, plugin usage
    - findings: observations and issues
    - tracks: per-track device chain info
    """
    findings = []
    track_devices = []

    all_plugins = Counter()
    all_native = Counter()
    plugin_vendors = Counter()
    total_devices = 0
    bypassed_devices = []
    empty_chains = []
    rack_count = 0

    for track in project.all_tracks:
        if not track.devices:
            continue

        chain = _analyze_device_list(track.devices, track.name or "")
        track_entry = {
            "track_name": track.name,
            "track_type": track.track_type,
            "device_count": len(track.devices),
            "chain": chain,
        }
        track_devices.append(track_entry)

        for d in track.devices:
            total_devices += 1

            # Count by type
            if d.device_type in ("vst", "vst3", "au"):
                all_plugins[d.plugin_name or d.class_name] += 1
                if d.plugin_vendor:
                    plugin_vendors[d.plugin_vendor] += 1
            elif d.device_type == "native":
                all_native[d.class_name or d.name] += 1
            elif d.device_type == "rack":
                rack_count += 1

            # Bypassed devices
            if d.is_on is False:
                bypassed_devices.append({
                    "device": d.plugin_name or d.class_name,
                    "track": track.name,
                })

            # Empty racks
            if d.rack_type and len(d.chains) == 0:
                empty_chains.append({
                    "device": d.class_name,
                    "rack_type": d.rack_type,
                    "track": track.name,
                })

            # Recurse into rack chains
            for rc in d.chains:
                for rd in rc.devices:
                    total_devices += 1
                    if rd.device_type in ("vst", "vst3", "au"):
                        all_plugins[rd.plugin_name or rd.class_name] += 1
                        if rd.plugin_vendor:
                            plugin_vendors[rd.plugin_vendor] += 1
                    elif rd.device_type == "native":
                        all_native[rd.class_name or rd.name] += 1

                    if rd.is_on is False:
                        bypassed_devices.append({
                            "device": rd.plugin_name or rd.class_name,
                            "track": track.name,
                            "rack_chain": rc.name,
                        })

    # --- Findings ---
    if bypassed_devices:
        if len(bypassed_devices) > 5:
            findings.append({
                "type": "many_bypassed",
                "severity": "info",
                "message": f"{len(bypassed_devices)} devices are bypassed — clean up or remove unused ones",
                "devices": bypassed_devices[:10],  # cap at 10
            })
        else:
            findings.append({
                "type": "bypassed_devices",
                "severity": "info",
                "message": f"{len(bypassed_devices)} bypassed devices",
                "devices": bypassed_devices,
            })

    if empty_chains:
        findings.append({
            "type": "empty_racks",
            "severity": "info",
            "message": f"{len(empty_chains)} empty rack devices",
            "racks": empty_chains,
        })

    # Heavy tracks (many devices)
    heavy_tracks = [
        td for td in track_devices if td["device_count"] >= 8
    ]
    if heavy_tracks:
        findings.append({
            "type": "heavy_device_chains",
            "severity": "info",
            "message": f"{len(heavy_tracks)} tracks have 8+ devices — potential CPU hogs",
            "tracks": [
                {"track": t["track_name"], "devices": t["device_count"]}
                for t in sorted(heavy_tracks, key=lambda x: -x["device_count"])[:5]
            ],
        })

    # Tracks with no devices at all (non-group, non-return)
    naked_tracks = [
        t.name for t in project.tracks
        if t.track_type not in ("group",) and not t.devices
        and (len(t.midi_clips) + len(t.audio_clips)) > 0
    ]
    if naked_tracks:
        findings.append({
            "type": "no_devices",
            "severity": "info",
            "message": f"{len(naked_tracks)} tracks with clips but no devices/instruments",
            "tracks": naked_tracks,
        })

    # Duplicate plugin usage
    heavily_used = [(name, count) for name, count in all_plugins.most_common() if count >= 5]
    if heavily_used:
        findings.append({
            "type": "heavily_used_plugins",
            "severity": "info",
            "message": "Frequently used plugins",
            "plugins": [{"name": n, "instances": c} for n, c in heavily_used],
        })

    # Return/master chain analysis
    master_chain = []
    if project.master_track and project.master_track.devices:
        master_chain = [d.plugin_name or d.class_name for d in project.master_track.devices]
        has_limiter = any(
            "limit" in (d.class_name or "").lower() or "limit" in (d.plugin_name or "").lower()
            for d in project.master_track.devices
        )
        if not has_limiter and master_chain:
            findings.append({
                "type": "no_master_limiter",
                "severity": "suggestion",
                "message": "No limiter detected on master — consider adding one to protect against clipping",
            })

    summary = {
        "total_devices": total_devices,
        "third_party_plugins": dict(all_plugins.most_common(15)),
        "native_devices": dict(all_native.most_common(15)),
        "plugin_vendors": dict(plugin_vendors.most_common(10)),
        "rack_count": rack_count,
        "bypassed_count": len(bypassed_devices),
    }
    if master_chain:
        summary["master_chain"] = master_chain

    return {
        "summary": summary,
        "findings": findings,
        "tracks": track_devices,
    }
