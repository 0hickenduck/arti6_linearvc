# Brainstorming Meeting Minutes & Handoff Context

**Date:** 2026-05-22
**Task:** 05-22-evaluate-research-directions
**Goal:** Define a concrete Master's thesis direction and demo pipeline for Voice Synthesis / Conversion, pivoting from the ARTI-6 negative results.

---

## 1. Context & User Preferences
* **Background:** We reviewed a shortlist of 5 potential research directions to replace the previous ARTI-6 factorization approach.
* **Methodology Preference:** The user strongly prefers **Deep Learning / End-to-End models** (Representation Learning) over pure mathematical/physical DSP methods (like WORLD or VTLN).
* **Core User Insight:** The user astutely observed a real-world phenomenon: **"Timbre Shift" across domains**. A single speaker's timbre actually changes when they switch languages (e.g., English to Japanese) or when they switch from speaking to singing. 

## 2. The Academic Problem (Novelty)
* **The Gap:** Current TTS and Voice Conversion (VC) models treat speaker identity as a *static* latent point (e.g., a fixed 256-d embedding). When doing cross-lingual TTS or Singing Voice Conversion (SVC), this causes **"Timbre Leakage"** or **"Identity Entanglement"** (e.g., an American speaking Japanese sounds like they have a heavy accent, or a synthesized singing voice retains the source singer's habits).
* **The Inspiration:** While the Speech community often tries to "filter out" this leakage, the Computer Vision (CV) community explicitly finds "sliders" (steering vectors) in latent space (like StyleGAN changing age or expression). 
* **The Novelty:** Applying CV-style **Latent Space Steering** to explicitly model and control the cross-lingual/singing timbre drift in speech.

## 3. The Agreed Technical Approach (A + B Combined)
We decided to combine two approaches into a single, cohesive Master's project pipeline:

### Route A: "Finding the Slider" (Statistical / Unsupervised)
* **What:** Discover the latent direction of the timbre shift without retraining a massive generative model.
* **How:** Extract embeddings using a pre-trained model (like ECAPA-TDNN or WavLM). Compute the mean vectors for domains (e.g., `Mean(Singing) - Mean(Speaking)`). This simple "Difference of Means" provides a baseline steering vector (the "slider") to apply to any speaking voice to make it sound like a singing voice.

### Route B: "The Micro-Mapper" (Deep Learning Engineering)
* **What:** Since the shift might be non-linear and speaker-dependent, we build a lightweight predictive model.
* **How:** Train a small MLP or lightweight Transformer.
  * **Input:** Base speaking embedding.
  * **Output:** Predicted domain-shifted embedding (e.g., singing or L2 language).
  * **Loss:** MSE against the ground-truth shifted embedding.
* **Why:** This satisfies the user's preference for Deep Learning, provides a clear engineering task, and is highly feasible to train on a single GPU in a few hours.

### The Final Demo (Action Item for the Next Agent)
1. Pass audio through an embedding extractor.
2. Apply the "Slider" (Route A) or the "Micro-Mapper" (Route B) to shift the embedding.
3. Feed the shifted embedding into a frozen, off-the-shelf Any-to-Any synthesizer (e.g., ARTI-6, OpenVoice) to generate the new audio.
4. Compare the baseline (un-shifted) vs. the shifted audio to prove the cross-domain accent/singing feels more natural.

---
**Note to Next Agent:** The user is ready to move from planning to implementation/demo building. Use this document as your primary context for the architecture.