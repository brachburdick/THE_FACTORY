"""Extract device chains, plugins, racks, and parameters."""
from __future__ import annotations

import logging
from xml.etree.ElementTree import Element

from ..models import Device, DeviceParameter, RackChain, MacroMapping
from ._xml_helpers import find, find_all, attr_int, attr_bool, value_str, value_bool, attr_float

logger = logging.getLogger(__name__)

# Known Ableton native device tags
NATIVE_INSTRUMENTS = {
    "OriginalSimpler", "MultiSampler", "Operator", "Collision", "Tension",
    "Electric", "Analog", "Wavetable", "Drift", "Meld", "DrumGroupDevice",
    "InstrumentGroupDevice", "Simpler",
}

NATIVE_EFFECTS = {
    "Eq8", "Compressor2", "GlueCompressor", "Limiter", "MultibandDynamics",
    "Gate", "AutoFilter", "Chorus2", "Delay", "PingPongDelay", "FilterDelay",
    "Reverb", "Hybrid Reverb", "Echo", "Erosion", "Redux2", "Vinyl",
    "Saturator", "Overdrive", "Amp", "Cabinet", "Corpus", "FrequencyShifter",
    "Phaser", "Flanger", "Resonators", "Vocoder", "BeatRepeat", "Looper",
    "Utility", "Tuner", "Spectrum", "Pedal", "DrumBuss", "ChannelEq",
    "AutoPan", "StereoGain", "AudioEffectGroupDevice", "MidiEffectGroupDevice",
    "CrossDelay", "SpectralResonator", "SpectralTime", "ShifterDevice",
    "InstrumentVector",
}

RACK_TAGS = {
    "InstrumentGroupDevice": "instrument_rack",
    "AudioEffectGroupDevice": "effect_rack",
    "MidiEffectGroupDevice": "midi_effect_rack",
    "DrumGroupDevice": "drum_rack",
}

# Known parameter tags to extract values from
KNOWN_PARAMS = {
    "Threshold", "Ratio", "Attack", "Release", "Gain", "DryWet",
    "Ceiling", "Mode", "DecayTime", "RoomSize", "PitchCoarse", "PitchFine",
}


def _classify_device(tag: str, el: Element) -> tuple[str, str | None, str | None, str | None]:
    """Classify a device element. Returns (device_type, plugin_name, vendor, category)."""
    if tag == "PluginDevice":
        desc = find(el, "PluginDesc")
        if desc is not None:
            vst = find(desc, "VstPluginInfo")
            if vst is not None:
                return (
                    "vst",
                    value_str(vst, "PlugName"),
                    value_str(vst, "Vendor"),
                    value_str(vst, "Category"),
                )
            vst3 = find(desc, "Vst3PluginInfo")
            if vst3 is not None:
                return (
                    "vst3",
                    value_str(vst3, "Name"),
                    value_str(vst3, "Vendor"),
                    value_str(vst3, "Category"),
                )
        return ("vst", None, None, None)

    if tag == "AuPluginDevice":
        desc = find(el, "PluginDesc")
        if desc is not None:
            au = find(desc, "AuPluginInfo")
            if au is not None:
                return (
                    "au",
                    value_str(au, "Name"),
                    value_str(au, "Manufacturer"),
                    None,
                )
        return ("au", None, None, None)

    if tag == "MxDeviceAudioEffect" or tag == "MxDeviceInstrument" or tag.startswith("MxDevice"):
        return ("max4live", None, None, None)

    if tag in RACK_TAGS:
        return ("rack", None, None, None)

    if tag in NATIVE_INSTRUMENTS or tag in NATIVE_EFFECTS:
        return ("native", None, None, None)

    # Unknown — treat as native
    return ("native", None, None, None)


def _extract_params(el: Element) -> list[DeviceParameter]:
    """Extract known parameter values from a device element."""
    params = []
    for tag in KNOWN_PARAMS:
        child = find(el, tag)
        if child is not None:
            val = child.attrib.get("Value")
            if val is not None:
                try:
                    val = float(val)
                except (ValueError, TypeError):
                    pass
                params.append(DeviceParameter(name=tag, value=val))
    return params


def _extract_macros(el: Element) -> list[MacroMapping]:
    """Extract macro mappings from a rack device."""
    macros_el = find(el, "Macros")
    if macros_el is None:
        return []

    result = []
    for i in range(16):  # Ableton supports up to 16 macros
        macro_el = find(macros_el, f"Macro{i}")
        if macro_el is None:
            break
        name = value_str(macro_el, "MacroName")
        val = attr_float(find(macro_el, "Manual"))
        result.append(MacroMapping(name=name, value=val))
    return result


def _extract_rack_chains(el: Element) -> list[RackChain]:
    """Extract chains from a rack device (instrument, effect, or drum rack)."""
    branches_el = find(el, "Branches")
    if branches_el is None:
        return []

    result = []
    for branch in branches_el:
        chain_name = value_str(branch, "Name")
        dc = find(branch, "DeviceChain")
        chain_devices = extract_devices(dc) if dc is not None else []
        result.append(RackChain(name=chain_name, devices=chain_devices))

    return result


def _extract_single_device(el: Element) -> Device | None:
    """Extract a single device from an XML element."""
    tag = el.tag
    dev_id = attr_int(el, "Id")

    device_type, plugin_name, vendor, category = _classify_device(tag, el)

    on_el = find(el, "On")
    is_on = value_bool(on_el, "Manual") if on_el is not None else None

    expanded_el = find(el, "IsExpanded")
    is_expanded = attr_bool(expanded_el) if expanded_el is not None else None

    rack_type = RACK_TAGS.get(tag)
    chains = _extract_rack_chains(el) if rack_type else []
    macros = _extract_macros(el) if rack_type else []
    params = _extract_params(el)

    # Determine display name
    name = plugin_name or tag

    return Device(
        id=dev_id,
        name=name,
        class_name=tag,
        is_on=is_on,
        is_expanded=is_expanded,
        device_type=device_type,
        plugin_name=plugin_name,
        plugin_vendor=vendor,
        plugin_category=category,
        rack_type=rack_type,
        chains=chains,
        macros=macros,
        parameters=params,
    )


def extract_devices(device_chain_el: Element | None) -> list[Device]:
    """Extract all devices from a DeviceChain element.

    Looks for the inner DeviceChain/Devices path used by tracks.
    """
    if device_chain_el is None:
        return []

    # Tracks have DeviceChain > DeviceChain > Devices
    # But also sometimes DeviceChain > Devices directly (e.g., rack chains)
    devices_el = find(device_chain_el, "Devices")
    if devices_el is None:
        inner_dc = find(device_chain_el, "DeviceChain")
        devices_el = find(inner_dc, "Devices") if inner_dc else None
    if devices_el is None:
        return []

    result = []
    for child in devices_el:
        try:
            dev = _extract_single_device(child)
            if dev is not None:
                result.append(dev)
        except Exception:
            logger.warning("Failed to parse device %s Id=%s", child.tag, child.attrib.get("Id"), exc_info=True)

    return result
