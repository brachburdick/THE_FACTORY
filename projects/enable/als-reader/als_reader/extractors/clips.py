"""Extract MIDI clips, audio clips, clip slots, and their contents."""
from __future__ import annotations

import logging
from xml.etree.ElementTree import Element

from ..models import (
    MidiClip, MidiNote, AudioClip, LoopSettings, WarpMarker, SampleRef,
    ClipSlot, FollowAction, ClipEnvelope, ClipEnvelopePoint,
)
from ._xml_helpers import (
    find, find_all, attr, attr_float, attr_int, attr_bool,
    value_float, value_int, value_str, value_bool,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Loop settings
# ---------------------------------------------------------------------------

def _extract_loop(clip_el: Element) -> LoopSettings | None:
    loop_el = find(clip_el, "Loop")
    if loop_el is None:
        return None
    return LoopSettings(
        loop_on=value_bool(loop_el, "LoopOn"),
        loop_start=value_float(loop_el, "LoopStart"),
        loop_end=value_float(loop_el, "LoopEnd"),
        start_relative=value_float(loop_el, "StartRelative"),
        out_marker=value_float(loop_el, "OutMarker"),
    )


# ---------------------------------------------------------------------------
# Follow actions
# ---------------------------------------------------------------------------

def _extract_follow_action(parent: Element) -> FollowAction | None:
    fa_el = find(parent, "FollowAction")
    if fa_el is None:
        return None
    return FollowAction(
        follow_time=value_float(fa_el, "FollowTime"),
        is_linked=value_bool(fa_el, "IsLinked"),
        loop_iterations=value_int(fa_el, "LoopIterations"),
        enabled=value_bool(fa_el, "FollowActionEnabled"),
        action_a=value_int(fa_el, "FollowActionA"),
        action_b=value_int(fa_el, "FollowActionB"),
        chance_a=value_int(fa_el, "FollowChanceA"),
        chance_b=value_int(fa_el, "FollowChanceB"),
    )


# ---------------------------------------------------------------------------
# Clip envelopes
# ---------------------------------------------------------------------------

def _extract_clip_envelopes(clip_el: Element) -> list[ClipEnvelope]:
    """Extract clip-level automation envelopes."""
    envelopes_wrapper = find(clip_el, "Envelopes")
    if envelopes_wrapper is None:
        return []
    envelopes_inner = find(envelopes_wrapper, "Envelopes")
    if envelopes_inner is None:
        return []

    result = []
    for env_el in find_all(envelopes_inner, "ClipEnvelope"):
        target = find(env_el, "EnvelopeTarget")
        pointee_id = value_int(target, "PointeeId") if target is not None else None

        points = []
        automation = find(env_el, "Automation")
        events = find(automation, "Events") if automation is not None else None
        if events is not None:
            for evt in find_all(events, "AutomationEvent"):
                points.append(ClipEnvelopePoint(
                    time=attr_float(evt, "Time"),
                    value=attr_float(evt, "Value"),
                ))

        result.append(ClipEnvelope(pointee_id=pointee_id, points=points))
    return result


# ---------------------------------------------------------------------------
# MIDI notes
# ---------------------------------------------------------------------------

def _extract_midi_notes(clip_el: Element) -> list[MidiNote]:
    """Extract all MIDI notes from a clip's KeyTracks."""
    notes_el = find(clip_el, "Notes")
    if notes_el is None:
        return []
    key_tracks = find(notes_el, "KeyTracks")
    if key_tracks is None:
        return []

    result = []
    for kt in find_all(key_tracks, "KeyTrack"):
        midi_key = value_int(kt, "MidiKey")
        notes_container = find(kt, "Notes")
        if notes_container is None:
            continue
        for note_el in find_all(notes_container, "MidiNoteEvent"):
            result.append(MidiNote(
                pitch=midi_key,
                time=attr_float(note_el, "Time"),
                duration=attr_float(note_el, "Duration"),
                velocity=attr_float(note_el, "Velocity"),
                velocity_deviation=attr_float(note_el, "VelocityDeviation"),
                off_velocity=attr_float(note_el, "OffVelocity"),
                probability=attr_float(note_el, "Probability"),
                is_enabled=attr_bool(note_el, "IsEnabled"),
                note_id=attr_int(note_el, "NoteId"),
            ))

    # Sort by time then pitch
    result.sort(key=lambda n: (n.time or 0, n.pitch or 0))
    return result


# ---------------------------------------------------------------------------
# MIDI clips
# ---------------------------------------------------------------------------

def _extract_midi_clip(clip_el: Element) -> MidiClip:
    return MidiClip(
        id=attr_int(clip_el, "Id"),
        name=value_str(clip_el, "Name") or attr(clip_el, "Name"),
        color=value_int(clip_el, "Color"),
        time=attr_float(clip_el, "Time"),
        start=value_float(clip_el, "CurrentStart"),
        end=value_float(clip_el, "CurrentEnd"),
        loop=_extract_loop(clip_el),
        notes=_extract_midi_notes(clip_el),
        envelopes=_extract_clip_envelopes(clip_el),
        is_warped=value_bool(clip_el, "IsWarped"),
        launch_mode=value_int(clip_el, "LaunchMode"),
        launch_quantization=value_int(clip_el, "LaunchQuantization"),
        legato=value_bool(clip_el, "Legato"),
        follow_action=_extract_follow_action(clip_el),
    )


# ---------------------------------------------------------------------------
# Audio clips
# ---------------------------------------------------------------------------

def _extract_sample_ref(clip_el: Element) -> SampleRef | None:
    sr_el = find(clip_el, "SampleRef")
    if sr_el is None:
        return None
    file_ref = find(sr_el, "FileRef")
    if file_ref is None:
        return None
    return SampleRef(
        relative_path=value_str(file_ref, "RelativePath"),
        absolute_path=value_str(file_ref, "Path"),
        file_type=value_int(file_ref, "Type"),
        live_pack_name=value_str(file_ref, "LivePackName"),
        default_duration=value_int(sr_el, "DefaultDuration"),
        default_sample_rate=value_int(sr_el, "DefaultSampleRate"),
    )


def _extract_warp_markers(clip_el: Element) -> list[WarpMarker]:
    wm_el = find(clip_el, "WarpMarkers")
    if wm_el is None:
        return []
    result = []
    for wm in find_all(wm_el, "WarpMarker"):
        result.append(WarpMarker(
            sec_time=attr_float(wm, "SecTime"),
            beat_time=attr_float(wm, "BeatTime"),
        ))
    return result


def _extract_audio_clip(clip_el: Element) -> AudioClip:
    return AudioClip(
        id=attr_int(clip_el, "Id"),
        name=value_str(clip_el, "Name") or attr(clip_el, "Name"),
        color=value_int(clip_el, "Color"),
        time=attr_float(clip_el, "Time"),
        start=value_float(clip_el, "CurrentStart"),
        end=value_float(clip_el, "CurrentEnd"),
        loop=_extract_loop(clip_el),
        is_warped=value_bool(clip_el, "IsWarped"),
        warp_mode=value_int(clip_el, "WarpMode"),
        sample_ref=_extract_sample_ref(clip_el),
        warp_markers=_extract_warp_markers(clip_el),
        gain=value_float(clip_el, "Gain"),
        pitch_coarse=value_int(clip_el, "PitchCoarse"),
        pitch_fine=value_int(clip_el, "PitchFine"),
    )


# ---------------------------------------------------------------------------
# Arrangement clips from a sequencer
# ---------------------------------------------------------------------------

def extract_arrangement_clips(device_chain_el: Element) -> tuple[list[MidiClip], list[AudioClip]]:
    """Extract arrangement-view clips from a track's MainSequencer."""
    midi_clips: list[MidiClip] = []
    audio_clips: list[AudioClip] = []

    seq = find(device_chain_el, "MainSequencer")
    if seq is None:
        return midi_clips, audio_clips

    ct = find(seq, "ClipTimeable")
    if ct is None:
        ct = find(seq, "Sample")
    aa = find(ct, "ArrangerAutomation") if ct is not None else None
    events = find(aa, "Events") if aa is not None else None
    if events is None:
        return midi_clips, audio_clips

    for child in events:
        try:
            if child.tag == "MidiClip":
                midi_clips.append(_extract_midi_clip(child))
            elif child.tag == "AudioClip":
                audio_clips.append(_extract_audio_clip(child))
            else:
                logger.debug("Unknown clip type in arrangement: %s", child.tag)
        except Exception:
            logger.warning("Failed to parse %s clip Id=%s", child.tag, child.attrib.get("Id"), exc_info=True)

    return midi_clips, audio_clips


# ---------------------------------------------------------------------------
# Session clip slots
# ---------------------------------------------------------------------------

def extract_clip_slots(device_chain_el: Element) -> list[ClipSlot]:
    """Extract session-view clip slots from a track's MainSequencer."""
    seq = find(device_chain_el, "MainSequencer")
    if seq is None:
        return []

    slot_list = find(seq, "ClipSlotList")
    if slot_list is None:
        return []

    result = []
    for slot_el in find_all(slot_list, "ClipSlot"):
        slot_id = attr_int(slot_el, "Id")
        inner = find(slot_el, "ClipSlot")
        if inner is None:
            result.append(ClipSlot(id=slot_id))
            continue

        has_stop = value_bool(inner, "HasStop")

        # Check for clip inside Value element
        clip = None
        value_el = find(inner, "Value")
        if value_el is not None:
            midi_el = find(value_el, "MidiClip")
            audio_el = find(value_el, "AudioClip")
            try:
                if midi_el is not None:
                    clip = _extract_midi_clip(midi_el)
                elif audio_el is not None:
                    clip = _extract_audio_clip(audio_el)
            except Exception:
                logger.warning("Failed to parse session clip in slot %s", slot_id, exc_info=True)

        result.append(ClipSlot(id=slot_id, has_stop=has_stop, clip=clip))

    return result
