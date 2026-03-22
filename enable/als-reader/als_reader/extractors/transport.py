"""Extract transport, tempo, time signature, locators, scale, and groove pool."""
from __future__ import annotations

import logging
from xml.etree.ElementTree import Element

from ..models import (
    TransportInfo, TimeSignature, Locator, ScaleInfo, GrooveSettings,
)
from ._xml_helpers import find, find_all, value_float, value_int, value_bool, value_str, attr, attr_float, attr_int

logger = logging.getLogger(__name__)


# Common Ableton time sig Manual values (index → num/den)
_TS_MANUAL_MAP = {
    201: (4, 4), 200: (3, 4), 202: (5, 4), 203: (6, 4), 204: (7, 4),
    199: (2, 4), 198: (1, 4),
    101: (4, 8), 100: (3, 8), 102: (5, 8), 103: (6, 8), 104: (7, 8),
    99: (2, 8), 98: (1, 8),
    301: (4, 2), 300: (3, 2), 302: (5, 2),
    1: (4, 16), 0: (3, 16),
}


def extract_time_signature(mixer_el: Element | None, live_set: Element | None = None) -> TimeSignature | None:
    """Extract time signature from the master track mixer.

    Live 11: mixer has TimeSignature/TimeSignatures/RemoteableTimeSignature with Numerator/Denominator.
    Live 12: mixer has TimeSignature/Manual with an encoded int; explicit num/den on per-clip elements.
    """
    ts_el = find(mixer_el, "TimeSignature")
    if ts_el is not None:
        # Try Live 11 style: nested RemoteableTimeSignature
        sigs = find(ts_el, "TimeSignatures")
        if sigs is not None:
            first = find(sigs, "RemoteableTimeSignature")
            if first is not None:
                return TimeSignature(
                    numerator=value_int(first, "Numerator") or 4,
                    denominator=value_int(first, "Denominator") or 4,
                    time=value_float(first, "Time") or 0.0,
                )

        # Try Live 12 style: decode Manual value
        manual = value_int(ts_el, "Manual")
        if manual is not None and manual in _TS_MANUAL_MAP:
            num, den = _TS_MANUAL_MAP[manual]
            return TimeSignature(numerator=num, denominator=den)

    # Fallback: find first RemoteableTimeSignature anywhere in LiveSet
    if live_set is not None:
        for rts in live_set.iter("RemoteableTimeSignature"):
            num = value_int(rts, "Numerator")
            den = value_int(rts, "Denominator")
            if num is not None and den is not None:
                return TimeSignature(numerator=num, denominator=den)

    return None


def extract_transport(live_set: Element) -> TransportInfo:
    """Extract transport state from LiveSet."""
    transport_el = find(live_set, "Transport")

    # Tempo comes from master track mixer
    # Live 11 uses "MasterTrack", Live 12 uses "MainTrack"
    master = find(live_set, "MasterTrack")
    if master is None:
        master = find(live_set, "MainTrack")
    master_dc = find(master, "DeviceChain")
    master_mixer = find(master_dc, "Mixer")

    tempo_el = find(master_mixer, "Tempo")
    tempo = attr_float(find(tempo_el, "Manual")) if tempo_el is not None else None

    time_sig = extract_time_signature(master_mixer, live_set)

    return TransportInfo(
        tempo=tempo,
        time_signature=time_sig,
        loop_on=value_bool(transport_el, "LoopOn"),
        loop_start=value_float(transport_el, "LoopStart"),
        loop_length=value_float(transport_el, "LoopLength"),
        current_time=value_float(transport_el, "CurrentTime"),
        punch_in=value_bool(transport_el, "PunchIn"),
        punch_out=value_bool(transport_el, "PunchOut"),
        metronome_on=value_bool(transport_el, "MetronomeOn"),
    )


def extract_locators(live_set: Element) -> list[Locator]:
    """Extract locators/markers from LiveSet."""
    locators_wrapper = find(live_set, "Locators")
    if locators_wrapper is None:
        return []
    locators_inner = find(locators_wrapper, "Locators")
    if locators_inner is None:
        return []

    result = []
    for loc_el in find_all(locators_inner, "Locator"):
        result.append(Locator(
            id=attr_int(loc_el, "Id"),
            time=value_float(loc_el, "Time"),
            name=value_str(loc_el, "Name"),
            annotation=value_str(loc_el, "Annotation"),
            is_song_start=value_bool(loc_el, "IsSongStart"),
        ))
    return result


# Live 12 stores scale name as a numeric enum
_SCALE_NAMES = {
    "0": "Major", "1": "Minor", "2": "Dorian", "3": "Mixolydian",
    "4": "Lydian", "5": "Phrygian", "6": "Locrian",
    "7": "Diminished", "8": "Whole-Half", "9": "Whole Tone",
    "10": "Minor Blues", "11": "Minor Pentatonic", "12": "Major Pentatonic",
    "13": "Harmonic Minor", "14": "Melodic Minor", "15": "Super Locrian",
    "16": "Bhairav", "17": "Hungarian Minor", "18": "Minor Gypsy",
    "19": "Hirajoshi", "20": "Japanese", "21": "Pentatonic",
    "22": "Spanish",
}


def extract_scale(live_set: Element) -> ScaleInfo | None:
    """Extract scale information."""
    scale_el = find(live_set, "ScaleInformation")
    if scale_el is None:
        return None
    # Live 11 uses "RootNote", Live 12 uses "Root"
    root = value_int(scale_el, "RootNote")
    if root is None:
        root = value_int(scale_el, "Root")
    raw_name = value_str(scale_el, "Name")
    # Resolve numeric enum to human-readable name
    name = _SCALE_NAMES.get(raw_name, raw_name) if raw_name else None
    return ScaleInfo(root_note=root, name=name)


def extract_grooves(live_set: Element) -> list[GrooveSettings]:
    """Extract groove pool settings."""
    pool_el = find(live_set, "GroovePool")
    if pool_el is None:
        return []
    grooves_el = find(pool_el, "Grooves")
    if grooves_el is None:
        return []

    result = []
    for g in find_all(grooves_el, "Groove"):
        result.append(GrooveSettings(
            id=attr_int(g, "Id"),
            name=value_str(g, "Name"),
            base=value_float(g, "Base"),
            quantize=value_float(g, "Quantize"),
            timing=value_float(g, "Timing"),
            random=value_float(g, "Random"),
            velocity=value_float(g, "Velocity"),
        ))
    return result
