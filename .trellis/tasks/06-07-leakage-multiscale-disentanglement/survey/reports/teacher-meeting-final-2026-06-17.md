# Teacher Meeting Notes

Date: 2026-06-17

## Main Message

I am considering two research directions in speech/singing representation
learning. Both are small-GPU directions. The common idea is to study what
information is mixed inside modern audio representations: content, timbre,
singing technique, singing mode, and stable identity.

My current preference is:

- **Main thesis candidate:** speech-singing timbre shift.
- **Backup / parallel pilot:** GTSinger technique adaptation.

## Direction 1: From General Singing Skill To Specific Technique Adaptation

### Idea

Instead of predicting a vague "singing skill" score, focus on concrete
techniques:

- vibrato;
- breathy voice;
- falsetto;
- glissando;
- mixed voice;
- pharyngeal voice.

### Dataset

Use **GTSinger**, because it has technique labels and fine-grained annotations.

### Research Question

Do singing techniques appear as structure in frozen latent representations?

First checks:

- clustering / visualization;
- linear probing;
- analogy-style vector tests, inspired by phonological vector arithmetic;
- if linear direction fails, try nonlinear probes or lightweight adapters.

### Possible Architecture Direction

If technique information is useful, train a small technique-conditioned modifier:

- label token / prompt;
- FiLM;
- cross-attention;
- LoRA or other low-rank adapter.

The key question becomes:

> Can a model use a technique label to modify representation or generation in
> the intended direction?

### Main Risk

It is not guaranteed that techniques such as vibrato or breathiness are linear
directions. If they are not linear, the project should move from "linear
direction discovery" to "controllable technique conditioning."

## Direction 2: Speech-Singing Timbre Shift

### Idea

The same person's speech and singing can sound very different, but there may
still be a stable identity / timbre core.

### Research Question

After accounting for obvious factors such as F0, energy, duration, and phonetic
content, is there still a speech-to-singing timbre residual?

### Why It Matters

Speech-prompted singing voice conversion is useful because target singing
references are often unavailable. If we understand the speech-to-singing shift,
we may explain why speech references and singing references behave differently
in SVC.

### First Experiment

Use same-person speech/singing data:

- JVS + JVS-MuSiC;
- NHSS;
- GTSinger paired speech/singing.

Extract frozen representations:

- WavLM / HuBERT / ContentVec / Whisper;
- speaker or singer identity embeddings;
- possibly FACodec streams.

Measure:

- speech vs singing separability;
- same-person speech-to-singing retrieval;
- cosine gap between speech and singing;
- whether the signal remains after F0 / energy / duration controls.

### Central Technical Difficulty

F0 is very dominant in singing. If we remove too much acoustic information,
maybe nothing meaningful remains.

So the real technical question is:

> How can we control trivial pitch and duration cues without destroying the
> timbre information we want to study?

Possible controls:

- compare raw features with controlled features;
- residualize only simple nuisance variables such as F0 mean/std, energy,
  duration, and voiced ratio;
- match samples by phone or F0 range when possible;
- start with same-phone vowel regions if alignments allow;
- report whether the residual survives, instead of assuming it will.

### Possible Architecture Direction

If a stable residual exists:

- compare speech prompt vs singing prompt in Seed-VC;
- test average speech-to-singing residual;
- test predicted residual from target speech;
- possibly train a small adapter / LoRA module;
- optionally use Gradient Reversal Layer to suppress F0 or duration shortcuts
  while preserving identity or technique.

## Current Preference

I currently prefer **Direction 2** as the main thesis direction because:

- it has a clearer first experiment;
- it connects directly to speech-prompted SVC;
- it can produce a useful result even if the final intervention fails;
- it has a clear failure condition: if the residual disappears after controls,
  we should pivot.

Direction 1 is still valuable as a backup or parallel pilot, especially if
speech-singing timbre residuals collapse under F0/duration controls.

## Questions For Teacher

1. Which direction sounds more suitable as the main thesis direction?
2. For speech-singing timbre shift, which confounds should I control first:
   F0, duration, phonetic content, channel, or something else?
3. For technique adaptation, is probing enough, or would a synthesis/control
   experiment be necessary?
4. Which dataset should I start with for the fastest credible pilot?

## If Asked: Technical Details

### Residualization vs GRL

Residualization is the clean analysis baseline:

> Does the signal still exist after controlling simple nuisance variables?

Gradient Reversal Layer / LoRA is the later architecture stage:

> Can a small trainable adapter keep the target information while making F0,
> duration, or source identity harder to predict?

I should not present GRL as a replacement for residualization. They answer
different questions.

### GRL With Frozen Models

The base encoder can stay frozen:

```text
audio -> frozen encoder -> h -> adapter / LoRA -> z

z -> target head
z -> GRL -> nuisance head
```

Only the adapter / LoRA / projection module is trained.

### Important Ablations

- no control;
- linear residualization;
- matched phone/F0 cohort;
- adapter without GRL;
- adapter with GRL;
- check remaining nuisance leakage with both linear and nonlinear probes.

### Main Warning

Probe accuracy or adversarial failure does not prove true disentanglement. The
project should report a utility-leakage tradeoff: how much target information
is preserved while nuisance information is reduced.
