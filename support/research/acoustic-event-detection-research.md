# Acoustic Event Detection & Classification for Music Audio
## Deep Research Report (March 2026)

**Goal:** Build a tool that takes audio and outputs an "arrangement formula" -- detecting individual events (hits, notes, transients), classifying instruments/tracks, and grouping events (drum fills, arpeggio runs, etc.). This report covers SOTA approaches, models, and practical tooling.

---

## 1. Foundation Models & Audio Encoders

The landscape of general-purpose audio encoders has matured significantly. These serve as the backbone for downstream event detection and classification.

### BEATs (Bidirectional Encoder from Audio Transformers)
- **Architecture:** Vision Transformer adapted for audio. Converts 16kHz audio to 128-dim mel spectrograms, patches into 16x16 blocks, feeds through transformer encoder.
- **Training:** Iterative self-supervised pre-training with audio tokenizer bootstrapping.
- **Strengths:** Strong frame-level and clip-level representations. Widely used as embedding extractor in DCASE challenge winners.
- **Status:** Original weights are not fully open-source (training code/data withheld).
- **Paper:** https://arxiv.org/abs/2212.09058

### OpenBEATs (2025)
- **Key advance:** Fully open-source reimplementation scaling BEATs to 300M parameters with 20k hours of multi-domain audio (music, environmental, bioacoustics).
- **Variable-length input** support (original BEATs was fixed-length).
- **SOTA on 13 benchmarks** across bioacoustics, environmental sound, and reasoning tasks.
- **All code, checkpoints, and training logs released** within ESPnet toolkit.
- **Paper:** https://arxiv.org/abs/2507.14129
- **Code:** https://huggingface.co/collections/espnet/openbeats

### PANNs (Pretrained Audio Neural Networks)
- **Architecture:** CNN-based (Wavegram-Logmel-CNN uses both log-mel spectrogram and raw waveform).
- **Training:** AudioSet (2M clips, 527 classes).
- **Performance:** mAP 0.439 on AudioSet tagging.
- **Use case:** Good baseline embedding extractor. Fast inference. Well-supported in Python ecosystem.
- **Paper:** https://arxiv.org/abs/1912.10211

### Audio-MAE (Masked Autoencoders that Listen)
- **Architecture:** MAE adapted for audio spectrograms. 80% masking ratio with local-attention decoder.
- **Training:** Self-supervised on AudioSet.
- **Performance:** SOTA on 6 audio/speech classification tasks.
- **2024 update:** MW-MAE (Multi-Window MAE) improves with novel multi-window multi-head attention, outperforming standard MAEs on 10 downstream tasks.
- **Paper:** https://arxiv.org/abs/2207.06405

### ATST (Audio Teacher-Student Transformer)
- **Two variants:** ATST-Clip (clip-level) and ATST-Frame (frame-level).
- **ATST-Frame** is critical for event detection -- it produces frame-level representations that can be fine-tuned for onset/offset detection.
- **Performance:** 0.587/0.812 PSDS1/PSDS2 on DCASE Task 4 (sound event detection), surpassing previous SOTA by a large margin.
- **Paper:** https://arxiv.org/abs/2306.04186
- **Code:** https://github.com/Audio-WestlakeU/ATST-SED

### AST (Audio Spectrogram Transformer)
- **Architecture:** Pure ViT applied to audio spectrograms.
- **Widely used** as a backbone. PaSST variant adds structured patchout for efficient training.
- **2024:** Multi-stage training pipeline (PaSST + BEATs + ATST ensemble) achieves top DCASE results.

---

## 2. CLAP: Zero-Shot & Few-Shot Audio Classification

CLAP (Contrastive Language-Audio Pretraining) is the most directly relevant technology for flexible event classification.

### How It Works
- Dual encoder: audio encoder + text encoder trained with contrastive loss.
- At inference: describe a sound in text ("snare drum hit", "synth pad swell", "vocal chop") and CLAP finds matching audio segments.
- **Zero-shot classification:** No training examples needed -- just text descriptions.
- **Few-shot classification:** Use CLAP embeddings as features, train a lightweight classifier on a handful of examples.

### Implementations
1. **Microsoft CLAP** -- https://github.com/microsoft/CLAP (original, 128k audio-text pairs)
2. **LAION CLAP** -- https://github.com/LAION-AI/CLAP (scaled to 4.6M pairs, 26 downstream tasks evaluated)
3. **Music-specific CLAP checkpoints** available (pretrained on music + speech collections)

### 2024 Variants
- **CompA-CLAP:** Improves compositional reasoning by 10-28% (understanding "kick THEN snare" vs just "kick AND snare").
- **T-CLAP:** Adds temporal-contrastive learning for sequence-sensitive representations.
- **CoLLAP:** Long-form segment/fusion attention for extended audio understanding.

### Relevance to Arrangement Formula
CLAP is the most practical path to classifying detected events without needing large labeled datasets. Pipeline:
1. Detect onsets/events (via onset detector or source separation)
2. Extract audio snippets around each event
3. Classify each snippet using CLAP with text prompts like "kick drum", "hi-hat", "synth stab", "vocal phrase", etc.
4. Can be extended with few-shot fine-tuning for user-specific sound categories.

---

## 3. Few-Shot Audio Classification

### Prototypical Networks for Audio
- **Core idea:** Embed support examples into metric space, classify query by nearest prototype.
- **LC-Protonets (2024-2025):** Extends to multi-label few-shot -- generates one prototype per label *combination* rather than per label. Applied to world music audio tagging across diverse cultures.
- **Episodic Fine-Tuning (2024):** ProtoNets with episodic fine-tuning for optimization-based few-shot learning, presented at IEEE MLSP 2024.
- **Few-Shot Class-Incremental:** Achieves 87.82% on NSynth-100 (musical instrument notes) and 59.25% on FSC-89.
- **Paper:** https://arxiv.org/abs/2409.11264

### Few-Shot Drum Transcription
- **Prototypical Networks for ADT:** Trained episodically on percussion types. Embed query samples in metric space where new class prototypes are computed on-the-fly from a handful of support examples. Performance holds steady when moving from fixed to open vocabulary.
- **MAML (Model-Agnostic Meta-Learning):** Combined with CRNN backbones, generalizes to heterogeneous label sets and polyphonic mixtures. Superior F1 over plain transfer learning in low-resource scenarios (Kodag et al., 2025).
- **Paper:** https://arxiv.org/pdf/2501.04742

### Practical Few-Shot Pipeline
1. Use a pretrained encoder (BEATs, OpenBEATs, or CLAP audio encoder) as feature extractor
2. User provides 3-5 examples of a target sound
3. Compute prototype embedding (mean of support set)
4. Classify new detections by cosine similarity to prototypes
5. Optionally fine-tune encoder on user's examples

---

## 4. Source Separation as Preprocessing

Source separation before event detection dramatically improves accuracy by isolating instruments.

### HTDemucs (Demucs v4)
- **Architecture:** Hybrid Transformer with dual U-Nets in time and frequency domains, cross-domain transformer attention.
- **Stems:** drums, bass, vocals, other.
- **Context:** Processes up to 12.2 second segments.
- **Best open-source model:** `htdemucs_ft` (fine-tuned variant).
- **Code:** https://github.com/facebookresearch/demucs

### LarsNet (Deep Drum Source Separation)
- **5-stem drum separation:** Separates kick, snare, hi-hat, toms, cymbals from a stereo drum mixture.
- **Architecture:** Parallel arrangement of dedicated U-Nets.
- **Dataset:** StemGMD -- 1224 hours of audio, isolated clips for every instrument in a 9-piece drum kit.
- **Faster than real-time** processing.
- **Code:** https://github.com/polimi-ispl/larsnet

### Separation -> Detection Pipeline
The recommended architecture for arrangement analysis:
```
Raw Audio
  |
  v
HTDemucs --> [drums] [bass] [vocals] [other]
  |              |
  |              v
  |         LarsNet --> [kick] [snare] [hats] [toms] [cymbals]
  |
  v
Per-stem onset detection + classification
```

This two-stage separation approach gives you isolated signals where onset detection becomes much more reliable and classification is partially solved by the separation itself.

---

## 5. Onset Detection (Beyond Energy Methods)

### Neural Network Approaches

**madmom (Python library)**
- RNNOnsetProcessor: Multiple RNNs for onset activation functions.
- CNNOnsetProcessor: CNN-based onset detection.
- Consistently outperforms energy/spectral-flux methods.
- Also includes beat tracking, downbeat detection, tempo estimation, chord recognition.
- **Code:** https://github.com/CPJKU/madmom

**CNN Onset Detection**
- Treat onset detection as a computer vision problem on spectrograms.
- CNNs outperform previous SOTA on datasets of ~100 minutes with 26k annotated onsets while requiring less manual preprocessing.

**Spectral Sparsity (NINOS2)**
- Exploits difference in spectral sparsity between onset transients and sustained portions.
- Outperforms Logarithmic Spectral Flux for sustained-string instruments.
- Better for challenging polyphonic scenarios.

### Recommended Onset Stack
1. **After source separation:** Simple peak-picking on separated stems may suffice (isolated kick = very clean transients).
2. **On mixed audio:** Use madmom's CNNOnsetProcessor or RNNOnsetProcessor.
3. **For note-level transcription:** Use Spotify's Basic Pitch (see below).

---

## 6. Automatic Music Transcription

### Spotify Basic Pitch
- **Lightweight neural network** for polyphonic note transcription.
- **Instrument-agnostic:** Works on any instrument including vocals.
- **Outputs:** Frame-wise onsets, multi-pitch, and note activations. Generates MIDI with pitch bends.
- **Jointly predicts** onsets + pitch + note activations (multi-output improves accuracy).
- **Code:** https://github.com/spotify/basic-pitch
- **TypeScript version:** https://github.com/spotify/basic-pitch-ts (runs in browser)
- **Paper:** ICASSP 2022

### Automatic Drum Transcription (ADT)

**ADTOF (Current SOTA)**
- CRNN architecture with scaled-up training data.
- ~12% improvement over 8-class baselines on MDB and ENST datasets (Riley et al., 2025).
- Correction pipeline reduces annotation noise through beat-aligned linear correction and class remapping.

**Jointist (Multi-instrument)**
- Instrument recognition module conditions both transcription and source separation modules.
- Outputs instrument-specific piano rolls.
- Explicit multi-instrument architecture.

**STAR Drums Dataset (2025)**
- New benchmark for ADT research.
- Addresses class imbalance problem (most datasets skew toward kick/snare/hat trio).

---

## 7. Audio Language Models

### Qwen2-Audio (2024)
- **Audio encoder:** Whisper-large-v3 based.
- **Capabilities:** Speech, environmental sounds, music, and songs. Instrument/genre ID, emotion, notes, captioning, QA.
- **Relevance:** Can describe what's happening in an audio clip in natural language. Could be used for high-level arrangement description or validation.
- **Code:** https://github.com/QwenLM/Qwen2-Audio

---

## 8. Event Grouping and Temporal Pattern Detection

This is the least mature area -- grouping individual events into higher-level musical gestures (drum fills, arpeggio runs, build-ups) is largely unsolved in the literature.

### Available Approaches

**Rule-Based Grouping (Most Practical Today)**
- After detecting and classifying events, apply temporal rules:
  - Drum fill: rapid succession of varied drum hits (toms, snares) typically 1-2 bars before a section boundary.
  - Arpeggio run: ascending/descending pitched events with consistent interval and short inter-onset intervals.
  - Build-up: increasing event density + rising pitch/filter movement over 2-8 bars.
- Leverage section boundaries (which you already have) as anchoring points.

**Clustering-Based Grouping**
- DBSCAN on event embeddings (time + type + pitch features) to find natural groupings.
- More robust than k-means for variable-length patterns.

**Sequence Pattern Mining**
- Treat event sequences as symbolic strings.
- Apply sequential pattern mining (PrefixSpan, GSP) to find recurring motifs.
- Musical patterns often have approximate repetition -- need fuzzy/approximate matching.

**HMM-Based Pattern Detection**
- Hidden Markov Models used for drum pattern detection in polyphonic music.
- Can model temporal dependencies between events.

**Potential Deep Learning Approach**
- Frame the problem as sequence labeling: given a stream of detected events (with type, time, pitch), label each event as part of a "fill", "run", "break", etc.
- Could train on synthetically generated patterns using MIDI datasets where these gestures are annotated.
- Transformer-based sequence models (like those used for NER in NLP) could work well here.

---

## 9. DCASE Challenge Results (State of the Art)

The Detection and Classification of Acoustic Scenes and Events (DCASE) challenge is the primary benchmark.

### DCASE 2024 Task 4 (Sound Event Detection)
- **Best system:** FMSG-JLESS ensemble -- PSDS 0.656, mPAUC 0.762
- **Architecture:** BEATs + CRNN with MixStyle domain adaptation and sound event bounding box post-processing.
- **Key techniques:** Semi-supervised mean teacher, pseudo-labeling, multi-task learning with scene information.

### DCASE 2025
- Task 3 shifts to **stereo SELD** (Sound Event Localization and Detection) -- more accessible than 4-channel.
- Challenge ongoing as of March 2026.

---

## 10. Recommended Architecture: Arrangement Formula Pipeline

Based on this research, here is the recommended pipeline architecture:

```
                        RAW AUDIO
                            |
                   [1. SOURCE SEPARATION]
                    HTDemucs v4 (htdemucs_ft)
                   /    |      |        \
               drums   bass  vocals   other
                 |       |      |        |
          [LarsNet]      |      |        |
          5-stem         |      |        |
         drum sep        |      |        |
                         |      |        |
                   [2. ONSET DETECTION]
                   Per-stem onset detection
                   (madmom CNN/RNN or peak-picking on clean stems)
                            |
                   [3. EVENT EXTRACTION]
                   Extract audio snippets around each onset
                   (typically 50-200ms windows)
                            |
                   [4. EVENT CLASSIFICATION]
                   Option A: CLAP zero-shot (text prompts)
                   Option B: Few-shot prototypical network
                   Option C: Pre-classified by separation stem
                            |
                   [5. NOTE TRANSCRIPTION (optional)]
                   Basic Pitch for pitched content (bass, synths, vocals)
                   ADT model for drum hits
                            |
                   [6. EVENT GROUPING]
                   Rule-based + clustering:
                   - Temporal proximity
                   - Instrument grouping
                   - Pattern matching (fills, runs, builds)
                   - Section boundary alignment
                            |
                   [7. ARRANGEMENT FORMULA OUTPUT]
                   Structured timeline of events + groups
```

### Technology Choices Summary

| Component | Recommended | Alternative |
|---|---|---|
| Source separation | HTDemucs v4 (`htdemucs_ft`) | Spleeter (faster, lower quality) |
| Drum separation | LarsNet (5-stem) | HTDemucs drums stem only |
| Audio encoder | OpenBEATs or BEATs | PANNs (lighter), ATST-Frame (frame-level) |
| Zero-shot classify | LAION CLAP | Microsoft CLAP |
| Few-shot classify | Prototypical Networks + BEATs embeddings | LC-Protonets |
| Onset detection | madmom CNN/RNN | librosa onset_detect (simpler) |
| Note transcription | Basic Pitch | -- |
| Drum transcription | ADTOF | Few-shot ADT with MAML |
| Event grouping | Rule-based + DBSCAN | HMM, sequence mining |
| High-level validation | Qwen2-Audio | -- |

### Key Libraries / Toolkits
- **madmom** -- onset, beat, downbeat, chord detection (Python)
- **librosa** -- general MIR, spectrograms, features (Python)
- **Demucs** -- source separation (Python/PyTorch)
- **basic-pitch** -- audio-to-MIDI transcription (Python + TypeScript)
- **LAION CLAP** -- zero/few-shot audio classification (Python/PyTorch)
- **ESPnet** -- OpenBEATs and other audio models (Python/PyTorch)
- **torchaudio** -- HTDemucs integration, audio processing (Python/PyTorch)

---

## 11. Open Research Gaps

1. **Event grouping is unsolved.** No off-the-shelf model does "detect this is a drum fill" or "this is an arpeggio run." This will require custom engineering (rules + learned patterns).

2. **Few-shot for music-specific events.** While few-shot classification works well for instrument ID, applying it to musical gestures (fills, breaks, transitions) is unexplored.

3. **Temporal compositional reasoning.** CompA-CLAP begins to address "A then B" reasoning, but music requires much deeper temporal understanding.

4. **Cross-genre generalization.** Most models are trained on pop/rock. Electronic music, jazz, classical, and non-Western music remain underserved.

5. **Real-time processing.** Most SOTA models are offline. If you need real-time arrangement analysis during DJ performance, you'd need to distill or quantize.

---

## Sources

- [OpenBEATs Paper](https://arxiv.org/abs/2507.14129)
- [BEATs Paper](https://arxiv.org/abs/2212.09058)
- [ATST-SED Code](https://github.com/Audio-WestlakeU/ATST-SED)
- [PANNs Paper](https://arxiv.org/abs/1912.10211)
- [Audio-MAE Paper](https://arxiv.org/abs/2207.06405)
- [LAION CLAP](https://github.com/LAION-AI/CLAP)
- [Microsoft CLAP](https://github.com/microsoft/CLAP)
- [LC-Protonets Paper](https://arxiv.org/abs/2409.11264)
- [HTDemucs / Demucs](https://github.com/facebookresearch/demucs)
- [LarsNet Drum Separation](https://github.com/polimi-ispl/larsnet)
- [madmom Library](https://github.com/CPJKU/madmom)
- [Spotify Basic Pitch](https://github.com/spotify/basic-pitch)
- [Qwen2-Audio](https://github.com/QwenLM/Qwen2-Audio)
- [DCASE 2024 Challenge](https://dcase.community/challenge2024/index)
- [DCASE 2025 Challenge](https://dcase.community/challenge2025/index)
- [Few-Shot Drum Transcription (MAML)](https://arxiv.org/pdf/2501.04742)
- [Drum Transcription with Momentum](https://arxiv.org/html/2507.12596v2)
- [ADTOF Package](https://www.emergentmind.com/topics/adtof-package)
- [Enhanced ADT via Drum Stem Separation](https://arxiv.org/pdf/2509.24853)
- [STAR Drums Dataset](https://transactions.ismir.net/articles/244/files/6888ab991b2f2.pdf)
- [ICKAN Instrument Classification](https://pmc.ncbi.nlm.nih.gov/articles/PMC12216839/)
- [Multi-Stage AST Training](https://arxiv.org/abs/2408.00791)
