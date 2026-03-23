"""Extract mixer state: volume, pan, sends, routing."""
from __future__ import annotations

import logging
from xml.etree.ElementTree import Element

from ..models import MixerInfo, SendInfo, IORouting
from ._xml_helpers import find, find_all, value_str, value_bool, value_int, manual_value, attr_float, attr_bool

logger = logging.getLogger(__name__)


def _extract_sends(mixer_el: Element) -> list[SendInfo]:
    """Extract send levels from SendsListPreset."""
    sends_list = find(mixer_el, "SendsListPreset")
    if sends_list is None:
        return []

    result = []
    for preset in find_all(sends_list, "SendPreset"):
        send_el = find(preset, "Send")
        value = manual_value(preset, "Send") if send_el is None else attr_float(find(send_el, "Manual"))
        active = value_bool(preset, "Active")
        result.append(SendInfo(value=value, active=active))

    return result


def extract_mixer(device_chain_el: Element | None) -> MixerInfo | None:
    """Extract mixer info from a track's DeviceChain."""
    if device_chain_el is None:
        return None

    mixer_el = find(device_chain_el, "Mixer")
    if mixer_el is None:
        return None

    return MixerInfo(
        volume=manual_value(mixer_el, "Volume"),
        pan=manual_value(mixer_el, "Pan"),
        sends=_extract_sends(mixer_el),
        speaker=value_bool(mixer_el, "Speaker"),
        solo=value_bool(mixer_el, "Solo"),
        cross_fade_state=value_int(mixer_el, "CrossFadeState"),
    )


def _extract_routing(parent: Element | None, tag: str) -> IORouting | None:
    """Extract an I/O routing element."""
    if parent is None:
        return None
    routing_el = find(parent, tag)
    if routing_el is None:
        return None
    return IORouting(
        target=value_str(routing_el, "Target"),
        upper_display_string=value_str(routing_el, "UpperDisplayString"),
        lower_display_string=value_str(routing_el, "LowerDisplayString"),
    )


def extract_routing(device_chain_el: Element | None) -> tuple[
    IORouting | None, IORouting | None, IORouting | None, IORouting | None
]:
    """Extract all four routing targets. Returns (audio_in, midi_in, audio_out, midi_out)."""
    return (
        _extract_routing(device_chain_el, "AudioInputRouting"),
        _extract_routing(device_chain_el, "MidiInputRouting"),
        _extract_routing(device_chain_el, "AudioOutputRouting"),
        _extract_routing(device_chain_el, "MidiOutputRouting"),
    )
