"""Tests for als_reader — validates all 5 extraction tiers against the test fixture."""
from __future__ import annotations

import json
import os
import sys
import unittest

# Ensure the package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import als_reader
from als_reader.models import ALSProject


FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "test_project.als")


class TestFixtureExists(unittest.TestCase):
    def test_fixture_file_exists(self):
        self.assertTrue(os.path.exists(FIXTURE_PATH), "Run tests/create_fixture.py first")


class TestLoad(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = als_reader.load(FIXTURE_PATH)

    def test_returns_als_project(self):
        self.assertIsInstance(self.project, ALSProject)

    def test_file_path_stored(self):
        self.assertEqual(self.project.file_path, FIXTURE_PATH)


# ---------------------------------------------------------------------------
# Tier 1: Core
# ---------------------------------------------------------------------------

class TestTier1Version(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = als_reader.load(FIXTURE_PATH)

    def test_creator(self):
        self.assertEqual(self.project.version.creator, "Ableton Live 11.3.13")

    def test_ableton_version(self):
        self.assertEqual(self.project.version.ableton_version(), "11.3.13")

    def test_major_version(self):
        self.assertEqual(self.project.version.major_version, "5")


class TestTier1Transport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = als_reader.load(FIXTURE_PATH)

    def test_tempo(self):
        self.assertEqual(self.project.tempo, 128.0)

    def test_time_signature(self):
        ts = self.project.time_signature
        self.assertIsNotNone(ts)
        self.assertEqual(ts.numerator, 4)
        self.assertEqual(ts.denominator, 4)

    def test_loop_on(self):
        self.assertTrue(self.project.transport.loop_on)

    def test_loop_length(self):
        self.assertEqual(self.project.transport.loop_length, 16.0)

    def test_current_time(self):
        self.assertEqual(self.project.transport.current_time, 4.5)


class TestTier1Tracks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = als_reader.load(FIXTURE_PATH)

    def test_track_count(self):
        # 2 MIDI + 1 Audio + 1 Group = 4 main tracks
        self.assertEqual(self.project.track_count, 4)

    def test_return_track_count(self):
        self.assertEqual(len(self.project.return_tracks), 2)

    def test_master_track_exists(self):
        self.assertIsNotNone(self.project.master_track)
        self.assertEqual(self.project.master_track.track_type, "master")

    def test_track_types(self):
        types = [t.track_type for t in self.project.tracks]
        self.assertEqual(types, ["midi", "audio", "group", "midi"])

    def test_track_names(self):
        names = [t.name for t in self.project.tracks]
        self.assertEqual(names, ["Bass Synth", "Drums", "Music Group", "Lead"])

    def test_track_colors(self):
        colors = [t.color for t in self.project.tracks]
        self.assertEqual(colors, [13, 21, 5, 7])

    def test_group_membership(self):
        lead = self.project.tracks[3]
        self.assertEqual(lead.group_id, 3)

    def test_frozen_state(self):
        bass = self.project.tracks[0]
        self.assertFalse(bass.is_frozen)

    def test_midi_tracks_convenience(self):
        self.assertEqual(len(self.project.midi_tracks), 2)

    def test_audio_tracks_convenience(self):
        self.assertEqual(len(self.project.audio_tracks), 1)

    def test_group_tracks_convenience(self):
        self.assertEqual(len(self.project.group_tracks), 1)


class TestTier1Locators(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = als_reader.load(FIXTURE_PATH)

    def test_locator_count(self):
        self.assertEqual(len(self.project.locators), 3)

    def test_locator_names(self):
        names = [l.name for l in self.project.locators]
        self.assertEqual(names, ["Intro", "Build", "Drop"])

    def test_locator_times(self):
        times = [l.time for l in self.project.locators]
        self.assertEqual(times, [0.0, 8.0, 16.0])

    def test_song_start(self):
        self.assertTrue(self.project.locators[0].is_song_start)


class TestTier1Scale(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = als_reader.load(FIXTURE_PATH)

    def test_scale_info(self):
        self.assertIsNotNone(self.project.scale)
        self.assertEqual(self.project.scale.root_note, 0)
        self.assertEqual(self.project.scale.name, "Major")


# ---------------------------------------------------------------------------
# Tier 2: Arrangement
# ---------------------------------------------------------------------------

class TestTier2MidiClips(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = als_reader.load(FIXTURE_PATH)
        cls.bass = cls.project.tracks[0]

    def test_midi_clip_count(self):
        self.assertEqual(len(self.bass.midi_clips), 2)

    def test_clip_names(self):
        names = [c.name for c in self.bass.midi_clips]
        self.assertEqual(names, ["Bass Pattern", "Bass Fill"])

    def test_clip_positions(self):
        times = [c.time for c in self.bass.midi_clips]
        self.assertEqual(times, [0.0, 4.0])

    def test_clip_duration(self):
        self.assertEqual(self.bass.midi_clips[0].duration, 4.0)

    def test_note_count(self):
        self.assertEqual(self.bass.midi_clips[0].note_count, 5)

    def test_note_pitch(self):
        notes = self.bass.midi_clips[0].notes
        pitches = sorted(set(n.pitch for n in notes))
        self.assertEqual(pitches, [36, 48])

    def test_note_velocity(self):
        first_note = self.bass.midi_clips[0].notes[0]
        self.assertEqual(first_note.velocity, 100.0)

    def test_note_probability(self):
        # Third note on key 36 has probability 0.75
        notes_36 = [n for n in self.bass.midi_clips[0].notes if n.pitch == 36]
        self.assertEqual(notes_36[2].probability, 0.75)

    def test_loop_settings(self):
        loop = self.bass.midi_clips[0].loop
        self.assertIsNotNone(loop)
        self.assertTrue(loop.loop_on)
        self.assertEqual(loop.loop_end, 4.0)

    def test_clip_envelopes(self):
        envs = self.bass.midi_clips[0].envelopes
        self.assertEqual(len(envs), 1)
        self.assertEqual(envs[0].pointee_id, 100)
        self.assertEqual(len(envs[0].points), 2)


class TestTier2AudioClips(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = als_reader.load(FIXTURE_PATH)
        cls.drums = cls.project.tracks[1]

    def test_audio_clip_count(self):
        self.assertEqual(len(self.drums.audio_clips), 1)

    def test_clip_name(self):
        self.assertEqual(self.drums.audio_clips[0].name, "Break_120bpm")

    def test_sample_ref(self):
        sr = self.drums.audio_clips[0].sample_ref
        self.assertIsNotNone(sr)
        self.assertIn("Break_120bpm.wav", sr.relative_path)
        self.assertEqual(sr.default_sample_rate, 44100)

    def test_file_name(self):
        self.assertEqual(self.drums.audio_clips[0].file_name, "Break_120bpm.wav")

    def test_warp_mode(self):
        self.assertEqual(self.drums.audio_clips[0].warp_mode, 3)

    def test_warp_markers(self):
        wms = self.drums.audio_clips[0].warp_markers
        self.assertEqual(len(wms), 2)
        self.assertEqual(wms[0].sec_time, 0.0)
        self.assertEqual(wms[1].beat_time, 8.0)

    def test_gain(self):
        self.assertEqual(self.drums.audio_clips[0].gain, 1.0)


class TestTier2ClipSlots(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = als_reader.load(FIXTURE_PATH)
        cls.bass = cls.project.tracks[0]

    def test_clip_slot_count(self):
        self.assertEqual(len(self.bass.clip_slots), 2)

    def test_first_slot_has_clip(self):
        self.assertIsNotNone(self.bass.clip_slots[0].clip)
        self.assertEqual(self.bass.clip_slots[0].clip.name, "Session Bass")

    def test_second_slot_empty(self):
        self.assertIsNone(self.bass.clip_slots[1].clip)

    def test_follow_action(self):
        clip = self.bass.clip_slots[0].clip
        self.assertIsNotNone(clip.follow_action)
        self.assertTrue(clip.follow_action.enabled)
        self.assertEqual(clip.follow_action.follow_time, 4.0)


class TestTier2Scenes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = als_reader.load(FIXTURE_PATH)

    def test_scene_count(self):
        self.assertEqual(len(self.project.scenes), 2)

    def test_scene_names(self):
        names = [s.name for s in self.project.scenes]
        self.assertEqual(names, ["Intro", "Drop"])

    def test_scene_tempo(self):
        # Intro has no tempo (-1 → None), Drop has 130
        self.assertIsNone(self.project.scenes[0].tempo)
        self.assertEqual(self.project.scenes[1].tempo, 130.0)


# ---------------------------------------------------------------------------
# Tier 3: Mix
# ---------------------------------------------------------------------------

class TestTier3Mixer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = als_reader.load(FIXTURE_PATH)

    def test_volume(self):
        bass = self.project.tracks[0]
        self.assertEqual(bass.mixer.volume, 0.85)

    def test_pan(self):
        bass = self.project.tracks[0]
        self.assertEqual(bass.mixer.pan, -0.1)

    def test_sends(self):
        bass = self.project.tracks[0]
        self.assertEqual(len(bass.mixer.sends), 2)
        self.assertEqual(bass.mixer.sends[0].value, 0.5)
        self.assertEqual(bass.mixer.sends[1].value, 0.2)

    def test_solo(self):
        lead = self.project.tracks[3]
        self.assertTrue(lead.mixer.solo)
        self.assertTrue(lead.is_solo)

    def test_muted(self):
        bass = self.project.tracks[0]
        self.assertFalse(bass.is_muted)  # speaker=true → not muted

    def test_master_volume(self):
        self.assertEqual(self.project.master_track.mixer.volume, 0.7)


class TestTier3Routing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = als_reader.load(FIXTURE_PATH)

    def test_audio_output(self):
        bass = self.project.tracks[0]
        self.assertIsNotNone(bass.audio_output_routing)
        self.assertEqual(bass.audio_output_routing.target, "AudioOut/Master")

    def test_midi_input(self):
        bass = self.project.tracks[0]
        self.assertIsNotNone(bass.midi_input_routing)
        self.assertIn("External", bass.midi_input_routing.target)

    def test_group_routing(self):
        lead = self.project.tracks[3]
        self.assertIsNotNone(lead.audio_output_routing)
        self.assertIn("GroupTrack", lead.audio_output_routing.target)


# ---------------------------------------------------------------------------
# Tier 4: Sound Design
# ---------------------------------------------------------------------------

class TestTier4Devices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = als_reader.load(FIXTURE_PATH)
        cls.bass = cls.project.tracks[0]
        cls.drums = cls.project.tracks[1]

    def test_device_count(self):
        self.assertEqual(len(self.bass.devices), 4)

    def test_native_device(self):
        eq = self.bass.devices[1]
        self.assertEqual(eq.class_name, "Eq8")
        self.assertEqual(eq.device_type, "native")
        self.assertTrue(eq.is_on)

    def test_device_off(self):
        comp = self.bass.devices[2]
        self.assertEqual(comp.class_name, "Compressor2")
        self.assertFalse(comp.is_on)

    def test_vst_plugin(self):
        serum = self.bass.devices[3]
        self.assertEqual(serum.device_type, "vst")
        self.assertEqual(serum.plugin_name, "Serum")
        self.assertEqual(serum.plugin_vendor, "Xfer Records")

    def test_au_plugin(self):
        proq = self.drums.devices[2]
        self.assertEqual(proq.device_type, "au")
        self.assertEqual(proq.plugin_name, "FabFilter Pro-Q 3")
        self.assertEqual(proq.plugin_vendor, "FabFilter")

    def test_effect_rack(self):
        rack = self.drums.devices[1]
        self.assertEqual(rack.rack_type, "effect_rack")
        self.assertEqual(len(rack.chains), 1)
        self.assertEqual(rack.chains[0].name, "Chain A")

    def test_rack_chain_devices(self):
        rack = self.drums.devices[1]
        chain_devs = rack.chains[0].devices
        self.assertEqual(len(chain_devs), 1)
        self.assertEqual(chain_devs[0].class_name, "Compressor2")

    def test_rack_macros(self):
        rack = self.drums.devices[1]
        self.assertEqual(len(rack.macros), 2)
        self.assertEqual(rack.macros[0].name, "Macro 1")
        self.assertEqual(rack.macros[0].value, 64.0)

    def test_instrument_rack(self):
        lead = self.project.tracks[3]
        self.assertEqual(len(lead.devices), 1)
        ir = lead.devices[0]
        self.assertEqual(ir.rack_type, "instrument_rack")
        self.assertEqual(len(ir.chains), 2)

    def test_instrument_rack_nested_plugin(self):
        lead = self.project.tracks[3]
        ir = lead.devices[0]
        pluck = ir.chains[1]
        self.assertEqual(pluck.name, "Pluck Layer")
        self.assertEqual(len(pluck.devices), 1)
        self.assertEqual(pluck.devices[0].plugin_name, "Vital")

    def test_device_parameters(self):
        comp = self.bass.devices[2]
        param_names = [p.name for p in comp.parameters]
        self.assertIn("Threshold", param_names)
        self.assertIn("Ratio", param_names)
        threshold = next(p for p in comp.parameters if p.name == "Threshold")
        self.assertEqual(threshold.value, -20.0)

    def test_return_track_devices(self):
        reverb_track = self.project.return_tracks[0]
        self.assertEqual(len(reverb_track.devices), 1)
        self.assertEqual(reverb_track.devices[0].class_name, "Reverb")

    def test_master_track_devices(self):
        self.assertEqual(len(self.project.master_track.devices), 1)
        self.assertEqual(self.project.master_track.devices[0].class_name, "Limiter")


# ---------------------------------------------------------------------------
# Tier 5: Automation & Detail
# ---------------------------------------------------------------------------

class TestTier5Automation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = als_reader.load(FIXTURE_PATH)

    def test_track_automation(self):
        bass = self.project.tracks[0]
        self.assertEqual(len(bass.automation_envelopes), 1)
        env = bass.automation_envelopes[0]
        self.assertEqual(env.pointee_id, 100)
        self.assertEqual(len(env.points), 3)

    def test_automation_values(self):
        bass = self.project.tracks[0]
        env = bass.automation_envelopes[0]
        self.assertEqual(env.points[0].value, 0.85)
        self.assertEqual(env.points[1].time, 4.0)

    def test_master_automation(self):
        master = self.project.master_track
        self.assertEqual(len(master.automation_envelopes), 1)
        env = master.automation_envelopes[0]
        self.assertEqual(len(env.points), 3)


class TestTier5Grooves(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = als_reader.load(FIXTURE_PATH)

    def test_groove_count(self):
        self.assertEqual(len(self.project.grooves), 1)

    def test_groove_name(self):
        self.assertEqual(self.project.grooves[0].name, "MPC 16 Swing-62")

    def test_groove_params(self):
        g = self.project.grooves[0]
        self.assertEqual(g.timing, 0.8)
        self.assertEqual(g.quantize, 0.5)


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

class TestSerialization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = als_reader.load(FIXTURE_PATH)

    def test_to_dict(self):
        d = self.project.to_dict()
        self.assertIsInstance(d, dict)
        self.assertIn("tracks", d)
        self.assertIn("transport", d)

    def test_to_json(self):
        j = self.project.to_json()
        parsed = json.loads(j)
        self.assertIsInstance(parsed, dict)

    def test_json_roundtrip_track_count(self):
        j = self.project.to_json()
        parsed = json.loads(j)
        self.assertEqual(len(parsed["tracks"]), 4)

    def test_json_no_none_values(self):
        j = self.project.to_json()
        # The _clean_dict should strip None values
        self.assertNotIn('"null"', j)


if __name__ == "__main__":
    unittest.main()
