"""Write operations for .als files.

Core plumbing: decompress → modify ElementTree → recompress.
All mutations operate on the raw XML tree to preserve structure.
"""
from __future__ import annotations

import gzip
import logging
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

logger = logging.getLogger(__name__)


class ALSWriter:
    """Context for modifying an .als file.

    Usage:
        writer = ALSWriter("project.als")
        writer.set_track_volume("Bass", 0.7)
        writer.set_midi_velocities("Drums", velocity=100)
        writer.rename_track("3-Serum", "Lead Synth")
        writer.save()                    # overwrites original
        writer.save("project_v2.als")    # saves to new file
    """

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"ALS file not found: {self.file_path}")

        with gzip.open(self.file_path, "rb") as f:
            self._raw = f.read()

        self._root = ET.fromstring(self._raw)
        self._live_set = self._root.find("LiveSet")
        if self._live_set is None:
            raise ValueError("No LiveSet element found in ALS file")

        self._changes: list[str] = []

    @property
    def changes(self) -> list[str]:
        """List of changes made so far."""
        return list(self._changes)

    def save(self, output_path: str | Path | None = None, backup: bool = True) -> Path:
        """Save the modified .als file.

        Args:
            output_path: Where to save. If None, overwrites the original.
            backup: If overwriting original, create a .bak copy first.

        Returns:
            Path to the saved file.
        """
        out = Path(output_path) if output_path else self.file_path

        if backup and out == self.file_path:
            bak = self.file_path.with_suffix(".als.bak")
            shutil.copy2(self.file_path, bak)
            logger.info("Backup saved to %s", bak)

        xml_bytes = b'<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_bytes += ET.tostring(self._root, encoding="unicode").encode("utf-8")

        with gzip.open(out, "wb") as f:
            f.write(xml_bytes)

        logger.info("Saved %s (%d changes)", out, len(self._changes))
        return out

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find_tracks_el(self) -> ET.Element:
        tracks = self._live_set.find("Tracks")
        if tracks is None:
            raise ValueError("No Tracks element found")
        return tracks

    def _find_track_by_name(self, name: str) -> ET.Element | None:
        """Find a track element by its EffectiveName (case-insensitive)."""
        for track_el in self._find_tracks_el():
            name_el = track_el.find("Name")
            if name_el is not None:
                eff = name_el.find("EffectiveName")
                if eff is not None and eff.attrib.get("Value", "").lower() == name.lower():
                    return track_el
        # Also check master
        for tag in ("MasterTrack", "MainTrack"):
            master = self._live_set.find(tag)
            if master is not None:
                name_el = master.find("Name")
                if name_el is not None:
                    eff = name_el.find("EffectiveName")
                    if eff is not None and eff.attrib.get("Value", "").lower() == name.lower():
                        return master
        return None

    def _find_mixer(self, track_el: ET.Element) -> ET.Element | None:
        dc = track_el.find("DeviceChain")
        if dc is None:
            return None
        return dc.find("Mixer")

    def _get_all_midi_clips(self, track_el: ET.Element) -> list[ET.Element]:
        """Find all MidiClip elements in a track (arrangement + session)."""
        clips = []
        dc = track_el.find("DeviceChain")
        if dc is None:
            return clips

        # Arrangement clips
        seq = dc.find("MainSequencer")
        if seq is not None:
            for container_tag in ("ClipTimeable", "Sample"):
                ct = seq.find(container_tag)
                if ct is not None:
                    aa = ct.find("ArrangerAutomation")
                    if aa is not None:
                        events = aa.find("Events")
                        if events is not None:
                            for child in events:
                                if child.tag == "MidiClip":
                                    clips.append(child)

        return clips

    def _list_track_names(self) -> list[str]:
        """List all track names for error messages."""
        names = []
        for track_el in self._find_tracks_el():
            name_el = track_el.find("Name")
            if name_el is not None:
                eff = name_el.find("EffectiveName")
                if eff is not None:
                    names.append(eff.attrib.get("Value", ""))
        return names

    # ------------------------------------------------------------------
    # Track renaming
    # ------------------------------------------------------------------

    def rename_track(self, old_name: str, new_name: str) -> bool:
        """Rename a track.

        Updates both EffectiveName and UserName.

        Returns:
            True if track was found and renamed.
        """
        track_el = self._find_track_by_name(old_name)
        if track_el is None:
            logger.warning("Track '%s' not found. Available: %s", old_name, self._list_track_names())
            return False

        name_el = track_el.find("Name")
        if name_el is None:
            return False

        eff = name_el.find("EffectiveName")
        user = name_el.find("UserName")
        if eff is not None:
            eff.set("Value", new_name)
        if user is not None:
            user.set("Value", new_name)

        self._changes.append(f"rename: '{old_name}' → '{new_name}'")
        return True

    # ------------------------------------------------------------------
    # Mixer adjustments
    # ------------------------------------------------------------------

    def set_track_volume(self, track_name: str, volume: float) -> bool:
        """Set a track's volume (linear scale, 0.0 to ~1.99).

        Ableton uses linear volume where 1.0 ≈ 0dB, 0.0 = -inf, ~1.99 ≈ +6dB.

        Returns:
            True if track was found and volume set.
        """
        track_el = self._find_track_by_name(track_name)
        if track_el is None:
            logger.warning("Track '%s' not found", track_name)
            return False

        mixer = self._find_mixer(track_el)
        if mixer is None:
            logger.warning("No mixer found on track '%s'", track_name)
            return False

        vol_el = mixer.find("Volume")
        if vol_el is None:
            return False
        manual = vol_el.find("Manual")
        if manual is None:
            return False

        old_val = manual.attrib.get("Value", "?")
        manual.set("Value", str(volume))
        self._changes.append(f"volume: '{track_name}' {old_val} → {volume}")
        return True

    def set_track_pan(self, track_name: str, pan: float) -> bool:
        """Set a track's pan position (-1.0 = full left, 0 = center, 1.0 = full right).

        Returns:
            True if track was found and pan set.
        """
        track_el = self._find_track_by_name(track_name)
        if track_el is None:
            logger.warning("Track '%s' not found", track_name)
            return False

        mixer = self._find_mixer(track_el)
        if mixer is None:
            return False

        pan_el = mixer.find("Pan")
        if pan_el is None:
            return False
        manual = pan_el.find("Manual")
        if manual is None:
            return False

        old_val = manual.attrib.get("Value", "?")
        manual.set("Value", str(pan))
        self._changes.append(f"pan: '{track_name}' {old_val} → {pan}")
        return True

    # ------------------------------------------------------------------
    # MIDI velocity editing
    # ------------------------------------------------------------------

    def set_midi_velocities(
        self,
        track_name: str,
        velocity: float | None = None,
        scale: float | None = None,
        min_vel: float = 1,
        max_vel: float = 127,
        clip_index: int | None = None,
    ) -> int:
        """Modify MIDI note velocities on a track.

        Exactly one of `velocity` or `scale` must be provided:
        - velocity: Set all notes to this fixed velocity.
        - scale: Multiply existing velocities by this factor (e.g., 0.8 for softer).

        Args:
            track_name: Track name (case-insensitive).
            velocity: Fixed velocity to set (1-127).
            scale: Multiplier for existing velocities.
            min_vel: Floor for velocity values after scaling.
            max_vel: Ceiling for velocity values after scaling.
            clip_index: If set, only modify this arrangement clip (0-indexed).
                If None, modify all clips on the track.

        Returns:
            Number of notes modified.
        """
        if velocity is None and scale is None:
            raise ValueError("Must provide either velocity or scale")
        if velocity is not None and scale is not None:
            raise ValueError("Provide velocity or scale, not both")

        track_el = self._find_track_by_name(track_name)
        if track_el is None:
            logger.warning("Track '%s' not found", track_name)
            return 0

        clips = self._get_all_midi_clips(track_el)
        if clip_index is not None:
            if clip_index >= len(clips):
                logger.warning("Clip index %d out of range (track has %d clips)", clip_index, len(clips))
                return 0
            clips = [clips[clip_index]]

        modified = 0
        for clip_el in clips:
            notes_el = clip_el.find("Notes")
            if notes_el is None:
                continue
            key_tracks = notes_el.find("KeyTracks")
            if key_tracks is None:
                continue

            for kt in key_tracks.findall("KeyTrack"):
                notes_container = kt.find("Notes")
                if notes_container is None:
                    continue
                for note in notes_container.findall("MidiNoteEvent"):
                    if velocity is not None:
                        note.set("Velocity", str(velocity))
                    elif scale is not None:
                        old_vel = float(note.attrib.get("Velocity", "100"))
                        new_vel = max(min_vel, min(max_vel, old_vel * scale))
                        note.set("Velocity", str(round(new_vel, 6)))
                    modified += 1

        if modified > 0:
            if velocity is not None:
                self._changes.append(f"velocity: '{track_name}' → {velocity} ({modified} notes)")
            else:
                self._changes.append(f"velocity: '{track_name}' ×{scale} ({modified} notes)")

        return modified

    def humanize_velocities(
        self,
        track_name: str,
        amount: float = 15,
        clip_index: int | None = None,
    ) -> int:
        """Add deterministic velocity variation to MIDI notes.

        Uses a simple hash-based approach (not random) so the result is
        reproducible. Alternating notes get pushed up/down by `amount`.

        Args:
            track_name: Track name.
            amount: Max velocity deviation in each direction (default: 15).
            clip_index: If set, only modify this clip.

        Returns:
            Number of notes modified.
        """
        track_el = self._find_track_by_name(track_name)
        if track_el is None:
            logger.warning("Track '%s' not found", track_name)
            return 0

        clips = self._get_all_midi_clips(track_el)
        if clip_index is not None:
            if clip_index >= len(clips):
                return 0
            clips = [clips[clip_index]]

        modified = 0
        for clip_el in clips:
            notes_el = clip_el.find("Notes")
            if notes_el is None:
                continue
            key_tracks = notes_el.find("KeyTracks")
            if key_tracks is None:
                continue

            note_idx = 0
            for kt in key_tracks.findall("KeyTrack"):
                notes_container = kt.find("Notes")
                if notes_container is None:
                    continue
                for note in notes_container.findall("MidiNoteEvent"):
                    old_vel = float(note.attrib.get("Velocity", "100"))
                    # Deterministic variation based on note position
                    time = float(note.attrib.get("Time", "0"))
                    # Simple pattern: use fractional part of time to create variation
                    offset = amount * (((hash((note_idx, int(time * 1000))) % 200) - 100) / 100)
                    new_vel = max(1, min(127, old_vel + offset))
                    note.set("Velocity", str(round(new_vel, 6)))
                    note_idx += 1
                    modified += 1

        if modified > 0:
            self._changes.append(f"humanize: '{track_name}' ±{amount} ({modified} notes)")
        return modified

    # ------------------------------------------------------------------
    # Tempo
    # ------------------------------------------------------------------

    def set_tempo(self, bpm: float) -> bool:
        """Set the project tempo.

        Returns:
            True if tempo was successfully set.
        """
        for tag in ("MasterTrack", "MainTrack"):
            master = self._live_set.find(tag)
            if master is not None:
                dc = master.find("DeviceChain")
                if dc is None:
                    continue
                mixer = dc.find("Mixer")
                if mixer is None:
                    continue
                tempo_el = mixer.find("Tempo")
                if tempo_el is None:
                    continue
                manual = tempo_el.find("Manual")
                if manual is None:
                    continue
                old_val = manual.attrib.get("Value", "?")
                manual.set("Value", str(bpm))
                self._changes.append(f"tempo: {old_val} → {bpm}")
                return True
        return False
