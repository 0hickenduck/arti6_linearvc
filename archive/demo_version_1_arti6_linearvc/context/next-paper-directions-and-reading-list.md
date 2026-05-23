# Next paper directions after ARTI-6 LinearVC probe

Date: 2026-05-20

## Current conclusion from our experiments

Our ARTI-6 6D LinearVC experiments produced a useful negative result:

- `source_arti + target_spk` gives a strong embedding-only VC baseline.
- `target_arti + source_spk` follows target phonetic/articulatory content more than target timbre.
- `linear(source_arti) + source_spk` does not produce reliable target timbre; diagonal/full/ridge/alpha transforms mostly damage intelligibility.
- Adding target speaker embedding in hybrid conditions makes the output sound more target-like, but the timbre change is mainly from `spk_emb`, not the 6D affine transform.

Interpretation:

```text
ARTI-6 6D features are better treated as an articulatory / phonetic-content bottleneck.
They are not currently a timbre transformation space.
```

This is not just a failure. It gives us a sharper question:

```text
Why does LinearVC work in high-dimensional SSL acoustic feature spaces,
but not in ARTI-6's low-dimensional articulatory bottleneck?
```

## Strongest paper framing

The project should pivot from "make ARTI-6 pure LinearVC work" to:

```text
Representation choice determines whether linear voice conversion is possible.

SSL features keep speaker and content information entangled but linearly movable.
ARTI-6 intentionally compresses toward articulatory-content trajectories and relies on
speaker embedding for speaker individuality.
```

This can become a representation-probing paper/demo without training a large model.

## Reading list and why each matters

### 1. ARTI-6: Towards Six-dimensional Articulatory Speech Encoding

Link: https://arxiv.org/abs/2509.21447

What it does:

- Defines the 6D ARTI representation from vocal-tract regions.
- Uses speech foundation models for articulatory inversion.
- Synthesizes from 6D articulatory features with speaker conditioning.

Why we read it:

- It is our tested representation.
- The important point is not "ARTI-6 fails"; it is that ARTI-6 is designed as a compact articulatory-content code, with speaker individuality supplied elsewhere.

Question to extract:

- Does the paper explicitly evaluate speaker leakage in 6D features?
- How much of speaker/accent/prosody is claimed to remain in the 6D bottleneck?

### 2. LinearVC: Linear transformations of self-supervised features through the lens of voice conversion

Link: https://arxiv.org/abs/2506.01510

What it does:

- Applies simple linear transformations to self-supervised speech features.
- Reports that even rotations can perform high-quality VC in SSL feature space.
- Uses the success of VC as a probe of SSL representation geometry.

Why we read it:

- This is the positive contrast to our ARTI-6 negative result.
- Its core claim depends on the SSL feature space retaining speaker/timbre degrees of freedom.

Experiment implication:

- Replicate a small WavLM LinearVC baseline on our same CMU ARCTIC split.
- Compare it directly with ARTI-6 affine transforms.

### 3. kNN-VC: Voice Conversion With Just Nearest Neighbors

Link: https://arxiv.org/abs/2305.18975

What it does:

- Extracts self-supervised representations from source and target reference speech.
- Converts by replacing each source frame with a nearest-neighbor target feature.
- Uses a pretrained vocoder to synthesize from converted SSL features.

Why we read it:

- It is another minimal SSL-space VC baseline.
- It does not require us to train a big model.
- It can test whether nearest-neighbor target feature substitution works where ARTI-6 affine transforms fail.

Experiment implication:

- Run or reimplement a tiny kNN-VC baseline if dependencies are feasible.
- Use it as the "SSL representation has target-speaker geometry" demonstration.

### 4. SPARC: Coding Speech through Vocal Tract Kinematics

Link: https://arxiv.org/abs/2406.12998

What it does:

- Builds a speech articulatory coding framework around vocal-tract kinematics and source features.
- Uses articulatory analysis and synthesis for high-quality speech coding.
- Includes speaker identity encoding and claims speaker embedding can be disentangled from articulations for accent-preserving zero-shot VC.

Why we read it:

- It is the closest sibling to ARTI-6 but more VC-oriented.
- It includes source features and larger-scale training, so it may explain what ARTI-6's 6D bottleneck is missing.

Experiment implication:

- Compare ARTI-6 with SPARC conceptually:
  - ARTI-6: 6D ROI-derived articulatory bottleneck + ECAPA speaker embedding.
  - SPARC: articulatory/source-feature coding + speaker identity encoder + VC objective.
- If SPARC code/assets are accessible, it may be a better articulatory baseline than ARTI-6 for VC.

### 5. RT-VC: Real-Time Zero-Shot Voice Conversion with Speech Articulatory Coding

Link: https://arxiv.org/abs/2506.10289

What it does:

- Extends speech articulatory coding into real-time zero-shot VC.
- Uses articulatory feature space plus DDSP-style efficient vocoding.

Why we read it:

- It shows what an articulatory-VC system needs beyond a tiny 6D trajectory.
- It is useful for understanding low-latency, source-filter-like articulatory decoding.

Experiment implication:

- Read for architecture, not necessarily to reproduce first.
- Extract what variables they keep separate: articulation, source, speaker identity, vocoder.

### 6. AutoVC: Zero-Shot Voice Style Transfer with Only Autoencoder Loss

Link: https://arxiv.org/abs/1905.05879

What it does:

- Uses an autoencoder with a carefully designed bottleneck to remove speaker information from content.
- Recombines content code with a target speaker embedding for VC.

Why we read it:

- It is the classic "content bottleneck + speaker embedding" framing.
- It helps us interpret ARTI-6: if 6D ARTI is an extreme content bottleneck, then expecting pure timbre conversion from it is structurally wrong.

Experiment implication:

- Our speaker-predictability audit is the direct test: does ARTI-6 look like a content bottleneck?

### 7. SpeechSplit / SpeechSplit 2.0

Link: https://arxiv.org/abs/2203.14156

What it does:

- Disentangles speech into content, rhythm, pitch, and timbre.
- SpeechSplit 2.0 uses signal-processing constraints to avoid fragile bottleneck tuning.

Why we read it:

- It gives a vocabulary for decomposing what our ARTI-6 experiment confuses:
  - content/articulation
  - rhythm/duration
  - pitch/source
  - timbre/speaker

Experiment implication:

- Our future diagnostics should not treat all failure as one dimension.
- We should separately measure content preservation, speaker similarity, pitch/source behavior, and trajectory distortion.

### 8. ACE-VC: Adaptive and Controllable Voice Conversion using Explicitly Disentangled SSL Representations

Link: https://arxiv.org/abs/2302.08137

What it does:

- Uses SSL representations but explicitly disentangles linguistic content, speaker characteristics, and speaking style.
- Uses pitch-shifted audio and a Siamese loss to remove speaker information from content embeddings.

Why we read it:

- It is a bridge between SSL VC and disentanglement.
- It makes a key point for our paper: SSL features are not automatically clean; models often have to explicitly control leakage.

Experiment implication:

- Our paper can contrast:
  - LinearVC: exploit retained speaker geometry in SSL space.
  - ACE-VC/AutoVC: remove speaker information for controllable synthesis.
  - ARTI-6: already strongly bottlenecked toward articulation/content.

### 9. WORLD / source-filter acoustic features

Reference implementation: https://github.com/mmorise/World

What it does:

- Decomposes speech into F0, spectral envelope, and aperiodicity, then resynthesizes.

Why we read it:

- It is closer to the original intuition of changing vocal-tract resonance or vocal-source parameters.
- If we want "small, interpretable transformations" without training a large neural decoder, source-filter features are a better target than ARTI-6 6D trajectories.

Experiment implication:

- Build a lightweight baseline:
  - keep source content/timing
  - apply simple F0 normalization or spectral-envelope/formant warping
  - resynthesize with WORLD
- This tests whether classical acoustic control gives more timbre movement with less content damage.

## Three concrete experiment tracks

### Track A: Representation audit, no VC synthesis required

Goal:

Quantify what ARTI-6 and WavLM retain.

Experiments:

1. Speaker predictability:
   - Input: utterance-level summaries of ARTI-6 6D features vs WavLM features.
   - Model: logistic regression / linear SVM.
   - Target: speaker ID.
   - Hypothesis: WavLM predicts speaker more easily than ARTI-6.

2. Same-prompt distance:
   - Compare same-prompt cross-speaker distance vs different-prompt same-speaker distance.
   - Do this in ARTI-6 and WavLM spaces.
   - Hypothesis: ARTI-6 clusters more by content/prompt; WavLM retains more speaker separation.

3. Perturbation sensitivity:
   - Add controlled perturbations to ARTI-6 dimensions.
   - Measure ASR/WER if available, speaker-similarity if available, and subjective intelligibility.
   - Hypothesis: small perturbations affect content faster than timbre.

Why this is paper-worthy:

It turns our failed VC demo into a representation analysis result.

### Track B: SSL LinearVC contrast on the same split

Goal:

Show that the failure is representation-specific, not caused only by our paired data or linear method.

Experiments:

1. Extract WavLM layer features for the same CMU ARCTIC `bdl -> slt` pairs.
2. Fit the same linear maps:
   - mean/std
   - diagonal affine
   - full affine / ridge affine
   - optional orthogonal transform if easy
3. Use a pretrained SSL-feature vocoder if feasible, or use existing kNN-VC/LinearVC tooling.
4. Compare to ARTI-6 6D transforms on the same train/test split.

Expected result:

WavLM/SSL features should produce stronger voice conversion than ARTI-6 transforms because the SSL space retains speaker/timbre degrees of freedom.

Risk:

The available vocoder/tooling may take setup time. If setup is heavy, use kNN-VC first because it already provides trained artifacts/code paths.

### Track C: Interpretable acoustic controls instead of ARTI-6 timbre controls

Goal:

Test the original intuition of "small interpretable transformation changes voice" in a better feature space.

Experiments:

1. WORLD analysis of source and target:
   - F0
   - spectral envelope
   - aperiodicity
2. Simple transforms:
   - F0 mean/std normalization source -> target
   - spectral-envelope warping or mel-cepstral mean shift
   - McAdams coefficient / formant-like warping if available
3. Resynthesize and package demos.

Expected result:

This may change perceived timbre more directly than ARTI-6 6D transforms, while preserving source content better than off-manifold articulatory perturbations.

Why this matters:

It gives us a lightweight, no-big-model path to test interpretable voice manipulation.

## Proposed reading order

1. ARTI-6: understand what we tested and what it did not claim.
2. LinearVC and kNN-VC: understand the positive SSL-space baseline.
3. SPARC and RT-VC: understand articulatory coding systems that are actually VC-oriented.
4. AutoVC, SpeechSplit, ACE-VC: understand disentanglement and bottleneck design.
5. WORLD/source-filter: design small interpretable acoustic baselines.

## Recommended next implementation step

Do Track A first.

Reason:

- It is cheap.
- It does not require a new decoder or vocoder.
- It directly tests the representation hypothesis that emerged from our listening experiments.
- It will tell us whether Track B is the right contrast and whether Track C is necessary.

Minimum useful artifact:

```text
outputs/representation_audit/
  arti6_vs_wavlm_speaker_predictability.json
  same_prompt_distance_summary.json
  plots/
  report.html
```

If Track A confirms that ARTI-6 strips speaker information while WavLM retains it, the next paper storyline becomes concrete:

```text
Linear voice conversion requires a representation that still contains speaker geometry.
ARTI-6 is valuable precisely because it collapses toward articulatory content,
but this makes it the wrong space for pure LinearVC.
```
