"""Domain dataclasses for ALS project data.

Every field is Optional or has a sensible default so that missing XML
elements produce None/empty rather than crashes.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_dict(d: dict) -> dict:
    """Recursively drop None values and empty lists for compact JSON."""
    cleaned = {}
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, list):
            if not v:
                continue
            cleaned[k] = [_clean_dict(i) if isinstance(i, dict) else i for i in v]
        elif isinstance(v, dict):
            sub = _clean_dict(v)
            if sub:
                cleaned[k] = sub
        else:
            cleaned[k] = v
    return cleaned


# ---------------------------------------------------------------------------
# Tier 1: Core
# ---------------------------------------------------------------------------

@dataclass
class VersionInfo:
    creator: Optional[str] = None
    major_version: Optional[str] = None
    minor_version: Optional[str] = None
    schema_change_count: Optional[str] = None

    def ableton_version(self) -> Optional[str]:
        """Extract version string like '11.3.13' from Creator."""
        if self.creator and "Ableton Live" in self.creator:
            return self.creator.split("Ableton Live ")[-1].strip()
        return None


@dataclass
class TimeSignature:
    numerator: int = 4
    denominator: int = 4
    time: float = 0.0


@dataclass
class TransportInfo:
    tempo: Optional[float] = None
    time_signature: Optional[TimeSignature] = None
    loop_on: Optional[bool] = None
    loop_start: Optional[float] = None
    loop_length: Optional[float] = None
    current_time: Optional[float] = None
    punch_in: Optional[bool] = None
    punch_out: Optional[bool] = None
    metronome_on: Optional[bool] = None


@dataclass
class Locator:
    id: Optional[int] = None
    time: Optional[float] = None
    name: Optional[str] = None
    annotation: Optional[str] = None
    is_song_start: Optional[bool] = None


@dataclass
class ScaleInfo:
    root_note: Optional[int] = None
    name: Optional[str] = None


# ---------------------------------------------------------------------------
# Tier 2: Arrangement
# ---------------------------------------------------------------------------

@dataclass
class MidiNote:
    pitch: Optional[int] = None
    time: Optional[float] = None
    duration: Optional[float] = None
    velocity: Optional[float] = None
    velocity_deviation: Optional[float] = None
    off_velocity: Optional[float] = None
    probability: Optional[float] = None
    is_enabled: Optional[bool] = None
    note_id: Optional[int] = None


@dataclass
class LoopSettings:
    loop_on: Optional[bool] = None
    loop_start: Optional[float] = None
    loop_end: Optional[float] = None
    start_relative: Optional[float] = None
    out_marker: Optional[float] = None


@dataclass
class FollowAction:
    follow_time: Optional[float] = None
    is_linked: Optional[bool] = None
    loop_iterations: Optional[int] = None
    enabled: Optional[bool] = None
    action_a: Optional[int] = None
    action_b: Optional[int] = None
    chance_a: Optional[int] = None
    chance_b: Optional[int] = None


@dataclass
class ClipEnvelopePoint:
    time: Optional[float] = None
    value: Optional[float] = None


@dataclass
class ClipEnvelope:
    pointee_id: Optional[int] = None
    points: list[ClipEnvelopePoint] = field(default_factory=list)


@dataclass
class MidiClip:
    id: Optional[int] = None
    name: Optional[str] = None
    color: Optional[int] = None
    time: Optional[float] = None
    start: Optional[float] = None
    end: Optional[float] = None
    loop: Optional[LoopSettings] = None
    notes: list[MidiNote] = field(default_factory=list)
    envelopes: list[ClipEnvelope] = field(default_factory=list)
    is_warped: Optional[bool] = None
    # Session-view extras
    launch_mode: Optional[int] = None
    launch_quantization: Optional[int] = None
    legato: Optional[bool] = None
    follow_action: Optional[FollowAction] = None

    @property
    def note_count(self) -> int:
        return len(self.notes)

    @property
    def duration(self) -> Optional[float]:
        if self.start is not None and self.end is not None:
            return self.end - self.start
        return None


@dataclass
class WarpMarker:
    sec_time: Optional[float] = None
    beat_time: Optional[float] = None


@dataclass
class SampleRef:
    relative_path: Optional[str] = None
    absolute_path: Optional[str] = None
    file_type: Optional[int] = None
    live_pack_name: Optional[str] = None
    default_duration: Optional[int] = None
    default_sample_rate: Optional[int] = None


@dataclass
class AudioClip:
    id: Optional[int] = None
    name: Optional[str] = None
    color: Optional[int] = None
    time: Optional[float] = None
    start: Optional[float] = None
    end: Optional[float] = None
    loop: Optional[LoopSettings] = None
    is_warped: Optional[bool] = None
    warp_mode: Optional[int] = None
    sample_ref: Optional[SampleRef] = None
    warp_markers: list[WarpMarker] = field(default_factory=list)
    gain: Optional[float] = None
    pitch_coarse: Optional[int] = None
    pitch_fine: Optional[int] = None

    @property
    def duration(self) -> Optional[float]:
        if self.start is not None and self.end is not None:
            return self.end - self.start
        return None

    @property
    def file_name(self) -> Optional[str]:
        if self.sample_ref and self.sample_ref.relative_path:
            return self.sample_ref.relative_path.split("/")[-1]
        return None


@dataclass
class ClipSlot:
    id: Optional[int] = None
    has_stop: Optional[bool] = None
    clip: Optional[MidiClip | AudioClip] = None


@dataclass
class Scene:
    id: Optional[int] = None
    name: Optional[str] = None
    color: Optional[int] = None
    tempo: Optional[float] = None
    time_signature_id: Optional[int] = None
    follow_action: Optional[FollowAction] = None


# ---------------------------------------------------------------------------
# Tier 3: Mix
# ---------------------------------------------------------------------------

@dataclass
class IORouting:
    target: Optional[str] = None
    upper_display_string: Optional[str] = None
    lower_display_string: Optional[str] = None


@dataclass
class SendInfo:
    value: Optional[float] = None
    active: Optional[bool] = None


@dataclass
class MixerInfo:
    volume: Optional[float] = None
    pan: Optional[float] = None
    sends: list[SendInfo] = field(default_factory=list)
    speaker: Optional[bool] = None
    solo: Optional[bool] = None
    cross_fade_state: Optional[int] = None


# ---------------------------------------------------------------------------
# Tier 4: Sound Design
# ---------------------------------------------------------------------------

@dataclass
class DeviceParameter:
    name: Optional[str] = None
    value: Optional[float | str] = None


@dataclass
class RackChain:
    name: Optional[str] = None
    devices: list[Device] = field(default_factory=list)


@dataclass
class MacroMapping:
    name: Optional[str] = None
    value: Optional[float] = None


@dataclass
class Device:
    id: Optional[int] = None
    name: Optional[str] = None
    class_name: Optional[str] = None  # XML tag name (e.g., "Eq8", "Compressor2")
    is_on: Optional[bool] = None
    is_expanded: Optional[bool] = None
    device_type: Optional[str] = None  # "native", "vst", "au", "max4live", "rack"
    plugin_name: Optional[str] = None
    plugin_vendor: Optional[str] = None
    plugin_category: Optional[str] = None
    rack_type: Optional[str] = None  # "instrument_rack", "effect_rack", "drum_rack"
    chains: list[RackChain] = field(default_factory=list)
    macros: list[MacroMapping] = field(default_factory=list)
    parameters: list[DeviceParameter] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Tier 5: Automation & Detail
# ---------------------------------------------------------------------------

@dataclass
class AutomationPoint:
    time: Optional[float] = None
    value: Optional[float] = None


@dataclass
class AutomationEnvelope:
    id: Optional[int] = None
    pointee_id: Optional[int] = None
    points: list[AutomationPoint] = field(default_factory=list)


@dataclass
class GrooveSettings:
    id: Optional[int] = None
    name: Optional[str] = None
    base: Optional[float] = None
    quantize: Optional[float] = None
    timing: Optional[float] = None
    random: Optional[float] = None
    velocity: Optional[float] = None


# ---------------------------------------------------------------------------
# Track (combines all tiers)
# ---------------------------------------------------------------------------

@dataclass
class Track:
    id: Optional[int] = None
    name: Optional[str] = None
    user_name: Optional[str] = None
    track_type: Optional[str] = None  # "midi", "audio", "return", "group", "master"
    color: Optional[int] = None
    index: Optional[int] = None
    group_id: Optional[int] = None
    is_frozen: Optional[bool] = None
    is_folded: Optional[bool] = None
    # Mix
    mixer: Optional[MixerInfo] = None
    audio_input_routing: Optional[IORouting] = None
    midi_input_routing: Optional[IORouting] = None
    audio_output_routing: Optional[IORouting] = None
    midi_output_routing: Optional[IORouting] = None
    # Arrangement clips
    midi_clips: list[MidiClip] = field(default_factory=list)
    audio_clips: list[AudioClip] = field(default_factory=list)
    # Session clip slots
    clip_slots: list[ClipSlot] = field(default_factory=list)
    # Devices
    devices: list[Device] = field(default_factory=list)
    # Automation
    automation_envelopes: list[AutomationEnvelope] = field(default_factory=list)

    @property
    def clips(self) -> list[MidiClip | AudioClip]:
        """All arrangement clips (MIDI + audio)."""
        return self.midi_clips + self.audio_clips

    @property
    def is_armed(self) -> Optional[bool]:
        # Arm state is stored differently; include for completeness
        return None

    @property
    def is_muted(self) -> Optional[bool]:
        if self.mixer and self.mixer.speaker is not None:
            return not self.mixer.speaker
        return None

    @property
    def is_solo(self) -> Optional[bool]:
        return self.mixer.solo if self.mixer else None


# ---------------------------------------------------------------------------
# Top-level Project
# ---------------------------------------------------------------------------

@dataclass
class ALSProject:
    file_path: Optional[str] = None
    version: Optional[VersionInfo] = None
    transport: Optional[TransportInfo] = None
    scale: Optional[ScaleInfo] = None
    tracks: list[Track] = field(default_factory=list)
    master_track: Optional[Track] = None
    return_tracks: list[Track] = field(default_factory=list)
    scenes: list[Scene] = field(default_factory=list)
    locators: list[Locator] = field(default_factory=list)
    grooves: list[GrooveSettings] = field(default_factory=list)

    # Convenience accessors
    @property
    def tempo(self) -> Optional[float]:
        return self.transport.tempo if self.transport else None

    @property
    def time_signature(self) -> Optional[TimeSignature]:
        return self.transport.time_signature if self.transport else None

    @property
    def markers(self) -> list[Locator]:
        return self.locators

    @property
    def midi_tracks(self) -> list[Track]:
        return [t for t in self.tracks if t.track_type == "midi"]

    @property
    def audio_tracks(self) -> list[Track]:
        return [t for t in self.tracks if t.track_type == "audio"]

    @property
    def group_tracks(self) -> list[Track]:
        return [t for t in self.tracks if t.track_type == "group"]

    @property
    def all_tracks(self) -> list[Track]:
        """All tracks including returns and master."""
        result = list(self.tracks)
        result.extend(self.return_tracks)
        if self.master_track:
            result.append(self.master_track)
        return result

    @property
    def track_count(self) -> int:
        return len(self.tracks)

    def to_dict(self) -> dict:
        """Convert to a dict suitable for JSON serialization."""
        return _clean_dict(asdict(self))

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string for LLM consumption."""
        return json.dumps(self.to_dict(), indent=indent)
