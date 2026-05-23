# Deep-Read: Interpretable Timbre Manipulation via Source-Filter Signal Processing

## Overview
The ARTI-6 model, despite its 6-dimensional latent space, failed to provide interpretable "small transformations" for timbre because its latent space is content/articulation-dominant, with speaker identity tied to a discrete `speaker_id`. To achieve true interpretable voice conversion, we must return to **physically-grounded source-filter representations** where parameters map directly to vocal tract geometry or excitation characteristics.

This document outlines 5 experiment ideas that bypass "black-box" neural pitfalls by using WORLD, LPC, or DDSP frameworks.

---

## Experiment 1: The McAdams Anonymizer (LPC-Pole Warping)
**Claim:** Non-linear warping of LPC poles provides a "global speaker size" control that is independent of phonetic content.
- **Why it avoids ARTI-6 failure:** It operates on the *explicit* spectral envelope (filter) after removing the excitation (source), ensuring no "leakage" of speaker identity from the content.
- **Minimal Experiment:**
    1. Perform 12th-order LPC analysis on a source utterance.
    2. Extract roots (poles) of the LPC polynomial.
    3. Apply $\phi' = \phi^\alpha$ to complex pole angles (McAdams coefficient $\alpha \in [0.8, 1.2]$).
    4. Resynthesize using the original LPC residual.
- **Expected Audio Behavior:** $\alpha < 1$ creates a "child-like/smaller" head resonance; $\alpha > 1$ creates a "giant/larger" chest resonance.
- **Measurement:** Perceptual speaker similarity (MOS) vs. Intelligibility (WER).
- **Failure Mode:** "Metallic" artifacts or "phasiness" if $\alpha$ is too extreme (>1.3 or <0.7).
- **Paper/Demo Value:** Establishes a baseline for "one-slider" timbre control.
- **Source:** [VoicePrivacy Challenge Baseline (B2)](https://arxiv.org/abs/2005.01387)

---

## Experiment 2: WORLD-VTLN (Frequency Warping)
**Claim:** Applying a bilinear frequency warping to the WORLD spectral envelope simulates Vocal Tract Length Normalization (VTLN) more robustly than latent morphing.
- **Why it avoids ARTI-6 failure:** WORLD explicitly disentangles F0, aperiodicity, and spectral envelope. VTLN targets *only* the frequency axis of the envelope.
- **Minimal Experiment:**
    1. Extract F0, SP (Spectral Envelope), and AP (Aperiodicity) using WORLD.
    2. Warp the frequency axis of SP using a bilinear function $f_{new} = \beta(f_{old})$.
    3. Synthesize.
- **Expected Audio Behavior:** Natural-sounding shifts in "vocal size" without affecting pitch or rhythm.
- **Measurement:** Formant frequency tracking (F1-F2 plot) to verify consistent shifting.
- **Failure Mode:** Spectrum "smearing" at high frequencies if the warping function is not properly constrained.
- **Paper/Demo Value:** Demonstrates "zero-shot" size manipulation without neural training.
- **Source:** [Differentiable WORLD (DiffWorld)](https://arxiv.org/abs/2210.15044)

---

## Experiment 3: Spectral Tilt for Vocal Effort
**Claim:** Manipulating the slope of the spectral envelope (Spectral Tilt) simulates "vocal effort" (whisper vs. shout) independently of volume.
- **Why it avoids ARTI-6 failure:** ARTI-6 likely entangles loudness with content. Spectral tilt is a pure filter-shaping operation.
- **Minimal Experiment:**
    1. Fit a linear regression to the log-magnitude spectrum of the WORLD envelope.
    2. Rotate the slope of this line by $\theta$.
    3. Apply the delta-filter back to the envelope and synthesize.
- **Expected Audio Behavior:** Voice sounds "strained/tense" (negative tilt) or "relaxed/breathy" (positive tilt).
- **Measurement:** Correlation between tilt parameter and perceived "energy."
- **Failure Mode:** Excessive positive tilt makes speech sound like it's coming through a telephone/muffled.
- **Paper/Demo Value:** Adds a second dimension ("Effort") to the "Size" dimension from VTLN.
- **Source:** [Source-Filter Emotional VC](https://arxiv.org/abs/2104.03523)

---

## Experiment 4: DDSP Harmonic-to-Noise Ratio (HNR) Control
**Claim:** A lightweight DDSP model can provide a single slider for "breathiness" by scaling the excitation of the noise synth vs. the harmonic synth.
- **Why it avoids ARTI-6 failure:** Neural models often conflate breathiness with poor reconstruction. DDSP makes it a *design parameter*.
- **Minimal Experiment:**
    1. Train a 1M-parameter DDSP model on any single speaker.
    2. At inference, multiply the `noise_gain` by a factor $\gamma$ and the `harmonic_gain` by $1-\gamma$.
- **Expected Audio Behavior:** Smooth transition from "pure tone" to "breathy/hoarse" to "whisper."
- **Measurement:** Signal-to-Noise Ratio (SNR) in unvoiced segments.
- **Failure Mode:** If HNR is too low, phonetic consonants (s, t, p) may become unintelligible.
- **Paper/Demo Value:** High-fidelity "texture" control for neural-classical hybrids.
- **Source:** [Google Magenta DDSP](https://github.com/magenta/ddsp)

---

## Experiment 5: Formant-Preserving F0 Normalization
**Claim:** Normalizing F0 to a constant mean while keeping formants fixed allows for "monotone" content extraction, proving that content and identity are separable.
- **Why it avoids ARTI-6 failure:** ARTI-6's speaker identity is entangled with the *pitch range*. Explicit normalization isolates the filter.
- **Minimal Experiment:**
    1. Extract F0 and Spectral Envelope using WORLD.
    2. Replace the F0 contour with its mean value $F_{mean}$.
    3. Synthesize using original Envelope.
- **Expected Audio Behavior:** Robotic, monotone speech that *perfectly* retains the speaker's timbre.
- **Measurement:** Speaker ID accuracy (ASV) on monotone speech vs. original.
- **Failure Mode:** Loss of prosodic cues might make word boundaries hard to detect.
- **Paper/Demo Value:** Disentanglement proof-of-concept.
- **Source:** [SpeechSplit2.0](https://arxiv.org/abs/2203.13444)

---

## Summary of Experiment Value
| Experiment | Parameter | Perceived Change | Framework |
| :--- | :--- | :--- | :--- |
| **1. McAdams** | $\alpha$ | Size / Body | LPC (Classical) |
| **2. VTLN** | $\beta$ | Age / Gender | WORLD (Classical) |
| **3. Tilt** | $\theta$ | Effort / Tension | WORLD (Classical) |
| **4. HNR** | $\gamma$ | Breathiness | DDSP (Neural-Hybrid) |
| **5. F0-Norm** | $F_{mean}$ | Prosody removal | WORLD (Classical) |
