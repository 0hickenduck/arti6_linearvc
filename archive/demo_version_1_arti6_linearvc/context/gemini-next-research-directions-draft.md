# ARTI-6 + LinearVC: Next Research Directions

## Context & Motivation
Our initial experiments attempted to apply Pure LinearVC (affine transformations) directly to ARTI-6's 6D articulatory features. This failed to achieve voice conversion; the affine transformations degraded intelligibility while the speaker timbre remained anchored to the explicitly provided ECAPA speaker embedding. 

The core research question moving forward is: **Why does LinearVC work in high-dimensional SSL acoustic feature spaces (e.g., WavLM), but fail in ARTI-6's low-dimensional articulatory bottleneck?** 

This document proposes literature to review and lightweight experiments to investigate this representation gap.

---

## 1. Required Reading List (5-8 Papers/Systems)

### 1. LinearVC (Kamper et al., Interspeech 2025)
- **Core representation:** High-dimensional self-supervised learning (SSL) acoustic features (specifically WavLM).
- **Conversion mechanism:** Computes a simple linear projection matrix (least-squares regression) to map source speaker features to target speaker features. 
- **Relation to ARTI-6:** This is the exact method we attempted to apply. LinearVC demonstrates that in WavLM space, content and speaker identity are linearly separable. Its success contrasts sharply with our ARTI-6 6D failure.

### 2. WavLM: Large-Scale Self-Supervised Pre-Training for Full Stack Speech Processing (Chen et al.)
- **Core representation:** 1024-dimensional acoustic embeddings optimized for both ASR and speaker verification.
- **Conversion mechanism:** Not a VC system itself, but provides the representation space where content, speaker, and prosody are entangled but extractable.
- **Relation to ARTI-6:** Acts as the high-dimensional, entangled baseline representation to compare against ARTI-6's explicitly factorized 6D space.

### 3. Speech Articulatory Coding (SPARC) / RT-VC
- **Core representation:** Low-dimensional articulatory features (e.g., 14-channel EMA-based representation).
- **Conversion mechanism:** Maps audio to physical articulatory trajectories (analysis), then uses a speaker-dependent synthesis model to reconstruct audio. VC is achieved by passing source articulation to the target speaker's synthesizer.
- **Relation to ARTI-6:** Highly analogous to ARTI-6. Confirms that proper articulatory representations naturally factor out speaker identity, requiring the synthesizer (or an explicit embedding) to dictate the target voice.

### 4. kNN-VC: Voice Conversion with Non-Parametric self-supervised features
- **Core representation:** WavLM features.
- **Conversion mechanism:** Replaces each source feature frame with the nearest neighbor from a pool of target speaker reference frames.
- **Relation to ARTI-6:** Provides another non-parametric baseline in the SSL space. Useful for understanding how acoustic features cluster by phonetic content versus speaker identity.

### 5. NANSY (Neural Analysis and Synthesis) or FreeVC
- **Core representation:** Information bottlenecks (HuBERT/Wav2Vec2) combined with explicit pitch (F0) and energy contours.
- **Conversion mechanism:** Achieves VC by heavily bottlenecking the content representation (to strip speaker identity) and re-conditioning a vocoder with the target speaker embedding.
- **Relation to ARTI-6:** ARTI-6 functions as an extreme information bottleneck (6D). These papers provide the theoretical framework for why extreme bottlenecks naturally resist linear speaker transformations (because the speaker information has already been discarded).

### 6. ECAPA-TDNN: Emphasized Channel Attention, Propagation and Aggregation in TDNN
- **Core representation:** Highly discriminative, fixed-length speaker embeddings.
- **Conversion mechanism:** Used for speaker verification, not VC natively.
- **Relation to ARTI-6:** ARTI-6 relies entirely on ECAPA-TDNN for speaker conditioning. Understanding ECAPA's discriminative power explains why ARTI-6's decoder ignores small perturbations in the 6D space and anchors timbre strictly to the ECAPA vector.

---

## 2. Concrete Experiment Tracks (No Large Model Training Required)

These experiments focus on representation auditing and diagnostic contrasts, as recommended in the project's local notes.

### Track 1: Speaker Predictability Audit (Information Theoretic Check)
**Goal:** Quantify how much speaker identity is retained in ARTI-6's 6D features versus WavLM features.
**Method:** 
1. Extract ARTI-6 6D features and WavLM features for a subset of the CMU ARCTIC dataset.
2. Train lightweight linear classifiers (or SVMs) on these feature summaries to predict speaker ID.
3. **Expected Outcome:** WavLM representations will yield high speaker ID accuracy, proving speaker information is present. ARTI-6 6D features will yield near-random accuracy, proving the bottleneck successfully stripped speaker identity, explaining why a linear transform cannot recover it.

### Track 2: Same-Prompt Content Clustering Analysis (Distance Audit)
**Goal:** Understand the geometry of the representations regarding phonetic content versus speaker identity.
**Method:**
1. Select same-prompt (parallel) utterances across different speakers (e.g., `bdl` and `slt` saying the exact same sentence).
2. Compute dynamic time warping (DTW) or frame-wise Euclidean distances between:
   - Same-prompt, cross-speaker pairs.
   - Different-prompt, same-speaker pairs.
3. Compare the distance ratios in ARTI-6 6D space versus WavLM space.
4. **Expected Outcome:** In ARTI-6 6D space, same-prompt cross-speaker distances will be extremely small (tight content clustering, invariant to speaker). In WavLM space, the speaker variation will cause same-prompt representations to be much further apart.

### Track 3: WavLM LinearVC Contrast vs. ARTI-6 Embedding Swap
**Goal:** Establish a fair baseline showing that LinearVC works purely on the representation space, not via conditioning.
**Method:**
1. Apply the original LinearVC method (least-squares affine transform) to WavLM features on our existing CMU ARCTIC 5-train/1-test split.
2. Synthesize the WavLM LinearVC output using a standard vocoder (e.g., HiFi-GAN).
3. Compare the objective metrics (and subjective listening quality) of this "WavLM LinearVC" against our "ARTI-6 6D + Target ECAPA Swap" baseline.
4. **Expected Outcome:** This empirically proves that linear maps are sufficient for VC in un-bottlenecked acoustic spaces, but that ARTI-6's architectural separation of content (6D) and style (ECAPA) is performing the VC natively, rendering articulatory affine transforms obsolete.
