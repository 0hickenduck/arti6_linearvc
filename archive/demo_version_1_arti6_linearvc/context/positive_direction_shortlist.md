# Positive direction shortlist after stopping ARTI-only LinearVC

Date: 2026-05-20

## Goal

Find a positive project direction that does not spend more time proving the ARTI-6 negative result.

Current constraint:

```text
Prefer pretrained models, inference-time transforms, small linear/statistical modules,
or lightweight adapters. Avoid training a large decoder unless the direction is clearly worth it.
```

## Rank 1: speaker embedding steering inside ARTI-6

### Core idea

Since ARTI-6 timbre follows the speaker conditioning path, use that path as the actual control space:

```text
fixed ARTI content + moved speaker embedding -> controllable voice identity / attributes
```

### Concrete experiments

1. **Interpolation demo**
   - Fix one ARTI sequence.
   - Interpolate `spk = (1-alpha) * spk_A + alpha * spk_B`.
   - Listen for smooth timbre transition and check content stability.

2. **Attribute directions**
   - Build speaker embedding pools from metadata-rich datasets such as VCTK / LibriTTS.
   - Compute directions:
     - gender: `mean(female) - mean(male)`
     - pitch range: `mean(high_f0) - mean(low_f0)`
     - maybe age if metadata exists
   - Apply `spk' = spk + beta * direction`.

3. **Local-manifold pseudonym voices**
   - For a speaker embedding, find nearest neighbors in a speaker pool.
   - Interpolate locally to make a pseudo-speaker.
   - Goal: change identity without leaving the natural speaker manifold.

### Why this is better than ARTI linear transforms

It attacks the actual timbre path instead of a content path.

### Minimum artifact

An audio grid:

```text
same ARTI content
columns = alpha along speaker interpolation / attribute direction
rows = different source sentences
```

Plus objective diagnostics:

```text
speaker cosine to A/B
F0 statistics
ASR transcript stability
```

### Paper/demo value

Demo value is high. Paper value depends on whether embedding movement is smooth, controllable, and natural. If yes, the paper framing could be:

```text
Controllable speaker identity editing in an articulatory-content-conditioned synthesizer.
```

### Main risk

ECAPA speaker embeddings may not be a good generative latent space. Linear moves can go off-manifold and produce artifacts.

### My verdict

Best first experiment. It is cheap, directly follows our discovery, and can fail fast.

## Rank 2: source-filter physical timbre knobs

### Core idea

Use classical acoustic decompositions for what ARTI could not do:

```text
F0 / spectral envelope / formants / aperiodicity -> interpretable timbre controls
```

### Concrete experiments

1. **WORLD F0 mean/std mapping**
   - Preserve source timing/content.
   - Map source F0 distribution to target F0 distribution.

2. **VTLN / vocal-tract-length warping**
   - Warp WORLD spectral envelope frequency axis.
   - Slider controls perceived body size / resonance.

3. **McAdams coefficient**
   - Use LPC pole-angle warping to shift formants.
   - This is a known voice anonymization baseline and gives a one-parameter voice-change knob.

4. **Spectral anchor matching**
   - Keep lower content-critical formants more stable.
   - Warp higher resonance regions more aggressively.
   - Goal: identity change with less intelligibility damage.

### Why this is better than ARTI linear transforms

It manipulates acoustic filter/source parameters, not articulatory content trajectory. This matches the original intuition of changing vocal tract resonance.

### Minimum artifact

An interactive or static demo:

```text
original
F0 mapped
VTLN alpha sweep
McAdams alpha sweep
combined F0 + VTLN
```

With plots:

```text
spectrogram before/after
F0 contour before/after
estimated formant shift
```

### Paper/demo value

Strong demo value. Paper value is medium unless we add a new twist such as "content-anchored spectral warping" or a careful comparison with neural embedding steering.

### Main risk

Audio quality may sound classical / buzzy / metallic. But that is acceptable for an interpretable baseline.

### My verdict

Second-best first experiment. It is extremely implementable and gives immediate listening feedback.

## Rank 3: SSL-space small method, not reproduction

### Core idea

Use WavLM/kNN-VC tooling but add a small method instead of reproducing kNN-VC:

```text
retrieval / linear algebra over SSL features -> new conversion behavior
```

### Concrete experiments

1. **Delta-VC**
   - Compute `delta = mean(target_wavlm) - mean(source_wavlm)`.
   - Convert `Z' = Z_source + alpha * delta`.
   - This is the simplest "speaker vector arithmetic" test in SSL feature space.

2. **Locally linear kNN-VC**
   - Replace hard kNN frame averaging with constrained local interpolation.
   - Goal: reduce discrete retrieval jitter while staying non-parametric.

3. **Optimal-transport VC**
   - Replace framewise greedy nearest neighbors with a global transport plan.
   - Goal: avoid many source frames collapsing onto the same target frames.

### Why this is interesting

This could become a real method paper if one variant improves kNN-VC/LinearVC tradeoffs.

### Minimum artifact

First just get official kNN-VC running on our examples. Then add one variant:

```text
kNN-VC baseline
Delta-VC alpha sweep
locally-linear kNN variant
```

### Paper/demo value

Potentially high, but only after baseline tooling works. It is farther from the ARTI result, but more likely to be accepted as a VC method if the audio improves.

### Main risk

This can quickly become "yet another kNN-VC variant" unless the improvement is clear.

### My verdict

Good second-stage paper route. Not the first thing I would implement unless we decide to leave ARTI-6 completely.

## Rank 4: ARTI for accent / pronunciation editing

### Core idea

Use ARTI where it is strong:

```text
phonetic-articulatory content editing, not timbre editing
```

### Concrete experiments

1. **Accent / pronunciation correction**
   - Use L2-ARCTIC or similar.
   - Identify mispronounced segments.
   - Move local ARTI trajectory toward native reference.
   - Resynthesize with same speaker embedding.

2. **Local phone editing**
   - Pick vowel/consonant windows.
   - Manually perturb specific ARTI channels.
   - Goal: controlled phone-level changes while speaker identity stays stable.

3. **Emotion/prosody hybrid**
   - Keep source ARTI content.
   - Transfer F0/rhythm from emotional target.
   - Use same speaker ID.

### Why this is a better ARTI direction

It treats ARTI as a content/articulation editor, which matches the model.

### Paper/demo value

Potentially high, especially accent/pronunciation correction. But it needs the right dataset and segment-level evaluation, so it is not the fastest first demo.

### Main risk

Hybrid ARTI trajectories may go off-manifold; evaluation may require phoneme alignment and human listening.

### My verdict

Promising long-term. Do not start here unless the user specifically wants an accent/pronunciation project.

## Rank 5: dynamic speaker embeddings

### Core idea

Instead of one static speaker embedding for the whole utterance, use a time-varying embedding sequence:

```text
spk(t) from sliding reference windows -> richer local timbre texture
```

### Why it is interesting

It attacks a real limitation: speaker identity is global but timbre has local variation.

### Why not first

The ARTI-6 decoder may only accept or behave well with static global embeddings. If it accepts `(T, D)` conditioning, this becomes interesting; otherwise it requires model surgery.

### Verdict

High concept value, but implementation risk is higher than simple embedding interpolation.

## My suggested next move

Start with a two-prong probe:

```text
Probe 1: ARTI fixed + speaker embedding interpolation / attribute direction
Probe 2: WORLD fixed content + VTLN/McAdams/F0 sliders
```

Reason:

- Both produce immediate audio.
- Both are consistent with the lesson from ARTI-only failure.
- Neither needs large model training.
- Together they compare two control spaces:
  - learned speaker embedding space
  - physical source-filter acoustic space

If one sounds promising, we deepen that branch. If both fail, we pivot to SSL-space kNN/LinearVC variants.

## Sources checked

- ARTI-6: https://arxiv.org/abs/2509.21447
- LinearVC: https://arxiv.org/abs/2506.01510
- kNN-VC: https://arxiv.org/abs/2305.18975
- kNN-VC official repo: https://github.com/bshall/knn-vc
- SPARC: https://arxiv.org/abs/2406.12998
- RT-VC: https://arxiv.org/abs/2506.10289
- Accent Conversion with Articulatory Representations: https://arxiv.org/abs/2406.05947
- WORLD / PyWORLD: https://github.com/JeremyCCHsu/Python-Wrapper-for-World-Vocoder
- VoicePrivacy McAdams baseline: https://www.voiceprivacychallenge.org/docs/VoicePrivacy_2024_Eval_Plan_v2.1.pdf
- Controllable artificial speaker embeddings: https://www.isca-archive.org/interspeech_2023/lux23_interspeech.pdf
