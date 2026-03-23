# Research: Missing Audio Clips in ALS Parser

## Status: RESOLVED — Root cause identified

## Problem
The als_reader parser reports **0 audio clips** across 69 real Ableton Live 12.3.x projects, all of which are known to contain audio tracks/clips. MIDI clips parse correctly (8,949 found, 188,275 notes). Audio clips parse correctly from a synthetic test fixture.

## Root Cause

**The parser traverses the wrong intermediate XML element for audio tracks.**

Audio tracks in Ableton Live 12.x use `<Sample>` as the clip container under `MainSequencer`, not `<ClipTimeable>`. The tag name `<AudioClip>` is correct — only the parent path differs.

### Actual XML paths (verified across 4 projects, 1,346 clips)

| Track Type | XML Path |
|---|---|
| **MidiTrack** | `DeviceChain/MainSequencer/`**`ClipTimeable`**`/ArrangerAutomation/Events/MidiClip` |
| **AudioTrack** | `DeviceChain/MainSequencer/`**`Sample`**`/ArrangerAutomation/Events/AudioClip` |

The only difference is `ClipTimeable` vs `Sample`. Everything else — `ArrangerAutomation/Events/AudioClip`, the `<AudioClip>` tag, attributes, and child elements (`SampleRef`, `WarpMarkers`, etc.) — is exactly as expected.

### Verification data

| Project | AudioClip tags | AudioTrack tags | Path |
|---|---|---|---|
| Reunion | 601 | 29 | `.../MainSequencer/Sample/ArrangerAutomation/Events/AudioClip` (100%) |
| Casino | 255 | — | same path (100%) |
| Gravity | 198 | — | same path (100%) |
| Lucid | 292 | — | same path (100%) |

Zero AudioClip elements were found under `ClipTimeable` in any project. Zero AudioClip elements used an alternative tag name. The synthetic test fixture likely had AudioClips under `ClipTimeable`, which is why it passed.

### Original hypothesis results
1. ~~Different XML path~~ — **YES, this was it.** `Sample` not `ClipTimeable`.
2. ~~Session view only~~ — No. These are arrangement clips.
3. ~~Different inner structure~~ — Only the one intermediate element differs.
4. ~~Frozen tracks~~ — `FreezeSequencer` exists (60 occurrences in Reunion) but is separate; real audio clips are under `MainSequencer/Sample`.
5. ~~Different tag name~~ — No. Tag is `<AudioClip>` as expected.

## Fix

**File:** `als_reader/extractors/clips.py`, function `extract_arrangement_clips` (line ~214)

**Current code:**
```python
ct = find(seq, "ClipTimeable")
```

**Fixed code:**
```python
ct = find(seq, "ClipTimeable") or find(seq, "Sample")
```

This is a one-line change. `ClipTimeable` is checked first (for MIDI tracks), then `Sample` as fallback (for audio tracks). The rest of the extraction logic is unchanged — `ArrangerAutomation/Events` and the `AudioClip`/`MidiClip` tag dispatch all work correctly once the parent element is found.

### Session view (clip slots)
The `extract_clip_slots` function is **not affected** — it reads from `MainSequencer/ClipSlotList`, which is the same for both track types.

## Files
- Parser code: `als_reader/extractors/clips.py` (see `extract_arrangement_clips`, line ~205)
- Real project files: `/Users/brach/Documents/Ableton Projects/Onset Analysis/Projects V2/`
- Stress test: `tests/stress_test.py`
