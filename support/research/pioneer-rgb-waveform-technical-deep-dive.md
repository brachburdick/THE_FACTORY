# Pioneer CDJ/XDJ RGB Waveform: Technical Deep Dive

> Research date: 2026-03-20
> Sources: Deep Symmetry reverse engineering, pyrekordbox, rekordcrate, libdjwaveform, Mixxx, BBC audiowaveform issue tracker

---

## 1. Waveform Modes on Pioneer Hardware

Pioneer/AlphaTheta gear supports three waveform display modes:

| Mode | Color Mapping | Available On |
|------|--------------|-------------|
| **Blue** (legacy) | Monochrome blue/white. Brightness = frequency content (brighter = more highs, darker purple = more lows) | All CDJ/XDJ with screens |
| **RGB** | Red = lows, Green = mids, Blue = highs. Color is a blend based on frequency energy ratios | CDJ-2000NXS2+, XDJ-1000MK2+, XDJ-XZ/RX2+ |
| **3-Band** | Stacked: Blue = lows, Amber/Orange = mids, White = highs. Distinct layers, not a color blend | CDJ-3000, OPUS-QUAD, XDJ-RX3, DDJ-FLX10+ |

**Key distinction:** RGB mode blends the three frequency energies into a single color per column. 3-Band mode draws them as stacked/overlapping layers with fixed colors per band.

---

## 2. ANLZ File Format: Waveform Tags

Rekordbox stores pre-computed waveform data in ANLZ analysis files (`.DAT`, `.EXT`, `.2EX`). These are "tagged type" binary files with a file header followed by tagged sections.

### Tag Inventory

| Tag Code | Name | File | Entry Size | Purpose |
|----------|------|------|-----------|---------|
| `PWAV` | Wave Preview | `.DAT` | 1 byte | Monochrome overview (400 columns, older gear) |
| `PWV2` | Wave Tiny Preview | `.DAT` | 1 byte | Tiny monochrome preview (100 columns) |
| `PWV3` | Wave Detail | `.EXT` | 1 byte | Monochrome scrolling detail waveform |
| `PWV4` | Wave Color Preview | `.EXT` | 6 bytes | RGB color overview (1,200 columns) |
| `PWV5` | Wave Color Detail | `.EXT` | 2 bytes | RGB color scrolling detail waveform |
| `PWV6` | Wave 3-Band Preview | `.2EX` | 3 bytes | 3-band overview (1,200 columns) |
| `PWV7` | Wave 3-Band Detail | `.2EX` | 3 bytes | 3-band scrolling detail waveform |

### Common Header Structure (all waveform tags)

```
Offset  Size  Field
0x00    4     Tag identifier (e.g., "PWV5")
0x04    4     len_header (typically 24)
0x08    4     len_tag (total tag size including header)
0x0C    4     len_entry_bytes
0x10    4     len_entries
0x14    4     unknown (typically 0x00960000)
0x18    ...   Entry data begins
```

### Temporal Resolution

Detail waveforms (PWV3, PWV5, PWV7): **150 entries per second of audio** (one entry per half-frame at 75 fps). This means a 5-minute track has 45,000 entries.

Preview waveforms (PWAV, PWV4, PWV6): Fixed at **1,200 columns** regardless of track length (overview fits the touch strip).

---

## 3. Monochrome Waveform Encoding (PWAV, PWV2, PWV3)

Each entry is 1 byte:

```
Bits 7-5: "whiteness" / intensity (0-7)
Bits 4-0: height (0-31 pixels)
```

- Height determines how tall the waveform column is drawn
- Whiteness controls the brightness/saturation: higher values = whiter (more high-frequency content), lower values = more blue/dark (more bass)
- This is the "blue waveform" that older CDJs display

---

## 4. RGB Color Detail Waveform (PWV5) - Bit-Packed Format

Each entry is **2 bytes (16 bits, big-endian)**:

```
Bit layout (MSB first):
[15:13] red     (3 bits, values 0-7)
[12:10] green   (3 bits, values 0-7)
[ 9: 7] blue    (3 bits, values 0-7)
[ 6: 2] height  (5 bits, values 0-31)
[ 1: 0] unused  (2 bits)
```

### Extraction code (from pyrekordbox):

```python
rmask = 0xE000  # bits 15-13
gmask = 0x1C00  # bits 12-10
bmask = 0x0380  # bits 9-7
hmask = 0x007C  # bits 6-2

red   = (value & rmask) >> 13    # NOTE: pyrekordbox shifts >>12, likely a bug
green = (value & gmask) >> 10
blue  = (value & bmask) >> 7
height = (value & hmask) >> 2
```

**IMPORTANT NOTE on pyrekordbox bug:** The pyrekordbox source shifts red by 12 instead of 13, which would give red a range of 0-14 instead of 0-7. The Deep Symmetry Java implementation and the rekordcrate Rust implementation both correctly use 3-bit fields (0-7 range). The correct shift for red is `>> 13`.

### Extraction code (from Beat Link, Java - confirmed correct):

```java
red   = (bits >> 13) & 7;   // 3 bits: 0-7
green = (bits >> 10) & 7;   // 3 bits: 0-7
blue  = (bits >> 7) & 7;    // 3 bits: 0-7
height = (bits >> 2) & 0x1f; // 5 bits: 0-31
```

### Extraction code (from rekordcrate, Rust - confirmed correct):

```rust
pub struct WaveformColorDetailColumn {
    pub red: B3,      // 3 bits
    pub green: B3,    // 3 bits
    pub blue: B3,     // 3 bits
    pub height: B5,   // 5 bits
    unknown: B2,      // 2 bits
}
```

### Color Interpretation

- **Red channel (0-7):** Proportional to low-frequency energy (bass)
- **Green channel (0-7):** Proportional to mid-frequency energy
- **Blue channel (0-7):** Proportional to high-frequency energy
- **Height (0-31):** Overall amplitude/loudness of that time slice

To render to screen, scale 3-bit values to 8-bit:
```
r8 = (red * 255) / 7     // or (red * 36) approximately
g8 = (green * 255) / 7
b8 = (blue * 255) / 7
```

Beat Link's implementation averages multiple segments when zoomed out and uses the formula: `(component * 255) / (scale * 7)` where `scale` is the number of segments averaged.

---

## 5. RGB Color Preview Waveform (PWV4) - 6-Byte Format

Each entry is **6 bytes**. This is the most complex waveform tag. It encodes BOTH the color waveform AND the blue waveform in the same data.

### Byte Layout (from Deep Symmetry dysentery issue #9 + pyrekordbox):

```
Byte 0 (d0): unknown / unused
Byte 1 (d1): luminance scaling factor (0-127 after masking)
Byte 2 (d2): blue waveform inverse intensity (0-127 after masking)
Byte 3 (d3): red channel energy (0-127 after masking)
Byte 4 (d4): green channel energy (0-127 after masking)
Byte 5 (d5): blue channel energy / front height (0-127 after masking)
```

All values are masked with `& 0x7F` (7-bit, ignoring the high bit).

### Color Waveform Rendering (PWV4):

```python
# For each column x:
d1 = data[x*6 + 1] & 0x7F  # luminance
d3 = data[x*6 + 3] & 0x7F  # red
d4 = data[x*6 + 4] & 0x7F  # green
d5 = data[x*6 + 5] & 0x7F  # blue

# Color computation:
r = d3 * (d1 / 127)
g = d4 * (d1 / 127)
b = d5 * (d1 / 127)

# Heights (two layers: front and back):
back_height  = max(d3, d4, d5)   # tallest frequency band
front_height = d5                 # blue/high channel only

# Front gets +32 luminosity boost for visual pop
```

### Blue Waveform Rendering (from same PWV4 data):

```python
d2 = data[x*6 + 2] & 0x7F  # inverse blue intensity

# Inverted color formula (higher d2 = darker):
r = 95 - d2 * 1.0
g = 95 - d2 * 0.5
b = 95 - d2 * 0.25
```

This creates the characteristic blue-to-white gradient where quiet sections are light gray/white (95,95,95) and loud sections shift toward dark blue (low r, moderate g, high b).

### Beat Link's PWV4 Rendering (Java):

```java
// Color mode:
backHeight = max(unsign(bytes[base+3]), unsign(bytes[base+4]), unsign(bytes[base+5]));
frontHeight = unsign(bytes[base+5]);

maxLevel = front ? 255 : 191;  // front is brighter
red   = unsign(bytes[base+3]) * maxLevel / backHeight;
green = unsign(bytes[base+4]) * maxLevel / backHeight;
blue  = unsign(bytes[base+5]) * maxLevel / backHeight;
```

Key insight: the color is **normalized by the back height** (max of the three channels), so the color always represents the *ratio* of frequency energies, not absolute levels. The height encodes the absolute level.

---

## 6. 3-Band Waveform Data (PWV6, PWV7)

Each entry is **3 bytes**, one per frequency band:

```
Byte 0: mid-range frequency height (0-255)
Byte 1: high-frequency height (0-255)
Byte 2: low-frequency height (0-255)
```

**Note the non-intuitive order: mid, high, low** (not low, mid, high).

### Rendering Colors (fixed per band):
- Low: dark blue
- Mid: amber/orange
- High: white

### Rendering Approach:
- **Preview (PWV6):** Bands are stacked vertically (low on bottom, mid in middle, high on top)
- **Detail (PWV7):** Bands are drawn on the same axis (overlapping). Where low and mid overlap, the result appears brown. The overlap creates visual blending.

### Frequency Crossover Points (from reverse engineering, approximate):

Based on community analysis of the BBC audiowaveform issue #210 discussion:

```
Low band:    20 Hz  - 110 Hz   (high cut at 110 Hz, 6 dB/octave slope)
Low-mid:     150 Hz - 160 Hz   (12 dB/octave slopes)
Mid band:    180 Hz - 800 Hz   (12 dB/octave slopes)
High band:   2,500 Hz - 3,000 Hz (6 dB/octave slope)
             Gap from 3-19 kHz (attenuated/muted)
             19,000 Hz+ (low cut)
```

**WARNING:** These crossover points are from community observation, not official Pioneer documentation. The frequency gap from 3-19 kHz is notable and possibly intentional to focus on the most musically relevant frequencies.

For the simpler RGB mode (PWV4/PWV5), the approximate split is likely:
- Low: ~20-200 Hz
- Mid: ~200-2,500 Hz
- High: ~2,500-20,000 Hz

This aligns with Pioneer's mixer EQ crossover points (which is logical since the waveform should correspond to what the EQ knobs affect).

---

## 7. How Rekordbox Generates the Color Data (Analysis Process)

Rekordbox's analysis algorithm is proprietary, but from reverse engineering and open-source reimplementations, the process is understood to be:

### Step 1: Short-Time Fourier Transform (STFT)
- Audio is windowed into short frames (likely 1024 or 2048 sample FFT)
- Each frame is transformed via FFT to get frequency spectrum
- Window overlap improves temporal resolution (likely 50-75% overlap)
- A window function (Hann or similar) reduces spectral leakage

### Step 2: Frequency Band Energy Calculation
- FFT bins are grouped into frequency bands (low/mid/high)
- Energy (sum of squared magnitudes) is computed per band per time window
- Energy values are normalized/scaled to fit the bit depth of the output format

### Step 3: Quantization to Storage Format
- For PWV5: each band's energy is quantized to 3 bits (0-7), overall amplitude to 5 bits (0-31)
- For PWV4: each band gets 7 bits (0-127), plus a luminance byte
- For PWV6/PWV7: each band gets 8 bits (0-255) height

### Step 4: Temporal Decimation
- Detail waveforms: downsample to 150 entries/second
- Preview waveforms: downsample entire track to 1,200 columns

---

## 8. Common Mistakes When Replicating RGB Waveforms

### Mistake 1: "Color by dominant frequency"
A naive approach of "find the peak frequency, color the whole column by that frequency" produces wrong results. Rekordbox uses **energy ratios across three bands simultaneously**. A column with equal bass and treble should appear magenta (red+blue), not pick one or the other.

### Mistake 2: Using linear frequency binning
Human hearing is logarithmic. The frequency bands must use logarithmic spacing. The "mid" band covers roughly 200-2500 Hz (about 3.5 octaves), while "high" covers 2500-20000 Hz (about 3 octaves). Equal-width FFT bins would massively over-represent high frequencies.

### Mistake 3: Ignoring the two-layer rendering
The PWV4 preview waveform has TWO layers: a back (dimmer, taller) and front (brighter, shorter). The back height is `max(r, g, b)` and the front height is just the blue/high channel. This creates depth. Rendering as a single flat layer looks wrong.

### Mistake 4: Not normalizing color by amplitude
In PWV4, colors are normalized by dividing each channel by the max channel value (back_height). This means a quiet section with only bass still appears fully red, just shorter. A naive "absolute energy = brightness" approach would make quiet sections dark/invisible.

### Mistake 5: Wrong bit extraction from PWV5
The 16-bit packed format is easy to get wrong. Common errors:
- Reading as little-endian instead of big-endian
- Shifting red by 12 instead of 13 (pyrekordbox had this issue)
- Ignoring the 2 unused low bits

### Mistake 6: Using the wrong temporal resolution
150 entries per second, NOT 75. Each entry is one half-frame at 75 fps.

### Mistake 7: Full-mix spectral coloring without source separation
The libdjwaveform project explicitly warns: processing a full stereo mix produces poor color results because frequency bands overlap and mask each other. Professional results often benefit from stem separation (drums, bass, vocals, other) before color mapping, then compositing via screen blending.

---

## 9. Open Source Implementations

### Parsers (read ANLZ waveform data):

| Project | Language | URL | Notes |
|---------|----------|-----|-------|
| **crate-digger** | Java | https://github.com/Deep-Symmetry/crate-digger | Kaitai Struct definitions (`rekordbox_anlz.ksy`). Most complete RE documentation. |
| **beat-link** | Java | https://github.com/Deep-Symmetry/beat-link | Full rendering of color waveforms. `WaveformDetail.java`, `WaveformPreview.java` contain rendering code. |
| **pyrekordbox** | Python | https://github.com/dylanljones/pyrekordbox | Read/write ANLZ files. `anlz/tags.py` has PWV4/PWV5 parsing. Caution: possible bit-shift bug in PWV5 red channel. |
| **rekordcrate** | Rust | https://github.com/holzhaus/rekordcrate | Clean Rust structs with bitfield macros. `anlz.rs` has `WaveformColorDetailColumn`. |
| **rekordbox-parser** | JavaScript | https://github.com/evanpurkhiser/rekordbox-parser | Parses DeviceSQL and ANLZ files. |

### Generators (create waveform visuals from audio):

| Project | Language | URL | Notes |
|---------|----------|-----|-------|
| **libdjwaveform** | C | https://github.com/turbo/libdjwaveform | STFT-based, configurable frequency-to-color gradient. Recommends stem separation. |
| **Mixxx** | C++ | https://github.com/mixxxdj/mixxx | GLSL shader rendering. RGB mode: red=low, green=mid, blue=high. Crossovers at ~246 Hz and ~2.5 kHz. |

### Documentation:

| Resource | URL | Notes |
|----------|-----|-------|
| **DJ Link Ecosystem Analysis** | https://djl-analysis.deepsymmetry.org/rekordbox-export-analysis/anlz.html | Definitive ANLZ format reference |
| **pyrekordbox docs** | https://pyrekordbox.readthedocs.io/en/latest/formats/anlz.html | Python-focused format docs |
| **dysentery issue #9** | https://github.com/Deep-Symmetry/dysentery/issues/9 | Original NXS2 color waveform reverse engineering discussion |

---

## 10. Blue Overview vs RGB Detail: The Visual Difference

### Blue Waveform (legacy, all Pioneer gear)
- Single-color (blue to white gradient)
- Brightness encodes frequency content: bright white = lots of highs, dark blue/purple = lots of bass
- Height encodes amplitude
- Stored in PWAV/PWV2 (preview) and PWV3 (detail) as 1 byte per entry
- The 3-bit "whiteness" value in the upper bits controls the blue-to-white blend

### RGB Color Waveform (NXS2+)
- Full color where R/G/B channels independently represent low/mid/high frequency energy
- A pure kick drum appears red
- A hi-hat appears blue
- A vocal appears green/yellow
- A full-spectrum mastered section appears white or light gray (all channels high)
- Color represents frequency *ratio*, height represents overall *amplitude*
- Stored in PWV4 (preview, 6 bytes/entry) and PWV5 (detail, 2 bytes/entry)

### 3-Band Waveform (CDJ-3000+)
- Three distinct colored layers rather than a single blended color
- Each band has its own independent height value (0-255)
- Visual rendering stacks or overlaps the three bands
- More analytically useful than RGB because you can see each band's amplitude independently
- Stored in PWV6 (preview) and PWV7 (detail), 3 bytes per entry

---

## 11. Rendering Algorithm Summary

### For PWV5 (RGB Detail) - what you'd implement:

```
For each time column:
  1. Read 2 bytes, big-endian
  2. Extract: r(3-bit), g(3-bit), b(3-bit), h(5-bit)
  3. Scale color: r8 = r * 36, g8 = g * 36, b8 = b * 36
  4. Scale height: pixel_height = h * (display_height / 31)
  5. Draw vertical line of color (r8, g8, b8) from center,
     extending pixel_height/2 up and pixel_height/2 down
```

### For PWV4 (RGB Preview) - two-layer approach:

```
For each of 1,200 columns:
  1. Read 6 bytes, mask each with 0x7F
  2. d1 = luminance, d2 = blue_inv, d3 = red, d4 = green, d5 = blue

  Color waveform (foreground):
    3. back_h = max(d3, d4, d5)
    4. front_h = d5
    5. color = (d3, d4, d5) * (d1/127)  -- luminance-scaled
    6. Draw back layer at back_h with dimmer color
    7. Draw front layer at front_h with brighter color (+32 luminance)

  Blue waveform (alternative):
    8. r = 95 - d2, g = 95 - d2*0.5, b = 95 - d2*0.25
    9. Height from d2 value
```

### For PWV6/PWV7 (3-Band):

```
For each column:
  1. Read 3 bytes: mid_h, high_h, low_h  (NOTE: mid first, not low)

  Preview (stacked):
    2. Draw low (blue) from bottom, height = low_h
    3. Draw mid (amber) stacked on top of low
    4. Draw high (white) stacked on top of mid

  Detail (overlapping):
    2. Draw all three from same baseline
    3. Where bands overlap, colors blend (low+mid = brown)
```
