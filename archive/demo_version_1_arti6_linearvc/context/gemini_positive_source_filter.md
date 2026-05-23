# Research Report: Source-Filter Voice Conversion with Interpretable Transformations

**Task ID**: 05-19-package-linearvc-demo-results  
**Author**: Gemini Research Sub-agent  
**Date**: 2026-05-20  
**Focus**: Proposing executable projects using WORLD, source-filter models, and interpretable transformations (McAdams, VTLN, Formants, F0) for voice conversion (VC) without training large models.

---

## 1. Technological Landscape
Modern neural VC is highly effective but often serves as a "black box." Source-filter models (like WORLD vocoder) provide a transparent framework where pitch ($F_0$) and timbre (spectral envelope) are decoupled. Interpretable transformations allow for precise control over identity by manipulating physical proxies like vocal tract length and resonance positions.

### Key Tools & Techniques
- **WORLD Vocoder**: Standard high-quality vocoder that decomposes speech into $F_0$, Spectral Envelope (SP), and Aperiodicity (AP).
- **Vocal Tract Length Normalization (VTLN)**: A frequency warping technique ($\alpha$ factor) that simulates changing the physical length of the vocal tract.
- **McAdams Coefficient**: A power-law transformation ($\phi^\alpha$) typically applied to LPC poles or spectral bins to shift formants.
- **Formant Shifting**: Targeted movement of $F_1, F_2, F_3$ resonances to alter vowel identity or speaker timbre.
- **F0 Statistics Normalization**: Matching the mean and variance of the source $F_0$ to the target's distribution.

---

## 2. Five Concrete Project Proposals

### Project A: "The Physical Twin" — Differential VTLN for Zero-Shot VC
**Core Claim**: Voice identity can be significantly transferred by matching the "average formant spacing" ($\Delta F$) between source and target via a single differential warping factor.
- **Novelty**: Unlike ASR-based VTLN which normalizes to a neutral speaker, this method directly calculates the ratio between two specific individuals' vocal tract lengths using formant peaks.
- **Minimal Experiment**: 
    1. Extract $F_1$-$F_4$ for a set of vowels from source and target.
    2. Estimate tract length $L \approx \frac{c}{2\Delta F}$.
    3. Apply `pyworld` frequency warping using $\alpha = L_{source}/L_{target}$.
- **Data Needed**: 5-10 utterances per speaker (non-parallel).
- **Evaluation**: Objective (MCD - Mel Cepstral Distortion); Listening (Speaker Similarity vs. Naturalness).
- **Failure Mode**: Vocal tract *shape* differences (not just length) will limit similarity.
- **Verdict**: **Paper potential** (as a robust baseline for low-resource or edge-device VC).

### Project B: "McAdams Morphing" — Optimal $\alpha$ Trajectories
**Core Claim**: Using a static McAdams coefficient causes "metallic" artifacts; a dynamic coefficient $\alpha(t)$ based on instantaneous $F_0$ or energy preserves naturalness better.
- **Novelty**: Applying McAdams transformations in a time-varying manner to account for the physical constraints of the vocal tract during different phonemes.
- **Minimal Experiment**: 
    1. Implement WORLD-based McAdams transformation.
    2. Test static $\alpha$ vs. $\alpha$ modulated by a simple voicing-strength or $F_0$ curve.
- **Data Needed**: Any single-speaker dataset (e.g., CMU Arctic).
- **Evaluation**: MOS (Mean Opinion Score) for naturalness.
- **Failure Mode**: Over-modulation leads to warbling/instability.
- **Verdict**: **Demo-focused** (high visual/audio "wow" factor for a website demo).

### Project C: "Spectral Anchor Matching" — Formant-Preserving Timbre Transfer
**Core Claim**: Preserving the first two formants ($F_1, F_2$) while shifting higher-order resonances ($F_3+$) allows for timbre change without affecting linguistic intelligibility (WER).
- **Novelty**: Decoupling "content" formants from "identity" formants in a non-neural source-filter pipeline.
- **Minimal Experiment**:
    1. Use WORLD to get the spectral envelope.
    2. Detect formant peaks.
    3. Keep $F_1, F_2$ fixed; apply frequency warping only to frequencies $> 3kHz$.
- **Data Needed**: Single speaker, variety of phonemes.
- **Evaluation**: Word Error Rate (WER) using an off-the-shelf ASR; Speaker Recognition (EER).
- **Failure Mode**: Discontinuity at the 3kHz boundary.
- **Verdict**: **Paper potential** (focused on "Intelligibility-Preserving Anonymization").

### Project D: "The Statistical Mirror" — Non-Parallel F0 & Energy Histograms
**Core Claim**: Mapping source prosody to target prosody using simple histogram equalization of $F_0$ and log-energy is sufficient for many "impersonation" tasks.
- **Novelty**: A purely statistical, non-parametric approach to prosody transfer without sequence-to-sequence models.
- **Minimal Experiment**:
    1. Collect $F_0$ distributions for Source and Target.
    2. Apply a linear or spline-based mapping to the source $F_0$ contour to match target mean/variance.
- **Data Needed**: 2-3 minutes of audio from both speakers.
- **Evaluation**: F0 Correlation; Jitter/Shimmer analysis.
- **Failure Mode**: Doesn't capture "timing" or "rhythm" (durations).
- **Verdict**: **Demo-focused** (useful for "Real-time Voice Chameleon" features).

### Project E: "The Hybrid Filter" — WORLD + Differentiable All-Pass Warping
**Core Claim**: Replacing discrete spectral bin interpolation with a differentiable all-pass filter (warped-LPC) reduces phase artifacts in WORLD resynthesis.
- **Novelty**: Marrying classical warping theories (Bilinear Transform) with the high-quality decomposition of WORLD.
- **Minimal Experiment**:
    1. Implement a Bilinear all-pass filter layer.
    2. Pass WORLD spectral envelopes through this filter instead of `np.interp`.
- **Data Needed**: Standard speech datasets.
- **Evaluation**: Phase coherence metrics; Perceptual Evaluation of Speech Quality (PESQ).
- **Failure Mode**: High computational cost compared to simple interpolation.
- **Verdict**: **Paper potential** (Technical contribution to vocoder signal processing).

---

## 3. Implementation Roadmap for Demo
To produce a "useful demo" immediately:
1.  **Frontend**: Interactive sliders for "Tract Length" (VTLN $\alpha$) and "Timbre Sharpness" (McAdams $\alpha$).
2.  **Backend**: `pyworld` + `numpy` processing (extremely fast, runs on a basic CPU).
3.  **Visuals**: Real-time Spectrogram/Formant-map showing the "warping" of the spectral envelope as the user moves sliders.

## 4. References
1. Sundermann, D., et al. (2003). "VTLN-based voice conversion."
2. Patino, J., et al. (2021). "Speaker Anonymisation using the McAdams Coefficient."
3. Morise, M., et al. (2016). "WORLD: a vocoder-based high-quality speech synthesis system for real-time applications."
4. [Sprocket Toolkit (High-quality WORLD VC)](https://github.com/k2kobayashi/sprocket)
5. [PyWorld Wrapper](https://github.com/JeremyCCHsu/Python-Wrapper-for-World-Vocoder)
