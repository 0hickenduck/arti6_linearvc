# Literature Survey: Domain and Skill Shifters for Voice/Singing Conversion

## Executive Summary

This literature survey investigates the feasibility of freezing a strong backbone (e.g., self-supervised representations like ContentVec/WavLM) and training a lightweight "shifter" or adapter to perform voice, singing, and style conversion. It addresses 10 key research directions requested to determine whether this approach forms a defensible and productive direction for a Master's thesis.

The findings largely **support** the hypothesis that a lightweight shifter on top of a frozen backbone is viable. Recent research demonstrates that self-supervised learning (SSL) representations naturally organize information hierarchically and geometrically, disentangling content from speaker identity and recording conditions. Linear transformations, projection matrices, and nearest-neighbor matching (e.g., kNN-VC) have proven remarkably effective without requiring full model fine-tuning.

However, **singing voice conversion (SVC) presents distinct challenges** compared to speech. The interplay between $F_0$ (pitch) and vocal tract resonances is more complex in singing, especially at high frequencies, and dynamic singing techniques (vibrato, breathiness) are harder to model with simple linear shifts. Similarly, prosody transfer requires explicit modeling (e.g., PMVC) because simple vector addition does not capture temporal alignment and rhythmic variations effectively.

The survey concludes that while lightweight shifters are excellent for timbre and simple domain adaptation, transferring complex, temporally dependent skills (like professional singing techniques or charismatic speaking) requires structured latent variable modeling or explicit prompt-based extraction rather than naive latent addition.

---

## Ranked Recommendations for Master's Thesis

1. **Geometry-Based Shifters for Skill & Timbre (Direction 9 + Direction 3)**
   - **Why:** Investigating the linear separability and geometry of SSL representations for singing vs. speaking offers a highly defensible, analytically rigorous thesis. Building a lightweight "skill shifter" (novice to professional) using linear probes or simple adapters on a frozen WavLM backbone is computationally cheap, novel, and robust to negative results (if it fails, the geometric analysis is still a valid thesis).
2. **Domain-Adversarial Latent Filtering for Dirty Data (Direction 2 + Direction 1)**
   - **Why:** Real-world VC data is always noisy (BGM, bad mics). Applying domain-adversarial training to extract a "clean" latent representation from a frozen backbone before shifting identity is highly practical. The thesis would focus on whether dataset-specific artifacts (like room IR or music style) can be successfully stripped using adversarial classifiers without hurting content.
3. **Prompt-Based Prosody & Skill Transfer via Partial Substitution (Direction 7 + Direction 5)**
   - **Why:** Inspired by Ozuru et al. (2020), this direction focuses on what makes a speaker sound "professional". Using a frozen backbone to encode content, and training a lightweight module to inject prosody/style from a reference prompt (e.g., PMVC) provides a clear evaluation path and demo-friendly results.

---

## 1. Dataset-Specific Information as Nuisance

### Core Papers
1. **Noise-robust voice conversion with domain adversarial training** (Du et al., 2022) [arXiv:2201.10693]
   - *Task:* VC under noisy conditions.
   - *Data:* Clean speech corrupted with varied noise.
   - *Representation:* Disentangled speaker and content encoders.
   - *Model/Loss:* Domain adversarial training (GRL) to ensure representations are noise-invariant.
   - *Evaluation:* Objective metrics and subjective MOS.
   - *Conclusion:* DAT successfully forces the latent space to ignore noise, synthesizing clean target speech.
2. **Noise-Robust Voice Conversion by Conditional Denoising Training...** (Igarashi et al., 2024) [arXiv:2406.07280]
   - *Task:* VC with noisy/reverberant inputs.
   - *Data:* Varied recording qualities and environments.
   - *Representation:* Frame-wise and utterance-wise latent variables for environment and quality.
   - *Model/Loss:* Conditional denoising training using specialized deep neural networks to extract quality/environment embeddings.
   - *Conclusion:* Conditioning the VC model on frame-wise environment variables significantly improves naturalness in noisy-to-clean scenarios.

**Supports "only train a shifter"?** Yes. By treating the dataset/noise as a domain, a lightweight network can map the corrupted representation into a clean subspace before the main "shift" is applied.
**Minimal Experiment:** Train a linear classifier on frozen WavLM features to predict `dataset_id` or `mic_id`. If accuracy is high, train a small GRL adapter to make it un-predictable.
**Feasibility:** High.

---

## 2. Domain-Adversarial Training for Dirty Voice Data

### Core Papers
1. **Cross-Lingual Text-To-Speech Synthesis via Domain Adaptation and Perceptual Similarity Regression in Speaker Space** (Xin, Saito, Takamichi et al., 2020) [ISCA Archive]
   - *Task:* Cross-lingual TTS maintaining speaker identity.
   - *Data:* Multi-lingual speech corpora.
   - *Representation:* Speaker embeddings.
   - *Model/Loss:* Domain adaptation to map different language speaker embeddings into a language-independent space, plus perceptual similarity regression.
   - *Conclusion:* Adapting speaker embeddings to a shared space improves cross-lingual synthesis and preserves perceptual similarity.
2. **General DAT Literature in TTS/VC** (Various, 2020-2024)
   - *Task:* Disentangling content from style, accent, or noise.
   - *Model/Loss:* Gradient Reversal Layers (GRL) attached to attribute classifiers.

**Supports "only train a shifter"?** Yes. Xin et al. (2020) shows that a speaker space can be adapted (shifted) to be language-independent. This perfectly aligns with learning a domain-shifter `f(z, domain)`.
**Minimal Experiment:** Use the existing ARTI-6 or Seed-VC latents. Add a domain classifier (e.g., `is_clean_studio` vs `is_web_scraped`) with a GRL and update only a small projection layer to fool the classifier.
**Feasibility:** High.

---

## 3. Frozen Backbone plus Lightweight Shifter

### Core Papers
1. **ContentVec: An Improved Self-Supervised Speech Representation...** (Qian et al., 2022) [arXiv:2204.09224]
   - *Task:* Disentangling speaker info from content in SSL.
   - *Model:* HuBERT-based, explicitly trained to discard speaker identity.
   - *Conclusion:* ContentVec representations are highly robust for VC because the backbone already does the disentangling.
2. **kNN-VC: Untrained Voice Conversion with Non-parametric Nearest Neighbors** (Baas et al., 2023) [arXiv:2305.18975]
   - *Task:* Zero-shot VC.
   - *Representation:* Frozen WavLM features.
   - *Model:* No training. Replaces source frames with k-nearest neighbor frames from the target, then uses a vocoder.
   - *Conclusion:* Extremely strong VC is possible with zero training, just by navigating the geometric space of a frozen backbone.

**Supports "only train a shifter"?** Absolutely. kNN-VC proves that the frozen backbone geometry is already rich enough that simple interpolation (kNN) works. A trained lightweight shifter would only optimize this trajectory.
**Minimal Experiment:** Replicate kNN-VC logic locally using HuBERT or WavLM, but replace the kNN step with a small learned linear mapping between speaker A and speaker B clusters.
**Feasibility:** High.

---

## 4. Singing Skill as a Latent Attribute

### Core Papers
1. **GTSinger** (2024) [arXiv:2409.13832] - A massive annotated singing dataset for technique-controllable SVS.
2. **TechSinger** (2025) [arXiv:2502.12572] - Flow-matching synthesis controlled by natural language prompts describing vocal techniques (breathiness, falsetto).
3. **CONTUNER: Singing Voice Beautifying** (2024) [arXiv:2404.19187]
   - *Task:* Amateur-to-Professional singing conversion (SVB).
   - *Model:* Diffusion model with an "expressiveness enhancer" in the latent space to correct pitch and enhance tone without changing timbre.

**Supports "only train a shifter"?** Partially. CONTUNER shows that latent-space beautification works, but it uses a diffusion model, which is heavier than a simple linear shifter. Skill in singing (vibrato, pitch correction) requires temporal awareness that a pure frame-by-frame shifter might lack.
**Minimal Experiment:** Train a classifier on GTSinger to predict `has_vibrato`. Try to shift a flat note latent vector along the vibrato gradient.
**Feasibility:** Medium.

---

## 5. Speaking Skill as a Latent Attribute

### Core Papers
1. **Are you professional?: Analysis of prosodic features between a newscaster and amateur speakers through partial substitution by DNN-TTS** (Ozuru, Ijima, Saito, Minematsu, 2020) [ISCA Archive]
   - *Task:* Analyzing perceptual differences between amateur and professional (newscaster) speech.
   - *Model:* DNN-TTS used to partially substitute prosodic features (F0, duration) while keeping spectral features constant.
   - *Conclusion:* Listeners' perception of "professionalism" is heavily affected by F0 patterns (specifically the standard deviation of F0) rather than just phoneme duration.
2. **PSST: Public-Speaking Style Transfer** (2024) - Benchmark for text-to-text style transfer targeting interactivity and emotionality.

**Supports "only train a shifter"?** Yes. Ozuru et al. proved that you can substitute specific prosodic features (F0) into an otherwise constant spectral representation to shift the perceived skill level. A lightweight shifter could specifically target the F0 conditioning of a vocoder.
**Minimal Experiment:** Take an amateur recording, extract content latents, and run them through a vocoder conditioned on an artificially smoothed and widened F0 contour (mimicking the newscaster SD).
**Feasibility:** High.

---

## 6. Why Singing Is Harder than Speech VC

### Core Papers
1. **F0 Transformation and High-F0 Representation** - Highlights that at high pitches, harmonics become sparse, making spectral envelope (formant) estimation highly ambiguous.
2. **Vocal Tract Resonances in Speech and Singing** - Shows that unlike speech (where F0 and formants are independent), singers actively tune their vocal tract resonances to align with F0 harmonics for projection (formant tuning).

**Supports "only train a shifter"?** Weakens. Because singers dynamically couple their articulation (formants) to their pitch (F0), a simple linear combination `z + f(skill)` might fail. The shift required changes non-linearly based on the current F0.
**Minimal Experiment:** Plot the mutual information between F0 and the top 3 PCA dimensions of the frozen backbone for a speaking dataset vs. a singing dataset.
**Feasibility:** Medium (analysis is easy, solving it is hard).

---

## 7. Prompt-Based Prosody Transfer

### Core Papers
1. **PMVC: Data Augmentation-Based Prosody Modeling for Expressive VC** (2023) [arXiv:2308.11084]
   - *Task:* Extracting and transferring prosody without text.
   - *Model:* Encoder with AdaIN to remove static speaker info, combined with a Mask-and-Predict mechanism to disentangle dynamic prosody.
2. **Wavelet analysis of speaker dependent and independent prosody** (Sisman, 2018) - Using wavelets to separate scale-variant prosodic features.

**Supports "only train a shifter"?** Yes, but the shifter must be temporal (e.g., a Transformer/RNN layer, not just an MLP). PMVC uses AdaIN, which is essentially a shifting and scaling operation (`gamma * z + beta`), proving the shifter hypothesis is valid for style transfer.
**Minimal Experiment:** Implement an AdaIN layer that takes a reference prosody embedding and shifts the content embedding.
**Feasibility:** High.

---

## 8. Articulatory Representation for Skill or Pronunciation Editing

### Core Papers
1. **Coding Speech through Vocal Tract Kinematics (SPARC)** (2024) [arXiv:2406.12998]
   - *Task:* Disentangling speaker and content using physically grounded kinematic traces.
2. **RT-VC** (2025) [arXiv:2506.10289]
   - *Task:* Real-time zero-shot VC using articulatory features and DDSP.

**Supports "only train a shifter"?** Yes. Articulation is mostly speaker-independent. Modifying the articulatory trace (e.g., smoothing it for better pronunciation) before passing it to a target speaker's decoder is exactly what a skill shifter would do.
**Minimal Experiment:** Apply a low-pass filter to the ARTI-6 representation (simulating sluggish articulation) and see if the converted voice sounds "drunk" or "unskilled".
**Feasibility:** High.

---

## 9. Representation Geometry Audit

### Core Papers
1. **Layer-wise Analysis of SSL Models** (Various) - Shows lower layers capture acoustics, middle capture phonemes, and speaker identity is globally distributed.
2. **Linear Probes for Speech Representation** (Kamper et al.) - Demonstrates that voice conversion can be achieved by simple linear projections (PCA/SVD) between speaker subspaces, because phonemes reside in geometrically similar arrangements across speakers.

**Supports "only train a shifter"?** Strongly Supports. The fact that a single linear transformation matrix can map Speaker A's phoneme space to Speaker B's means a lightweight linear shifter is theoretically sufficient.
**Minimal Experiment:** Train a linear probe on layer 6 of WavLM to classify singers vs. speakers. Look at the weights to see what dimensions separate the domains.
**Feasibility:** Very High.

---

## 10. Evaluation Protocol for Dirty-Data Skill/Domain Conversion

### Core Papers
1. **Singing Voice Conversion Challenge (SVCC) 2025**
   - *Metrics:* Used 5-scale MOS for naturalness, 4-scale AB test for identity similarity (using multiple references), and a novel 4-scale XAB test for **Singing Style Similarity**.
   - *Objective:* Found that VERSA metrics (like SingMOS and speaker embedding cosine similarity) have >0.6 Spearman correlation with human judgments.

**Recommendation for Evaluation:**
Adopt the SVCC 2025 protocol: Use WavLM/Speaker embeddings for objective distance calculation, and implement an XAB test for style conversion (Is the output's skill more similar to the amateur source or the professional reference?).

---

## Final Synthesis

### Best Thesis Story
**"Geometric Skill Shifting: Transforming Novice to Professional via Linear Adapters on Frozen SSL Speech Backbones"**
The literature shows that SSL latents are highly structured and that domain/speaker traits can be altered via simple shifts (AdaIN, linear projections, domain-adversarial filtering). The thesis would prove that "skill" (professional vs. amateur) is an isolatable subspace, and shifting vectors along this axis yields professional singing/speaking without expensive full-model retraining. The inclusion of Ozuru et al. (2020) provides strong theoretical backing for F0-targeted shifts.

### Most Defensible Negative-Result Story
If the skill shifter fails, the thesis becomes: **"The Non-Linearity of Singing Expertise: Why Linear Latent Shifts Fail at Formant-F0 Coupling."** You can defend the failure by demonstrating (via representation geometry audits) that unlike speech identity, singing technique tightly couples F0 and vocal tract resonances, meaning "skill" cannot be untangled as an orthogonal vector in WavLM space.

### Best Demo-First Story
**The "Dirty Data Domain Filter & kNN-VC Matcher"**
Use Xin et al. (2020) and Du et al. (2022) to train a lightweight adversarial cleaner that strips dataset/mic/noise artifacts from scraped YouTube singing videos. Then, feed those clean latents into a training-free kNN-VC algorithm to clone voices. The demo allows users to upload garbage-quality audio and output studio-quality voice clones.

### Which Directions Should be Dropped
- **Direction 8 (Articulatory Representation):** While physically interesting, predicting kinematics adds a bottleneck that is likely unnecessary given how well WavLM/ContentVec disentangle content implicitly.
- **Direction 6 (Why Singing is Harder):** This is good for discussion but too theoretical to form the engineering core of the thesis. Focus on building the shifter first, and use Direction 6 to explain limitations.
