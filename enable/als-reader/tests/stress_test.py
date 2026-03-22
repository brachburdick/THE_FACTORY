"""Parse every .als file in a directory tree, report failures and stats."""
from __future__ import annotations

import os
import sys
import time
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import als_reader

PROJECTS_DIR = "/Users/brach/Documents/Ableton Projects/Onset Analysis/Projects V2"


def find_als_files(root: str, skip_backups: bool = True) -> list[str]:
    result = []
    for dirpath, _, filenames in os.walk(root):
        if skip_backups and "Backup" in dirpath:
            continue
        for f in filenames:
            if f.endswith(".als"):
                result.append(os.path.join(dirpath, f))
    result.sort()
    return result


def main():
    files = find_als_files(PROJECTS_DIR)
    print(f"Found {len(files)} .als files\n")

    passed = 0
    failed = 0
    warnings = []
    stats = []

    for path in files:
        name = os.path.basename(path)
        try:
            t0 = time.monotonic()
            project = als_reader.load(path)
            elapsed = time.monotonic() - t0

            # Validate we got something useful
            n_tracks = project.track_count
            n_returns = len(project.return_tracks)
            tempo = project.tempo
            version = project.version.ableton_version() if project.version else "?"

            # Count clips and devices across all tracks
            n_midi_clips = sum(len(t.midi_clips) for t in project.tracks)
            n_audio_clips = sum(len(t.audio_clips) for t in project.tracks)
            n_devices = sum(len(t.devices) for t in project.all_tracks)
            n_notes = sum(
                sum(c.note_count for c in t.midi_clips)
                for t in project.tracks
            )
            n_automation = sum(len(t.automation_envelopes) for t in project.all_tracks)

            # Check JSON serialization works
            json_str = project.to_json(indent=None)
            json_size = len(json_str)

            stats.append({
                "name": name,
                "version": version,
                "tracks": n_tracks,
                "returns": n_returns,
                "midi_clips": n_midi_clips,
                "audio_clips": n_audio_clips,
                "notes": n_notes,
                "devices": n_devices,
                "automation": n_automation,
                "tempo": tempo,
                "json_kb": round(json_size / 1024, 1),
                "time_ms": round(elapsed * 1000, 1),
            })

            passed += 1
            print(f"  OK  {name} — {n_tracks}t {n_midi_clips}mc {n_audio_clips}ac {n_devices}d {n_notes}n — {json_size//1024}KB — {elapsed*1000:.0f}ms")

        except Exception as e:
            failed += 1
            tb = traceback.format_exc()
            print(f" FAIL {name} — {e}")
            warnings.append((name, str(e), tb))

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed out of {len(files)}")

    if warnings:
        print(f"\nFailures:")
        for name, err, tb in warnings:
            print(f"\n  {name}:")
            print(f"    {err}")
            # Print last 3 lines of traceback
            for line in tb.strip().split("\n")[-3:]:
                print(f"    {line}")

    if stats:
        # Summary stats
        total_tracks = sum(s["tracks"] for s in stats)
        total_clips = sum(s["midi_clips"] + s["audio_clips"] for s in stats)
        total_notes = sum(s["notes"] for s in stats)
        total_devices = sum(s["devices"] for s in stats)
        total_json = sum(s["json_kb"] for s in stats)
        avg_time = sum(s["time_ms"] for s in stats) / len(stats)
        versions = set(s["version"] for s in stats)

        print(f"\nAggregate stats across {len(stats)} projects:")
        print(f"  Ableton versions: {', '.join(sorted(versions))}")
        print(f"  Total tracks: {total_tracks}")
        print(f"  Total clips: {total_clips} ({sum(s['midi_clips'] for s in stats)} MIDI, {sum(s['audio_clips'] for s in stats)} audio)")
        print(f"  Total MIDI notes: {total_notes}")
        print(f"  Total devices: {total_devices}")
        print(f"  Total JSON output: {total_json:.0f} KB")
        print(f"  Avg parse time: {avg_time:.1f} ms")


if __name__ == "__main__":
    main()
