# Survey

- Date: 2026-06-01
- Task: 06-01-research-system-architecture

## Human-Readable Synthesis

### Direction Memo: Singing Transition Skill Representation

Date: 2026-06-02

The strongest research direction after the supervisor one-on-one is not general
"prosody" or static timbre shift. It is narrower and more defensible:

> Learn a disentangled representation of singing skill from local dynamic F0
> behavior around note transitions, then use that representation for singing
> quality assessment and controlled skill/style shifting.

This moves the project from static speaker/timbre embeddings toward a
performance-technique code. The target phenomena are local note-transition
behaviors such as pitch attack, portamento, glissando, overshoot, preparation,
legato continuity, scooping, and vibrato onset. These are closer to how humans
judge whether a singer sounds controlled or beginner-like than a whole-utterance
speaker embedding.

Relevant prior anchors:

- Saitou et al. show that F0 dynamic characteristics such as overshoot, vibrato,
  preparation, and fine fluctuation affect perceived singing quality, with
  overshoot especially important.
  Source: https://hdl.handle.net/10119/18075
- Nakano et al. evaluate singing skill without score information using pitch
  interval accuracy and vibrato features, reaching 83.5% average classification
  in a good/poor setup.
  Source: https://www.isca-archive.org/interspeech_2006/nakano06_interspeech.html
- GTSinger provides 80.59 hours of high-quality singing, 20 professional
  singers, nine languages, six technique annotations, manual alignments, music
  scores, and 16.16 hours of paired speech.
  Source: https://arxiv.org/abs/2409.13832
- SingMOS-Pro provides a modern singing-quality assessment benchmark with 7,981
  generated singing clips from 41 models and at least five ratings per clip.
  Source: https://arxiv.org/abs/2510.01812
- NaturalSpeech 3 and recent disentangled-codec work support the architecture
  idea: split audio into factorized subspaces rather than force one latent to
  carry content, prosody, timbre, and detail.
  Sources: https://arxiv.org/abs/2403.03100 and
  https://arxiv.org/abs/2508.08399
- AdaptVC supports the practical engineering pattern: use frozen SSL features
  plus trainable adapters to learn useful disentanglement without training a
  huge model from scratch.
  Source: https://arxiv.org/abs/2501.01347
- The existing project already has a Seed-VC singing-aware decoder path and
  objective cross-domain speaker evaluation. Seed-VC is useful as a baseline or
  downstream renderer because it supports zero-shot singing voice conversion
  with F0 conditioning.
  Source: https://arxiv.org/abs/2411.09943

### Proposed Core Method

Represent the singing signal with four separated parts:

```text
content / lyrics / phonemes
timbre / singer identity
global prosody / melody phrase shape
local transition skill code
```

The local transition skill code should be extracted from short windows around
note boundaries, not from the whole clip. Candidate inputs:

- F0 contour in cents relative to source and target notes;
- note onset/offset alignment from score or F0 segmentation;
- transition direction and interval size;
- portamento slope and curvature;
- overshoot magnitude and recovery time;
- pitch attack delay;
- preparation before note onset;
- vibrato onset delay, rate, extent, and regularity;
- voiced/unvoiced gap and legato continuity;
- energy and spectral stability around the transition.

The first model does not need to convert beginners into professionals. It should
first learn a representation that predicts or ranks transition skill while being
hard to use for singer ID, song ID, lyrics, and language.

### Training Signals

Use a multi-task/adversarial setup:

- Reconstruction or codec loss so the representation still carries enough
  acoustic information.
- Transition-quality classification/ranking/regression loss from human ratings
  or proxy labels.
- Technique label loss using GTSinger labels such as glissando and vibrato.
- Pitch/score-alignment losses for note center, interval, and boundary timing.
- Speaker adversarial loss on the skill code so singer ID is not recoverable.
- Song/lyrics/language adversarial losses so the skill code does not become a
  melody or text shortcut.
- Speaker/timbre classification or contrastive loss only on the timbre branch.
- Optional residual split: timbre branch captures speaker mean/std style, while
  transition residual captures dynamic technique deviations.

This matches the supervisor note: use the task/loss to guide the representation,
including auxiliary decoders/classifiers, but place each decoder on the branch
where the information should or should not live.

### Crowdsourced Score Filtering

The data collection should not trust raw average scores. Use a filtering layer:

- Collect pairwise preference and small rubric ratings, not only one MOS number.
  Useful rubric axes: pitch center accuracy, transition smoothness, attack
  confidence, legato continuity, vibrato control, strain/noise, and overall
  professionalness.
- Include gold/control clips: obvious professional, obvious off-pitch beginner,
  duplicated clips, and phase-inverted/order-swapped sanity checks.
- Remove raters with low agreement to gold/control items, very fast completion,
  low intra-rater consistency on duplicates, or constant-score behavior.
- Normalize rater bias with z-score or mixed-effects modeling before averaging.
- Keep uncertainty: train with confidence weights or ordinal/pairwise losses
  instead of pretending all averaged labels are equally reliable.
- Normalize by song, interval type, range, and gender/range class so the model
  does not learn that harder passages are automatically "worse."

For an MVP, use 5-7 raters per clip/window, discard unreliable raters, and train
with pairwise ranking over transition windows. Pairwise labels are likely easier
for non-expert listeners than absolute technical scores.

### Candidate Research Directions

#### 1. TransitionSkillCodec

Claim: a local transition code can predict perceived singing skill while being
invariant to singer identity, language, lyrics, and melody context.

MVP:

1. Use GTSinger score/F0/technique annotations.
2. Extract note-transition windows.
3. Train a frozen-SSL-plus-adapter encoder with disentanglement losses.
4. Evaluate whether the transition code predicts technique/quality while
   speaker ID and language classifiers fail from that code.

Why it is strongest: it directly matches the supervisor note and creates a
clear thesis contribution before attempting hard audio conversion.

#### 2. Score-Guided Skill Shifter

Claim: a trained singing-quality scorer can guide a generative model to shift
local transition behavior toward professional distributions while preserving
content, melody, and timbre.

MVP:

1. Train the transition scorer first.
2. Freeze a singing-capable decoder or VC model.
3. Optimize only a small adapter/transition-token branch using scorer loss plus
   identity/content preservation losses.
4. Demonstrate A/B outputs where attacks, overshoot, and legato improve without
   changing singer identity.

Risk: this is much harder than scoring because there is no paired
beginner-to-professional target. Treat it as phase two.

#### 3. Cross-Language Skill Invariance

Claim: transition skill features should transfer across languages better than
lyrics or timbre features. A good skill code should recognize controlled
portamento/overshoot/vibrato in English, Japanese, Chinese, etc.

MVP:

1. Train on a subset of languages in GTSinger.
2. Test technique/quality prediction on held-out languages.
3. Add language-adversarial training and measure whether it improves held-out
   language generalization.

This connects to the existing cross-language timbre work but shifts novelty away
from "speaker ID degrades under language/domain mismatch," which already has
prior work.

#### 4. VTuber Weak-Label Extension

Claim: after the controlled GTSinger proof, noisy VTuber clips can expand style
diversity using weak scoring and confidence filtering.

MVP:

1. Use the existing VTuber clean_candidate bucket only as unlabeled or weakly
   labeled data.
2. Run F0/transition extraction and a pretrained transition scorer.
3. Keep high-confidence windows; reject clips with backing vocals, unstable F0,
   multi-speaker contamination, or low rater/model agreement.

This should not be the first proof because VTuber audio is noisy and licensing
is more sensitive, but it is a good later demo/data-mining contribution.

### Recommended Thesis Path

Best first title:

```text
Disentangled Transition-Skill Representation Learning for Singing Voice
Assessment and Control
```

Concrete first research question:

```text
Can we learn a local singing-transition representation that predicts perceived
skill/technique while removing singer identity, lyrics, language, and global
melody shortcuts?
```

Concrete first experiment:

```text
Dataset: GTSinger
Unit: note-transition windows
Input: F0 + SSL/acoustic features around each transition
Labels: technique labels, score-derived transition attributes, small human or
proxy quality labels
Model: frozen SSL encoder + small adapters + adversarial disentanglement heads
Evaluation:
  - transition quality / technique prediction
  - speaker ID leakage from skill code
  - language/song leakage from skill code
  - held-out singer and held-out language generalization
  - correlation with human preference on transition windows
```

The conversion idea should remain in scope, but as a second-stage payoff:

```text
Once the transition-skill code and scorer are valid, use them as a differentiable
loss or guidance signal for a singing-capable decoder to improve beginner-like
transitions.
```

### What Not To Claim

- Do not claim that speaker recognition degradation on singing or language
  mismatch is new. JukeBox and other work already cover that broad observation.
- Do not claim full beginner-to-professional conversion before a scorer and
  representation are validated.
- Do not use raw crowdsourced MOS as ground truth without rater filtering and
  uncertainty modeling.
- Do not train the first model on noisy VTuber data as the main evidence. Use
  controlled corpora first, then VTuber data as a weak-label extension.

## Open Questions

- Which exact F0 tracker/alignment tool should define note-transition windows
  for the first GTSinger experiment?
- Should the first label be technique classification, pairwise human preference,
  or a proxy transition-quality score derived from pitch/score alignment?
- Which frozen representation is the best first backbone: WavLM/HuBERT,
  EnCodec/DAC/Descript codec, or a Seed-VC internal representation?
