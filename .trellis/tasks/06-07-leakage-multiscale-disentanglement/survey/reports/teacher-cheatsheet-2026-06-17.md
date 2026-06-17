# Research Direction Cheat Sheet For Teacher Meeting

Date: 2026-06-17

## One-Sentence Framing

I am choosing between two small-GPU speech/singing research directions:

1. **Technique/style control in singing representations**: use GTSinger labels
   such as vibrato, breathy, falsetto, and glissando to study whether modern
   frozen representations contain controllable technique directions.
2. **Speech-vs-singing timbre shift**: study whether same-person speech and
   singing differ beyond obvious F0, energy, duration, and content effects, and
   whether that residual explains failures in speech-prompted singing voice
   conversion.

Recommended priority: present both, but make **Direction 2** the main thesis
candidate and **Direction 1** the backup or parallel pilot.

## Direction 1: Technique / Style Control With GTSinger

### Research Question

Can frozen audio representations encode singing techniques such as vibrato,
breathy voice, falsetto, glissando, mixed voice, and pharyngeal voice in a way
that is separable from singer identity, phonetic content, F0, and song context?

If such directions exist, can they be used as controllable conditioning signals
for singing voice generation or conversion?

### Why It Is Interesting

- The recent SVC/SVS field is moving from only timbre conversion toward
  **style and technique control**.
- GTSinger provides technique labels at a fine granularity, so it supports
  controlled experiments that are not possible with only global song-level
  labels.
- A successful result could become a useful technique-control or
  technique-preservation evaluation direction.

### Small Experiments

1. **Clustering / visualization**
   - Extract frozen representations from GTSinger.
   - Run K-means, PCA, UMAP, or t-SNE.
   - Ask whether clusters align with technique labels.
   - Important caveat: clustering is only exploratory. Clusters may instead
     reflect singer, phone, F0, language, or song.

2. **Linear probing**
   - Train simple classifiers to predict technique labels from frozen
     representations.
   - Use leave-singer-out splits.
   - Compare raw features against features with F0/energy/duration controls.
   - This is stronger evidence than clustering.

3. **Technique direction / vector arithmetic**
   - Do not define a direction as `mean(vibrato) - mean(speech)`, because that
     mixes technique with speech/singing mode.
   - Better definition:
     `mean(vibrato singing) - mean(non-vibrato or control singing)`, matched by
     singer, phone, F0 range, and duration where possible.
   - Test whether adding this direction changes a probe's prediction or a
     downstream synthesis model's output.

4. **Conditioned lightweight adapter**
   - Train a small adapter over frozen or intermediate representations.
   - Input condition: technique label or phone-level technique tag.
   - Output: a representation modifier, for example FiLM scale/shift or a
     low-rank adapter update.
   - Compare conditioning methods: label token prompting, FiLM, cross-attention,
     and possibly label-conditioned LoRA/adapters.

### FiLM vs Cross-Attention Clarification

**FiLM** means a condition network maps the technique label embedding to
feature-wise scale and shift parameters:

```text
h'_t = gamma(label_t) * h_t + beta(label_t)
```

- Basic FiLM uses only the label embedding to generate `gamma` and `beta`.
- The same modifier can be applied to all frames in a labeled span.
- If labels are phone-level, each frame can use the tag of its phone or segment.
- If the frame itself is also fed into the modifier network, the method becomes
  a more powerful dynamic adapter, not the simplest FiLM baseline.

**Cross-attention** lets frame hidden states attend to one or more condition
tokens:

```text
query = frame hidden state
key/value = technique-label embedding tokens
```

- The label and frame dimensions do not need to match initially because learned
  projection matrices map them into a shared attention dimension.
- If there is only one global label token, cross-attention may behave like a
  heavier broadcast condition.
- Cross-attention becomes more useful when conditions are multiple,
  time-varying, or hierarchical, such as technique plus singer plus lyrics.

**Recommended comparison**

Start with the simplest conditioning baseline first:

1. label embedding concatenation or additive bias;
2. FiLM;
3. cross-attention;
4. label-conditioned low-rank adapter only if the simple baselines work.

### Main Risks

- Technique labels may be entangled with singer identity or song content.
- Vibrato, glissando, and breathiness are dynamic; global utterance embeddings
  may hide the time-varying pattern.
- A classifier result is not enough. The stronger claim requires transfer,
  intervention, or downstream synthesis evidence.

## Direction 2: Speech-Vs-Singing Timbre Shift

### Research Question

For the same person, how much of the difference between speech and singing
remains after controlling for F0, energy, duration, phonetic content, and
recording/channel factors?

If a residual remains, does it explain why speech references and singing
references behave differently in zero-shot singing voice conversion?

### Why It Is Interesting

- Voice conversion often treats timbre as a stable speaker identity, but the
  same person's speaking and singing voices are not identical.
- Speech-prompted SVC is useful in practice because target singing references
  are often unavailable.
- The project can stay small-GPU: frozen features, probes, retrieval,
  residualization, and only a small Seed-VC stress test.

### Stage A: Frozen Representation Audit

1. Collect same-person speech/singing data.
   - Candidate data: JVS + JVS-MuSiC, NHSS, and/or GTSinger paired speech.
2. Extract frozen representations.
   - WavLM, HuBERT/ContentVec, Whisper, speaker/singer embedding models, and
     possibly FACodec streams.
3. Measure:
   - speech/singing mode AUC;
   - residualized mode AUC;
   - speech-to-singing identity retrieval Recall@1/Recall@5;
   - singing-to-speech identity retrieval;
   - same-person speech/singing cosine gap.
4. Control nuisance variables.
   - F0 mean/std, voiced ratio, energy mean/std, duration, SNR/channel proxy,
     and phonetic/content effects where alignments allow.

### How To "Regress Out" F0, Energy, And Duration

The goal is not to delete all acoustic information. The goal is to ask whether
the representation still contains speech/singing or identity information after
removing what can be linearly or predictably explained by nuisance variables.

Simple residualization:

1. For every audio crop, compute nuisance features:
   F0 mean/std, voiced ratio, energy, duration, maybe SNR or spectral centroid.
2. Fit a regression from nuisance features to each representation dimension on
   the training set.
3. Replace the representation with:

```text
residual = original_representation - predicted_from_nuisance_features
```

4. Re-run the same probes and retrieval on the residual representation.

For duration and phonetic content:

- Use fixed-length crops when possible.
- Use phone-aligned pooling if phone alignments exist.
- Start with same-phone vowel interiors to reduce phonetic mismatch.
- Add duration as a nuisance covariate.
- Compare phone-matched and all-phone results.

Important: do not over-regress by removing every spectral cue, because real
timbre also lives in spectral structure. Report both raw and controlled
results.

### Stage B: Residual Modeling

If Stage A finds a robust signal:

- define a stable identity component and a mode residual;
- compare three residual types:
  1. **oracle residual**: uses actual speech/singing pair for the same person;
  2. **population residual**: average speech-to-singing shift from training
     singers;
  3. **deployable predicted residual**: estimated from target speech only.

### Stage C: Downstream Seed-VC Stress Test

Compare:

- target speech reference;
- target singing reference oracle;
- speech reference plus average residual;
- speech reference plus predicted residual;
- possibly representation-guided prompt selection.

Evaluate:

- singer/speaker similarity;
- F0 and content preservation;
- singing MOS proxy only as a weak quality metric;
- small paired listening test if time allows.

### Main Risks

- The residual may collapse after F0, energy, duration, and phone controls.
- The signal may be mostly gender, pitch range, channel, language, or song.
- Probe accuracy alone does not prove disentanglement.
- Seed-VC may not be sensitive to the residual.

## Teacher-Facing Comparison

| Question | Direction 1: Technique Control | Direction 2: Timbre Shift |
|---|---|---|
| Main data | GTSinger | JVS/JVS-MuSiC, NHSS, GTSinger |
| Main target | Singing technique/style labels | Same-person speech/singing residual |
| First experiment | Clustering + linear probe | Leakage map + residualization |
| Strong evidence | Cross-singer technique prediction or controllable synthesis | Residual survives controls and predicts SVC prompt behavior |
| Biggest risk | Technique labels leak singer/content | Residual is just F0/duration/channel |
| Best role | Backup or parallel pilot | Main thesis candidate |

## Suggested Meeting Script

I currently see two possible directions.

The first is technique control. Instead of only converting singer timbre, I can
use GTSinger technique labels such as vibrato, breathy, falsetto, and glissando
to test whether frozen audio representations contain separable technique
directions. I would start with clustering only as visualization, then use
leave-singer-out probes and controlled vector-direction tests. If the signal is
real, I can compare simple conditioning methods such as label tokens, FiLM, and
cross-attention.

The second is same-person speech-vs-singing timbre shift. The question is
whether the difference between a person's speech and singing voice remains after
controlling obvious factors like F0, energy, duration, and phonetic content. I
would start with frozen representations and residualization, then test whether
the remaining residual explains why speech prompts and singing prompts behave
differently in Seed-VC.

My current preference is to make the second direction the main thesis
candidate, because it has a clearer small-GPU measurement pipeline and a direct
downstream SVC motivation. The technique-control direction is still valuable as
a backup, especially if the speech/singing residual collapses under controls.

## Questions To Ask The Teacher

1. Does the main thesis question sound more convincing as speech-vs-singing
   timbre shift, or as singing technique control?
2. Which dataset would you trust more for the first pilot: JVS/JVS-MuSiC,
   NHSS, or GTSinger paired speech?
3. For the timbre-shift direction, which confounds must be controlled before
   the result becomes credible?
4. For the technique direction, would probing plus vector arithmetic be enough,
   or would a synthesis/intervention result be necessary?
5. Is a small Seed-VC prompt-mode stress test a good downstream validation, or
   should the first paper remain a representation-analysis paper?
