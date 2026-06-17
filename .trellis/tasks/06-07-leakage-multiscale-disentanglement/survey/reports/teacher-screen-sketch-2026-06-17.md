# Teacher Meeting Screen Sketch

Date: 2026-06-17

## Big Picture

I am considering two related research directions in singing voice / speech-singing representation learning.

The common theme is:

> Modern speech/singing models do not just contain "content" and "speaker
> timbre"; they may also contain technique, singing mode, and stable identity
> information in a mixed way. I want to measure and control these factors with
> small-GPU experiments.

## Direction 1: From General Singing Skill To Specific Technique Adaptation

### Core Idea

Instead of predicting a vague "singing skill" score, focus on concrete singing
techniques:

- vibrato;
- breathy voice;
- falsetto;
- glissando;
- mixed voice;
- pharyngeal voice.

### Dataset

GTSinger:

- singing technique labels;
- fine-grained / phone-level annotations;
- paired speech is also useful for the second direction.

### First Question

Do these techniques appear as structure in frozen latent representations?

Possible first checks:

- clustering / visualization;
- linear probing;
- analogy-style vector tests, inspired by phonological vector arithmetic such
  as `[b] - [p] ~= [d] - [t]`.

### Important Uncertainty

It is not proved that singing techniques are linear directions.

If they are linear:

- vector arithmetic or centroid differences may work.

If they are not linear:

- use nonlinear probes;
- use small adapters;
- use FiLM / cross-attention conditioning;
- evaluate by downstream controllability rather than only linear separability.

### Possible Downstream Direction

Train a lightweight technique-conditioned modifier:

- label token / prompt;
- FiLM;
- cross-attention;
- LoRA or other low-rank adapter.

Goal:

> Can a model use a technique label to modify representation or generation in
> the intended direction?

## Direction 2: Speech-Singing Timbre Shift

### Core Idea

The same person's speech and singing can sound very different, but there may
still be some stable identity / timbre core.

Question:

> After accounting for obvious factors like F0, energy, duration, and phonetic
> content, is there still a speech-to-singing timbre residual?

### Why This Matters

Speech-prompted singing voice conversion is useful because target singing
references are often unavailable.

If we can understand the speech-to-singing shift, we may explain why speech
references and singing references behave differently in SVC.

### First Experiment

Use same-person speech/singing data:

- JVS + JVS-MuSiC;
- NHSS;
- GTSinger paired speech/singing.

Measure frozen representations:

- WavLM / HuBERT / ContentVec / Whisper;
- speaker or singer identity embeddings;
- possibly FACodec streams.

Check:

- speech vs singing separability;
- same-person speech-to-singing retrieval;
- cosine gap between speech and singing;
- whether the signal remains after F0 / energy / duration controls.

### Central Difficulty

F0 is extremely dominant in singing.

If we remove too much acoustic information, nothing meaningful may remain.

So the technical question is not simply "delete pitch." It is:

> What control method removes trivial pitch/duration cues without destroying
> the timbre information we actually want to study?

Possible controls:

- compare raw features vs F0-controlled features;
- residualize only a small nuisance set: F0 mean/std, energy, duration,
  voiced ratio;
- match samples by phone or F0 range when possible;
- start with same-phone vowel regions if alignments allow;
- report whether the residual survives instead of assuming it will.

### Possible Downstream Direction

If a stable residual exists:

- compare speech prompt vs singing prompt in Seed-VC;
- test average speech-to-singing residual;
- test predicted residual from target speech;
- ask whether the residual improves target singer similarity.

## Current Preference

Main thesis candidate:

> Direction 2: speech-singing timbre shift.

Backup / parallel pilot:

> Direction 1: concrete technique adaptation with GTSinger.

Reason:

- Direction 2 has a clearer small first experiment and direct connection to
  speech-prompted SVC.
- Direction 1 is promising, but the linearity and controllability of technique
  directions must be tested.

## Questions For Teacher

1. Which direction sounds more suitable as the main thesis direction?
2. For speech-singing timbre shift, what confounds must be controlled first:
   F0, duration, phonetic content, channel, or something else?
3. For technique adaptation, is probing enough, or is downstream synthesis /
   control required?
4. Which dataset should I start with for a fast pilot?
