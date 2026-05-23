# Deep synthesis: research options after the ARTI-6 LinearVC negative result

Date: 2026-05-20

## 0. Corrected core observation

The decisive negative result is stronger than "our linear model was bad."

The useful oracle condition is:

```text
source_arti + target_speaker_id -> target-timbre speech preserving source content
```

This means that in the current ARTI-6 synthesizer, perceived timbre is mostly carried by the speaker conditioning path. The 6D ARTI stream carries the articulatory / phonetic trajectory needed to preserve what is being said.

Therefore:

```text
perfect ARTI transform -> preserves / changes linguistic-articulatory content
imperfect ARTI transform -> damages content
neither case gives ARTI-only target timbre
```

So the strongest claim is not "more data may fix pure ARTI LinearVC." More data may improve trajectory matching, but trajectory matching has already been bypassed by the oracle: preserving source ARTI and swapping only speaker ID already gives the target timbre. The remaining useful question is representation-theoretic:

```text
Why can linear / retrieval VC work in high-dimensional SSL acoustic spaces,
while it is structurally the wrong operation in a low-dimensional ARTI content bottleneck?
```

## 1. What the relevant papers imply

### ARTI-6

ARTI-6 defines a compact 6D articulatory encoding from vocal-tract regions, predicts it from speech, and reconstructs speech from the articulatory features. The public ARTI-6 pipeline we inspected uses a separate ECAPA-TDNN speaker embedding in synthesis. The paper's abstract frames ARTI-6 as an interpretable, physiologically grounded articulatory encoding, not as a timbre transformation space.

Implication for us:

```text
ARTI-6 is a content / articulation representation with a separate identity input.
Using it as a pure timbre-control space fights the architecture.
```

### LinearVC and kNN-VC

LinearVC reports that simple linear transformations of SSL features can convert voices; even rotation can be sufficient. It further argues that content and speaker information are geometrically structured in SSL space. kNN-VC similarly works by replacing each source SSL frame with nearest target-reference SSL frames and using a pretrained vocoder.

Implication for us:

```text
The positive baseline is not "linear algebra magically changes voices."
It is that SSL spaces still contain speaker/timbre geometry.
ARTI-6 likely removed or externalized that geometry into speaker_id.
```

### SPARC / RT-VC

SPARC and RT-VC are closer to articulatory voice-conversion systems than ARTI-6, but they still do not imply "change articulatory features to get timbre." SPARC explicitly includes articulatory/source features plus an additional speaker identity encoder for voice texture. RT-VC also uses articulatory feature space to disentangle content and speaker characteristics, then relies on a real-time synthesis/vocoding system.

Implication for us:

```text
Articulatory coding remains useful, but the task should be accent/content/control,
not ARTI-only timbre conversion.
```

### AutoVC / SpeechSplit / ACE-VC

These methods are useful conceptually because they show the standard VC decomposition: remove speaker information from the content stream, then re-inject target speaker / pitch / style through other streams. ACE-VC explicitly uses pitch-shifted pairs and Siamese training to separate content from speaker; SpeechSplit decomposes content, rhythm, pitch, and timbre.

Implication for us:

```text
If ARTI-6 already behaves like a strong content bottleneck, then our failure is a success of disentanglement.
The paper direction is to verify and exploit that, not to undo it.
```

### WORLD / source-filter controls

WORLD decomposes speech into F0, spectral envelope, and aperiodicity. McAdams coefficient / LPC pole warping and VTLN-style spectral-envelope warping directly target formants and vocal-tract resonance. This is much closer to the original intuition: small interpretable operations that affect perceived voice.

Implication for us:

```text
If we want "small interpretable timbre knobs" without training a large model,
use source-filter / spectral-envelope spaces, not ARTI-6 trajectories.
```

## 2. Proposal set, filtered

I would not present these as equal options. They fall into three tiers.

### Tier 1: mainline ideas worth doing now

#### Proposal A: Representation audit - ARTI-6 as content bottleneck vs SSL as timbre-bearing space

Claim:

```text
Linear VC requires representations that retain speaker geometry.
ARTI-6 6D features are useful because they collapse toward content / articulation,
which makes them a bad pure LinearVC space.
```

Minimal experiment:

1. Build a matched dataset from our existing CMU ARCTIC pairs.
2. Extract per-utterance and frame-pooled features:
   - ARTI-6 6D features
   - WavLM / HuBERT intermediate features, especially the layer used by kNN-VC / LinearVC
3. Train simple speaker classifiers:
   - logistic regression / linear SVM
   - same train/test speakers and utterances
4. Train or compute content/prompt probes:
   - same-prompt cross-speaker distance
   - different-prompt same-speaker distance
   - optional phoneme/prompt classifier if transcripts are easy
5. Report:
   - speaker predictability from ARTI vs SSL
   - prompt/content clustering from ARTI vs SSL
   - visualization colored by speaker and prompt

Expected result:

```text
SSL features should predict speaker better than ARTI-6.
ARTI-6 should preserve content/prompt structure more cleanly and show weaker speaker clusters.
```

Why it is valuable:

This directly turns the negative result into a measurable representation claim. It does not need a new decoder or a large training run.

Failure mode:

ARTI-6 may still predict speaker above chance because articulatory habits leak identity. That is not fatal. It gives a more nuanced claim:

```text
ARTI-6 contains some speaker leakage, but the synthesis model primarily realizes timbre through speaker conditioning.
```

Paper value:

High as the first section of a paper/demo. It is the cleanest bridge from our listening result to a quantitative argument.

#### Proposal B: Oracle-factorization demo - show that ARTI controls content and speaker_id controls timbre

Claim:

```text
In ARTI-6 synthesis, voice conversion is mostly a speaker-conditioning intervention,
not an articulatory-trajectory mapping problem.
```

Minimal experiment:

Create a small condition grid for multiple held-out utterances:

```text
source_arti + source_spk     -> source reconstruction
source_arti + target_spk     -> embedding-only VC
target_arti + source_spk     -> source-like voice saying target content
target_arti + target_spk     -> target reconstruction
linear(source_arti)+source_spk -> content damage without target timbre
linear(source_arti)+target_spk -> target timbre mostly unchanged, content may degrade
```

Add two cheap quantitative measures:

1. ASR transcript / WER for content preservation.
2. Speaker embedding cosine similarity against source and target references.

Expected result:

```text
speaker similarity follows speaker_id;
content follows ARTI stream;
linear perturbation mainly worsens content.
```

Why it is valuable:

It formalizes the listening result the user identified. It is easy to explain in one figure and one table.

Failure mode:

Off-the-shelf ASR or speaker-verification metrics may be noisy on generated audio. We can still use them as weak diagnostics and keep listening examples.

Paper value:

High for demo/storytelling. This should be the first figure because it proves why the original LinearVC hypothesis is structurally blocked.

#### Proposal C: SSL positive contrast - run kNN-VC or LinearVC on the same source-target split

Claim:

```text
The failure is representation-specific, not a general failure of linear / retrieval VC.
```

Minimal experiment:

1. Use official kNN-VC first, because it provides pretrained WavLM + HiFi-GAN paths.
2. Run `source -> target` conversion on the same CMU ARCTIC pair.
3. If feasible, add LinearVC-style least-squares projection over WavLM layer features.
4. Compare:
   - ARTI-6 affine transforms
   - ARTI-6 speaker-ID swap baseline
   - kNN-VC / LinearVC SSL baseline

Expected result:

```text
SSL VC should change timbre while preserving content better than ARTI affine transforms,
because SSL features retain speaker geometry.
```

Why it is valuable:

This is the cleanest external validation that our negative result is not caused only by bad paired data, tiny training, or linear algebra. It also anchors our work to LinearVC / kNN-VC literature.

Failure mode:

Dependency setup may be annoying, and kNN-VC may sound worse on CMU ARCTIC than on its original domain. Even then, the attempt is useful as a baseline.

Paper value:

High if it runs. Without this contrast, the paper risks sounding like "we tried one representation and it failed."

### Tier 2: good side experiments after Tier 1

#### Proposal D: Speaker-embedding interpolation / steering inside ARTI-6

Claim:

```text
If timbre lives in speaker_id, then continuous movement in speaker embedding space should move timbre while preserving ARTI-controlled content.
```

Minimal experiment:

1. Fix one `source_arti`.
2. Interpolate `spk = (1-alpha) * source_spk + alpha * target_spk`.
3. Synthesize for alpha from 0 to 1.
4. Measure speaker-similarity curves against source and target.

Expected result:

Smooth perceived timbre transition, with content stable.

Why it is valuable:

It redirects the project from "linear ARTI transform" to "where is the controllable timbre geometry in this architecture?"

Risk:

ECAPA embedding interpolation may go off-manifold. If the synthesizer was only trained on real embeddings, intermediate vectors may create artifacts.

Paper value:

Medium-high as a figure. It is probably not enough as a main paper alone, but it strongly supports Proposal B.

#### Proposal E: WORLD / McAdams / VTLN interpretable timbre controls

Claim:

```text
For small interpretable voice changes, classical source-filter spaces are a better target than ARTI-6.
```

Minimal experiment:

1. Use `pyworld` to extract F0, spectral envelope, and aperiodicity.
2. Conditions:
   - F0 mean/std normalization
   - spectral envelope / VTLN frequency warping
   - LPC McAdams coefficient pole warping
3. Resynthesize and package demos next to ARTI-6.
4. Measure:
   - ASR/WER for content
   - speaker embedding similarity shift
   - formant/F0 statistics before/after

Expected result:

Formant/spectral-envelope operations should change perceived body size / resonance more directly than ARTI transforms, while not changing words.

Risk:

WORLD/LPC audio may sound buzzy or metallic. That is acceptable for a baseline if the control axis is clear.

Paper value:

Medium. It may become a strong demo, but by itself it is more of an interpretable baseline than a new representation-learning result.

#### Proposal F: ARTI perturbation sensitivity map

Claim:

```text
ARTI dimensions are content/articulation knobs; perturbing them should produce phonetic degradation or articulatory-style changes before timbre conversion.
```

Minimal experiment:

1. For each ARTI dimension, apply small additive offsets and variance scaling.
2. Keep speaker_id fixed.
3. Run ASR and speaker similarity.
4. Plot WER and speaker-similarity vs perturbation magnitude per dimension.

Expected result:

Small perturbations affect intelligibility / phone quality; speaker similarity remains mostly stable until the decoder collapses.

Risk:

Manual perturbations may go off-manifold too quickly. Use small perturbations and alpha sweeps.

Paper value:

Medium-high as a diagnostic figure. It strengthens the claim that ARTI is not a timbre space.

### Tier 3: plausible but not first-line

#### Proposal G: Accent conversion / articulation morphing

Claim:

```text
If ARTI captures articulatory gestures, it may support accent or pronunciation morphing while preserving speaker identity.
```

Minimal experiment:

Use same-text native/non-native or cross-accent pairs, align ARTI trajectories with DTW, interpolate trajectories, synthesize with fixed speaker_id.

Why not first:

We need a suitable accent dataset and evaluation. CMU ARCTIC may not give enough accent variation. This can become good, but it is not the fastest next experiment.

Paper value:

Potentially high, but dataset/evaluation risk is high.

#### Proposal H: Dysarthric / speech correction via ARTI mapping

Claim:

```text
If ARTI controls content while speaker_id preserves identity, mapping impaired ARTI trajectories to healthy trajectories could repair intelligibility without changing speaker identity.
```

Why not first:

Requires a dysarthric paired or comparable dataset and robustness of ARTI inversion on impaired speech. High social value, but not a quick continuation.

Paper value:

High long-term; not the next demo.

#### Proposal I: Local/piecewise LinearVC in SSL space

Claim:

```text
Instead of one global SSL linear map, learn cluster-conditioned linear maps over WavLM features.
```

Why not first:

This is a real research idea, but it is a new method in SSL VC, not directly our ARTI-6 insight. It should come only after we reproduce a basic SSL positive baseline.

Paper value:

Medium-high later. First we need kNN-VC / LinearVC running.

#### Proposal J: AutoVC/ACE-style retraining or new decoder

Claim:

```text
Explicitly disentangled models can improve controllability beyond ARTI-6.
```

Why not first:

It violates our current constraint: avoid training a big model. It also moves away from the unique negative result we already have.

Paper value:

Not bad in general, but low fit for our current project.

## 3. Proposed paper skeleton

Working title:

```text
When Linear Voice Conversion Fails: Articulatory Bottlenecks vs SSL Speaker Geometry
```

Main claim:

```text
Linear voice conversion depends on a representation retaining speaker/timbre geometry.
ARTI-6's 6D articulatory representation is valuable precisely because it externalizes timbre to speaker conditioning,
so ARTI-space linear maps damage linguistic-articulatory content instead of converting voice identity.
```

Paper sections:

1. Motivation:
   - LinearVC works in SSL spaces.
   - Can the same idea work in a compact interpretable articulatory space?
2. ARTI-6 oracle intervention:
   - condition grid proving content follows ARTI, timbre follows speaker_id.
3. Negative result:
   - mean/std, diagonal, full, ridge, alpha transforms.
   - show more capacity improves trajectory MSE but not timbre.
4. Representation audit:
   - speaker predictability and content/prompt clustering for ARTI vs SSL.
5. Positive contrast:
   - kNN-VC / LinearVC on WavLM features.
6. Discussion:
   - articulatory spaces are good for content/accent/control, not pure timbre conversion.
   - interpretable timbre should use speaker embeddings or source-filter features.

## 4. Suggested figures and tables

Figure 1: ARTI-6 factorization grid

```text
Rows: source_arti, target_arti, linear(source_arti)
Columns: source_spk, target_spk, maybe average_spk
```

Caption claim:

```text
content follows rows; timbre follows columns.
```

Figure 2: Transformation degradation curve

```text
x-axis: transform strength / condition
y-axis left: WER or CER
y-axis right: speaker similarity to target
```

Expected:

```text
speaker similarity is controlled by speaker_id;
linear transform strength mostly increases content error.
```

Figure 3: ARTI vs SSL representation audit

```text
Panel A: speaker classifier accuracy
Panel B: same-prompt vs different-prompt distances
Panel C: 2D projection colored by speaker and by prompt
```

Figure 4: Positive contrast demo

```text
ARTI affine vs kNN-VC / LinearVC WavLM on same pair.
```

Table 1: Conditions and interpretation

```text
condition | ARTI stream | speaker stream | predicted content | predicted timbre | observed
```

Table 2: Minimal objective metrics

```text
system | WER/CER | speaker cosine to source | speaker cosine to target | notes
```

## 5. What I would do next

Do not add more ARTI affine variants yet.

The next implementation stage should be:

```text
Stage 1: objective oracle-factorization report
Stage 2: ARTI-vs-SSL representation audit
Stage 3: kNN-VC / LinearVC positive contrast
Stage 4: optional WORLD/source-filter timbre-control demo
```

Stage 1 is closest to our current artifacts. It should convert the user's listening insight into a table/plot:

```text
source_arti + target_spk proves target timbre does not require ARTI mapping.
linear ARTI mapping only introduces content error.
```

Stage 2 is the most paper-like next diagnostic. Stage 3 is the strongest external contrast. Stage 4 is a side demo that preserves the user's original "small interpretable timbre knobs" intuition, but it should not be confused with ARTI-6 LinearVC.

## 6. Source URLs checked

- ARTI-6: https://arxiv.org/abs/2509.21447
- LinearVC: https://arxiv.org/abs/2506.01510
- kNN-VC: https://arxiv.org/abs/2305.18975
- kNN-VC official repo: https://github.com/bshall/knn-vc
- SPARC: https://arxiv.org/abs/2406.12998
- RT-VC: https://arxiv.org/abs/2506.10289
- ACE-VC: https://arxiv.org/abs/2302.08137
- AutoVC: https://arxiv.org/abs/1905.05879
- SpeechSplit 2.0: https://arxiv.org/abs/2203.14156
- PyWORLD: https://github.com/JeremyCCHsu/Python-Wrapper-for-World-Vocoder
- VoicePrivacy McAdams baseline: https://www.voiceprivacychallenge.org/docs/VoicePrivacy_2024_Eval_Plan_v2.1.pdf
