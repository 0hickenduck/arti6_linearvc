# Proposed Experiment Protocol

## Research Hypotheses

### H1: Temporal concentration

Speaker identity, vocal mode, phonetic content, and prosody have different but
overlapping accessibility profiles across SSL layers and temporal scales.

### H2: Global statistics are insufficient

Global mean/std and normalized residuals do not fully disentangle these factors.
A nonredundant multiscale temporal decomposition produces a better
utility/leakage tradeoff.

### H3: Stable core plus mode residual

A representation that separates stable speaker identity from a
speaker-specific speech/singing residual improves cross-mode verification for
unseen singers without reducing same-mode verification or prosody/content
utility.

## Dataset

Use GTSinger for the primary controlled experiment:

- 20 professional singers;
- nine languages;
- paired speech and singing;
- phoneme alignment and singing-technique annotations;
- multiple songs per singer.

Treat language as metadata only in the MVP. Do not claim language
disentanglement because GTSinger speaker and language are confounded.

## Split

Use five fixed outer folds, each holding out four singers.

- 12 singers: train probe/decomposition heads.
- 4 singers: select hyperparameters and temporal scales.
- 4 singers: final test.

Rotate singers across five folds. No singer appears in more than one split
within a fold.

Within every singer:

- keep songs disjoint between fitting and evaluation where the task permits;
- keep paired speech/singing items together when assigning a split;
- prevent adjacent takes of the same song from crossing boundaries.

This gives:

- speaker verification: open-set evaluation on test singers;
- vocal-mode probes: speaker-disjoint evaluation;
- prosody/content probes: speaker- and song-disjoint evaluation.

## Frozen Representations

Begin with two encoders:

1. WavLM Base+ or WavLM Large frame-level hidden states.
2. FACodec pretrained encoder streams as an open factorized-codec baseline.

Add ContentVec only if compute permits. Keep ECAPA-TDNN as the existing
speaker-verification baseline, not as the only evaluator.

For WavLM, audit a small layer subset first: layers 3, 6, 9, and 12 for Base+,
or corresponding early/middle/late layers for Large.

## Temporal Decomposition

Let `H` be frame-level features at approximately 20 ms stride.

Global-statistics baseline:

```text
mu = mean_t(H)
sigma = std_t(H)
R_global = (H - mu) / (sigma + eps)
```

Do not assign linguistic meanings to fixed windows in advance. Begin with a
logarithmic sweep:

```text
M_20ms, M_40ms, M_80ms, M_160ms, M_320ms, M_640ms, M_1280ms
```

Construct nonredundant adjacent bands:

```text
B_20_40 = M_20ms - M_40ms
B_40_80 = M_40ms - M_80ms
...
B_640_1280 = M_640ms - M_1280ms
B_slow = M_1280ms
```

The 20 ms endpoint is the native frame-level baseline, not a meaningful
low-pass operation when the encoder stride is approximately 20 ms.

Use reflection padding and masked pooling so clip length does not become a
shortcut. Standardize features using training-fold statistics only. Interpret
bands after probes; do not pre-label them as phonetic, syllabic, or prosodic.

Compare fixed-duration bands with linguistically aligned alternatives:

- phone-interior pooling;
- boundary-centered transition windows;
- duration-normalized phone trajectories;
- syllable/note-aligned pooling where annotations permit.

## Stage A: Frozen Leakage Audit

Do not train a speech generator.

For every encoder layer and representation variant, freeze features and train:

- a regularized linear probe;
- a two-layer MLP probe with matched tuning budget.

Representation variants:

1. Raw pooled features.
2. Mean only.
3. Standard deviation only.
4. Mean plus log-standard-deviation.
5. Global normalized residual.
6. Every adjacent scale band from the 20--1280 ms sweep.
7. Every corresponding low-pass representation.
8. Concatenated multiscale bands.
9. Phone-interior pooled representation.
10. Phone-boundary/transition representation.
11. FACodec content, prosody, timbre, and residual streams.

Probe targets:

| Target | Evaluation |
| --- | --- |
| Vocal mode: speech/singing | Balanced accuracy, AUROC, macro-F1 on unseen singers |
| Speaker identity | Open-set EER and minDCF using held-out singers; closed-set ID only as a diagnostic |
| F0 trajectory | Voicing F1, cents MAE/RMSE, correlation or CCC |
| Energy | MAE and CCC |
| Phonetic content | Frame phone accuracy or CTC PER using provided alignments |
| Singing technique | Macro-F1 on unseen singers, singing subset only |

Report bootstrap 95% confidence intervals over speakers.

Repeat the temporal-scale analysis under:

- F0-matched sampling;
- explicit F0 regression/residualization;
- duration-matched sampling.

This tests whether an apparent short- or mid-scale factor is mostly pitch or
duration information.

### Phone-Conditioned Identity Gap

The global speech/singing identity gap must be decomposed into phonetic and
mode effects. Measure embedding distance for:

1. same speaker, same phone, cross-mode;
2. same speaker, different phone, same-mode;
3. same speaker, different phone, cross-mode;
4. different speaker, same phone.

Start with aligned vowel interiors, then add consonant classes and diphone
transitions. Fit a mixed-effects analysis controlling for phone class,
duration, F0 mean/range, SNR, speaker, and song.

This prevents phone inventory, note stretching, and phonetic mismatch from
being incorrectly reported as a pure vocal-mode identity shift.

The leakage matrix should distinguish intended utility from off-target
predictability. Probe accuracy is evidence of recoverability, not a mutual
information estimate and not proof that a decoder uses the factor.

## Stage B: Factorization Ablation

Train small heads over frozen SSL features. Do not fine-tune the backbone in the
first pass.

Baselines:

1. Raw pooled embedding.
2. Current ECAPA embedding.
3. Global difference-of-means speech-to-singing shift.
4. Existing residual MLP mapper.
5. Global mean/std plus normalized residual.
6. Best single scale selected on validation singers.
7. Multiscale bands without disentanglement losses.

Proposed model:

```text
z_core = E_core(B_20_40, ..., B_640_1280, B_slow, mu, sigma)
z_mode = E_mode(selected_bands, mu, sigma)
e_reconstructed = z_core + z_mode
```

Training objectives:

- supervised contrastive or metric loss for speaker identity on `z_core`;
- mode classification loss on `z_mode`;
- gradient-reversal mode adversary on `z_core`;
- covariance or cross-correlation penalty between `z_core` and `z_mode`;
- paired speech/singing consistency loss on `z_core`;
- reconstruction or embedding-reconstruction loss on `z_core + z_mode`.

Critical distinction:

`z_mode` should be allowed to contain a speaker-specific mode residual. The
goal is not to delete all vocal-mode variation, but to separate stable identity
from condition-dependent realization.

## Stage C: Causal Intervention

Only proceed if Stage B improves the held-out leakage/utility Pareto curve.

For paired utterances:

1. Keep content and melody from source singing.
2. Obtain stable identity from target speech.
3. Predict or select the target speaker's singing-mode residual.
4. Recombine identity core plus mode residual at the Seed-VC target-conditioning
   point or in a small compatible conditioning adapter.

Compare:

- raw target speech reference;
- target singing reference as an oracle;
- global mode shift;
- existing MLP mapper;
- proposed stable core plus mode residual.

Evaluate with:

- two independent speaker encoders;
- target similarity and source-speaker leakage;
- F0 correlation and cents RMSE;
- ASR CER/WER;
- UTMOS or another quality predictor;
- blinded identity preference and naturalness listening tests.

## Stop/Go Criteria

Proceed from Stage A to B only if at least one multiscale representation:

- changes off-target mode or speaker predictability by at least five absolute
  percentage points versus global mean/std; and
- retains at least 95% of the relevant target-factor probe performance.

Proceed from Stage B to C only if, on held-out singers:

- cross-mode EER improves relative to both the raw embedding and global-shift
  baselines;
- same-mode EER does not worsen by more than 10% relative;
- mode leakage from `z_core` decreases under both linear and MLP probes;
- results are consistent in at least four of five outer folds.

A reasonable downstream target is closing at least 25% of the gap between a
raw speech reference and the singing-reference oracle without significant
content or F0 degradation.

## Minimum Deliverable

The first deliverable is a reproducible CSV/JSON leakage cube indexed by:

```text
encoder x layer x representation_variant x target_factor x fold x probe_type
```

plus:

- aggregate tables with confidence intervals;
- heatmaps of factor accessibility;
- exact split manifests;
- a report stating whether Stage B is justified.
