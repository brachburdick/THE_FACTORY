"""Extract tracks from LiveSet, assembling data from all extractors."""
from __future__ import annotations

import logging
from xml.etree.ElementTree import Element

from ..models import Track
from ._xml_helpers import find, find_all, attr_int, value_str, value_int, value_bool
from .mixer import extract_mixer, extract_routing
from .clips import extract_arrangement_clips, extract_clip_slots
from .devices import extract_devices
from .automation import extract_automation_envelopes

logger = logging.getLogger(__name__)

# Map XML tag to track type
TRACK_TYPE_MAP = {
    "MidiTrack": "midi",
    "AudioTrack": "audio",
    "ReturnTrack": "return",
    "GroupTrack": "group",
    "MasterTrack": "master",
    "MainTrack": "master",
}


def _extract_single_track(el: Element, index: int) -> Track:
    """Extract a single track element into a Track dataclass."""
    track_type = TRACK_TYPE_MAP.get(el.tag, "unknown")
    track_id = attr_int(el, "Id")

    # Name
    name_el = find(el, "Name")
    effective_name = value_str(name_el, "EffectiveName") if name_el is not None else None
    user_name = value_str(name_el, "UserName") if name_el is not None else None

    # DeviceChain (contains mixer, routing, sequencer, devices)
    dc = find(el, "DeviceChain")

    # Mixer
    mixer = extract_mixer(dc)

    # Routing
    audio_in, midi_in, audio_out, midi_out = extract_routing(dc)

    # Clips
    midi_clips, audio_clips = extract_arrangement_clips(dc) if dc is not None else ([], [])

    # Clip slots (session view)
    clip_slots = extract_clip_slots(dc) if dc is not None else []

    # Devices — look in DeviceChain > DeviceChain > Devices
    inner_dc = find(dc, "DeviceChain") if dc is not None else None
    devices = extract_devices(inner_dc) if inner_dc is not None else []

    # Automation
    automation = extract_automation_envelopes(dc)

    return Track(
        id=track_id,
        name=effective_name,
        user_name=user_name,
        track_type=track_type,
        color=value_int(el, "Color"),
        index=index,
        group_id=value_int(el, "TrackGroupId"),
        is_frozen=value_bool(el, "Freeze"),
        is_folded=value_bool(el, "IsFolded"),
        mixer=mixer,
        audio_input_routing=audio_in,
        midi_input_routing=midi_in,
        audio_output_routing=audio_out,
        midi_output_routing=midi_out,
        midi_clips=midi_clips,
        audio_clips=audio_clips,
        clip_slots=clip_slots,
        devices=devices,
        automation_envelopes=automation,
    )


def extract_tracks(live_set: Element) -> tuple[list[Track], list[Track]]:
    """Extract all tracks from LiveSet.

    Returns (main_tracks, return_tracks) separately since Ableton
    stores them in the same <Tracks> element but they serve different roles.
    """
    tracks_el = find(live_set, "Tracks")
    if tracks_el is None:
        return [], []

    main_tracks: list[Track] = []
    return_tracks: list[Track] = []
    main_idx = 0
    return_idx = 0

    for child in tracks_el:
        try:
            if child.tag == "ReturnTrack":
                track = _extract_single_track(child, return_idx)
                return_tracks.append(track)
                return_idx += 1
            else:
                track = _extract_single_track(child, main_idx)
                main_tracks.append(track)
                main_idx += 1
        except Exception:
            logger.warning(
                "Failed to parse track %s Id=%s",
                child.tag, child.attrib.get("Id"),
                exc_info=True,
            )

    return main_tracks, return_tracks


def extract_master_track(live_set: Element) -> Track | None:
    """Extract the master track. Live 11 uses MasterTrack, Live 12 uses MainTrack."""
    master_el = find(live_set, "MasterTrack")
    if master_el is None:
        master_el = find(live_set, "MainTrack")
    if master_el is None:
        return None
    try:
        return _extract_single_track(master_el, 0)
    except Exception:
        logger.warning("Failed to parse master track", exc_info=True)
        return None
