# Eval: beat-link-api-style-dispatch

## Should: Branch on WaveformDetail.style before calling style-specific overloads
- Input: "Extract per-band waveform data from a WaveformDetail object in the Java bridge"
- Expected: Code checks `detail.style` (THREE_BAND, BLUE, RGB) and uses the correct API for each — `segmentHeight(i, max, ThreeBandLayer)` only for THREE_BAND, `segmentColor(i, max)` + `segmentHeight(i, max)` for BLUE/RGB
- Fail if: `ThreeBandLayer` overload used unconditionally for all waveform styles (throws UnsupportedOperationException on BLUE/RGB)

## Should: Handle all three WaveformDetail styles explicitly
- Input: "Add waveform extraction to the bridge for Pioneer hardware"
- Expected: THREE_BAND, BLUE, RGB, and mono branches all handled. XDJ-AZ sends BLUE; other hardware may send THREE_BAND or RGB.
- Fail if: Only one style handled, or unknown styles silently produce garbage data
