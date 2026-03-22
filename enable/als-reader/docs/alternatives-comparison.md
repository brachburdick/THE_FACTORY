# ALS Parsing Alternatives Comparison

**Date:** 2026-03-20

---

## Summary Table

| Criterion | pyableton | DIY gzip+ET | dawtool | loive |
|---|---|---|---|---|
| MIDI notes | Yes | Yes (manual) | No | No |
| Audio clips/refs | No | Yes | No | No |
| Devices/plugins | No | Yes | No | Yes (old) |
| Volume/sends | No | Yes | No | No |
| Tempo | Yes | Yes | Yes | No |
| Time markers | No | Yes | Yes (best) | No |
| Automation | Partial | Yes | Partial | No |
| Crash resilience | Poor | You control | Good | Unknown |
| Maintenance | Stale (2024-02) | N/A | Stale (2021) | Dead (2013) |
| Dependencies | muspy, pandas | None | None | colorama |
| Write .als | No | Possible | No | No |

---

## Raw gzip + xml.etree (DIY)

```python
import gzip
import xml.etree.ElementTree as ET

with gzip.open("project.als", "rb") as f:
    tree = ET.parse(f)
root = tree.getroot()

# Full access to every XML element
for track in root.find('.//Tracks'):
    print(track.tag, track.attrib.get('Id'))
```

**Advantages over pyableton:**
- Access to ALL XML elements, not just the ~20% pyableton models
- No crash on unexpected elements
- No external dependencies
- Can read device chains, audio clips, sample paths, volume, sends -- everything
- Can be version-aware via `root.attrib['Creator']`
- Trivial to implement: .als is just gzip'd XML

**Disadvantages:**
- No typed object model (raw ElementTree)
- Must know the XML schema yourself
- No MIDI export convenience

---

## dawtool (offlinemark/dawtool)

- **Stars:** 210 (10x pyableton)
- **Repo:** https://github.com/offlinemark/dawtool
- **Focus:** Time marker extraction with tempo automation support
- **Supports:** Ableton 8-12, FL Studio 10-20, .cue files
- **Maturity:** Production-tested on 10,000+ files since 2020
- **Limitation:** Only officially exposes markers. Internal APIs have more but are unstable.
- **Last activity:** March 2021 (stale, but proven)
- **Best for:** DJ mix tracklist generation, podcast chapters, cue point extraction
- **Not useful for:** General arrangement/MIDI/device analysis

---

## loive (naglalakk/loive)

- **Stars:** 41
- **Repo:** https://github.com/naglalakk/loive
- **Last updated:** February 2021 (effectively 2013-era code)
- **Focus:** Plugin/device detection, project summary
- **Unique strength:** Actually lists VST/AU plugins and Ableton native devices
- **Limitation:** Tested only on Ableton 8.1.3 and 9.0.4. Python 2 era.
- **Not viable** for modern use without significant modernization

---

## Other Notable Repos

- **jbremz/als-parser** (1 star): CLI tool, recently updated (2025), worth monitoring
- **Alerion/blendals** (3 stars): Parses .als to JSON, updated 2024
- **MartinBarker/Ableton-To-Cue-Tracklist-Generator** (2 stars): Specific to tracklist/cue generation

---

## Recommendation

**Build a custom parser using gzip + xml.etree.ElementTree.**

Rationale:
1. .als format is straightforward gzip'd XML with a consistent, self-documenting schema
2. pyableton covers only ~20% of useful schema and crashes on real-world files
3. Custom parser targets exactly the elements needed with graceful missing-element handling
4. Zero external dependencies (Python stdlib only)
5. Can be built incrementally: tracks -> MIDI notes -> devices -> audio refs -> automation
6. pyableton's declarative annotation-to-XML mapping pattern is worth borrowing, but needs proper optional-field handling

See [design-brief.md](design-brief.md) for the custom parser design.
