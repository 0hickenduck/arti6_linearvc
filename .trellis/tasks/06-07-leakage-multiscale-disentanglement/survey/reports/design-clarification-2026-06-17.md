# Design Clarification: Technique Track vs Timbre-Residual Track

Date: 2026-06-17

## Main Clarification

There are two different kinds of projects:

1. **Representation/probing project**
   - asks whether information exists in a representation;
   - can use frozen features, probes, clustering, analogy tests;
   - does not need input-output generation pairs.

2. **Adapter/generation project**
   - asks whether we can control or synthesize a factor;
   - needs a base generator, a clear input/output definition, losses, and
     evaluation;
   - should only follow after the probing result is strong.

The Pro reports specified the **timbre-residual track** much more concretely
than the **technique-adaptation track**.

## What Pro Actually Designed For Timbre Shift

Pro's main design is:

### Stage A: frozen representation audit

Use GTSinger paired speech/singing and extract frozen representations:

- WavLM Base+ layers;
- ContentVec as a content-oriented comparison;
- FACodec streams as factorized-codec comparison;
- ECAPA as existing identity-gap baseline/evaluator.

Run:

- mode classification;
- speaker/singer identity retrieval;
- F0/energy/duration/content probes;
- phone-conditioned identity-gap analysis;
- F0/duration residualization and matched controls.

No generator yet.

### Stage B: residual modeling

In one chosen representation space:

```text
z_speech_s = mean_i h_s,speech,i
z_sing_s   = mean_i h_s,singing,i
delta_s    = z_sing_s - z_speech_s
```

Compare:

- no residual;
- global residual;
- acoustic-only residual predictor;
- technique/language-conditioned residual baselines;
- deployable predicted residual;
- oracle residual using target singing.

Losses:

- residual prediction loss:
  `||delta_hat - delta_oracle||` or cosine distance;
- same-singer cross-mode contrastive loss for stable core;
- optional reconstruction in representation-statistic space;
- light regularization / variance floor.

### Stage C: downstream intervention

Freeze Seed-VC and test:

- target speech reference baseline;
- target singing reference oracle;
- global residual;
- deployable residual;
- oracle residual upper bound.

Intervention options:

- modify the target reference/timbre conditioning vector;
- apply an AdaIN-like statistics shift;
- use reference selection/reweighting if patching internals is too risky.

Important: **Pro did not say to trust one VC model's timbre channel as ground
truth**. It said to compare general SSL representations and factorized/VC
representations, then only proceed if a residual survives controls.

## What Pro Said For Technique Adaptation

Pro's technique direction was a promising field direction, not a complete
experiment spec.

The suggested high-level idea was:

> Dynamic-style adapter for vibrato/glissando/breathy conversion. Use a
> pretrained singing/SVC system as the base, freeze most of it, and train small
> LoRA/adapters or explicit style-control heads on GTSinger/SVCC-style labels.

This is useful, but it leaves open:

- what is the base model?
- what is the input?
- what is the output?
- what is the loss?
- does GTSinger provide paired technique on/off examples?
- how to evaluate if no parallel target exists?

So the technique track needs a separate concrete design.

## Conductible Technique Track: Stage A Only

This part is clear and can be done first.

### Data

Use GTSinger phone-level technique labels.

For each phone or segment:

```text
audio segment -> frozen encoder -> frame features -> phone pooled vector
```

### Tests

1. Clustering/visualization:
   - exploratory only.

2. Linear probe:
   - input: phone/segment representation;
   - output: technique label;
   - split: leave-singer-out;
   - controls: phone, F0, duration, language/song where possible.

3. Nonlinear probe:
   - same input/output;
   - small MLP;
   - asks whether technique exists but is not linearly separable.

4. Analogy/vector test:

```text
direction_tech = mean(vibrato, matched phone/singer/F0 bins)
               - mean(control/non-vibrato, matched phone/singer/F0 bins)
```

Then test whether this direction transfers to held-out phones/singers.

This does not require parallel technique on/off data, but matching quality
matters.

## Possible Technique Adapter Design

Only do this after Stage A shows robust technique signal.

### Option A: analysis-only paper

Stop at:

- technique leakage map;
- linear vs nonlinear recoverability;
- cross-singer generalization;
- metric suite for vibrato/glissando/breathy features.

This is safer and does not require a generator.

### Option B: conditional reconstruction adapter

Use a pretrained generator/codec/SVC model with accessible hidden states.

Input:

```text
audio x with true technique label y
frozen encoder hidden state h
technique label y
```

Train adapter:

```text
h' = Adapter(h, y)
```

Output target:

- reconstruct the same audio or codec/acoustic tokens.

Losses:

- reconstruction loss in codec/acoustic feature space;
- technique classification loss on generated/reconstructed output;
- content/lyrics preservation loss;
- F0/melody preservation loss where appropriate;
- singer identity preservation loss;
- optional adversarial loss to reduce source singer or nuisance leakage.

This tests whether labels can condition reconstruction. It does **not** prove
technique conversion unless label-swapping works and evaluation supports it.

### Option C: style conversion adapter

Use a base singing style conversion/SVC system such as Serenade, Seed-VC,
HQ-SVC, or Vevo-style inference if accessible.

Input:

```text
source singing audio
target identity/reference
desired technique label or style reference
```

Output:

```text
converted singing audio with desired technique
```

Loss/evaluation:

- if paired target exists: reconstruction/supervised acoustic loss;
- if not paired: technique classifier agreement, F0 modulation metrics,
  singer identity similarity, content preservation, and listening tests.

This is more demo-friendly but harder to make rigorous.

## Bottleneck Options

FiLM is not itself a complete bottleneck. It is a conditioning mechanism. It
can act as a low-capacity control path if the label only produces feature-wise
scale and shift.

Possible bottlenecks:

- phone-level pooling;
- vector quantization / codec tokens;
- small-rank LoRA;
- low-dimensional style embedding;
- FiLM scale/shift only;
- adversarial GRL against singer/F0/content leakage;
- information dropout/noise on content path;
- FACodec content/prosody/timbre streams as factorized baseline.

## What To Say To Teacher

For technique:

> I can conduct the first stage as a probing project using GTSinger phone-level
> technique labels. If technique directions are robust, the next question is
> whether to stop at representation analysis or build a small adapter on top of
> an existing singing/SVC model. I still need advice on what base model and
> loss would make the adapter stage credible.

For timbre:

> The Pro design is clearer: first audit frozen representations, then predict
> speech-to-singing residuals, then test the residual in Seed-VC only if the
> audit succeeds. We should not assume a speech-VC timbre encoder is already
> correct for singing; FACodec/VC streams are baselines to audit, not ground
> truth.
