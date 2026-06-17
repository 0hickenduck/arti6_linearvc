# Feasible Baselines and Compute Plan

- Research cutoff: 2026-06-08
- Objective: test multiscale speech/singing leakage and stable-core/mode-residual
  factorization with one or a few GPUs, without training a backbone, codec, or
  full voice-conversion system.

## Recommendation

Use a frozen-feature, probe-first pipeline with:

1. `microsoft/wavlm-base-plus` as the primary SSL encoder.
2. pretrained NaturalSpeech 3 FACodec as the factorized-codec comparison.
3. SpeechBrain ECAPA-TDNN as the existing identity-gap evaluation floor.
4. ContentVec only after the WavLM pipeline is stable.
5. kNN-VC and Seed-VC only for a small causal/intervention stage.

The main dataset should not initially be all 96.75 hours of GTSinger. Use all
16.16 hours of paired speech and a duration-matched 16.16-hour sample of its
paired singing, for approximately 32.3 hours total across all 20 singers.
Extract frozen features once, cache them, and reuse them across the five
singer-disjoint folds.

This plan is feasible on one 24 GB GPU. Two GPUs are useful for parallel feature
extraction and Seed-VC inference, but distributed training is unnecessary.

## Dataset Scale

GTSinger provides 80.59 hours of singing and 16.16 hours of paired speech from
20 professional singers in nine languages, with phoneme alignments and six
singing-technique annotations.

| Stage | Audio | Purpose |
| --- | ---: | --- |
| Pipeline smoke test | 3 hours | Six singers, 15 minutes per mode per singer; validate manifests, masks, feature extraction, and one-fold probes. |
| Main Stage A | 32.3 hours | All 16.16 hours of speech plus 16.16 hours of duration-matched paired singing; all 20 singers and five folds. |
| Expansion check | Up to 96.75 hours | Run only the winning encoder layer and representation variants to test whether conclusions survive more singing data. |
| Synthesis set | 100 source items | Five held-out items per singer, balanced by song, pitch range, duration, and technique. |

Use the fixed 12/4/4 train/validation/test singer split within each of five
outer folds. Keep songs and adjacent takes together. Extract features globally,
but fit standardization, residualization, probe parameters, and thresholds from
the training singers only.

Language remains confounded with singer in GTSinger. Include language as
descriptive metadata and a sensitivity grouping, not as an independently
identified leakage target.

## Frozen-Feature Pipeline

### 1. Build immutable examples

- Start from the existing GTSinger metadata and paired `speech_fn`/`wav_fn`
  entries used by `arti6_linearvc_demo/prepare_gtsinger_tiny.py`.
- Produce clip-, singer-, song-, mode-, phone-, technique-, and fold-level
  manifests.
- Resample SSL/codec inputs to 16 kHz.
- Use masked chunks of 2-4 seconds for coarse probes and annotation-aligned
  phone windows for the phonetic-gap analysis.
- Store duration, voiced ratio, F0 mean/range, energy, and SNR-like quality
  controls with every example.

### 2. Extract and cache frozen representations once

- WavLM Base+: hidden layers 3, 6, 9, and 12.
- FACodec: continuous encoder output, prosody codes, content codes, residual
  codes, and timbre/speaker embedding.
- ECAPA-TDNN: utterance embeddings for the existing speaker-domain protocols.
- ContentVec: one selected layer/checkpoint only after the primary audit works.

Do not cache every smoothed or band-pass variant. Cache the base frame-level
features in float16 and derive low-pass signals, adjacent bands, global
statistics, phone pools, and fold-specific residuals offline.

### 3. Use successive halving instead of a full factorial sweep

1. One fold, linear probes only: all four WavLM layers and all temporal scales.
2. Retain at most two layers and four nonredundant representation families.
3. Run five folds with linear and two-layer MLP probes on the retained set.
4. Run F0/duration controls only for representations on the validation Pareto
   frontier.
5. Train the stable-core/mode-residual head only if Stage A meets the predefined
   stop/go threshold.

This avoids thousands of nearly redundant probe fits.

## Exact Baseline Candidates

| Candidate | Exact public artifact | Training needed | Role and decision |
| --- | --- | --- | --- |
| SpeechBrain ECAPA-TDNN | `speechbrain/spkrec-ecapa-voxceleb` | None | Required identity-gap floor. Reuse `run_speaker_domain_eval.py`; add a second independent speaker encoder only for final intervention evaluation. |
| WavLM Base+ | `microsoft/wavlm-base-plus`, 378 MB checkpoint | None | Primary frozen encoder. It is much cheaper than Large and exposes all 12 hidden layers in one forward pass. |
| WavLM Large | `microsoft/wavlm-large`, 1.262 GB checkpoint | None | Escalation only. Run the best one or two representation variants after Base+ results stabilize; do not begin with a 24-layer sweep. |
| ContentVec | official `ContentVec_legacy` 500-class checkpoint, `checkpoint_best_legacy_500.pt` | None | Strong secondary content-oriented representation because it explicitly suppresses speaker variation. Fairseq and IBM Box dependencies add setup risk, so it should not block the MVP. |
| NaturalSpeech 3 FACodec | `amphion/naturalspeech3_facodec`: `ns3_facodec_encoder.bin` plus `ns3_facodec_decoder.bin` | None | Required factorized-codec comparison. Probe content, prosody, residual, and timbre streams separately. Do not train or fine-tune FACodec. |
| Existing global statistics | WavLM global mean, std, mean+log-std, and normalized residual | Small probes only | Required non-multiscale baseline and direct control for the proposed contribution. |
| Existing timbre shifts | Repository difference-of-means shift and residual MLP mapper | Minutes to a few hours | Required local baselines. Evaluate in embedding space before attempting synthesis. |
| kNN-VC | `bshall/knn-vc`; release `WavLM-Large.pt` (1.262 GB) and `prematch_g_02500000.pt` (66 MB) | None | Best no-training positive contrast for an SSL-space intervention. Use only on the synthesis subset; it is not a leakage-probe encoder sweep. |
| Seed-VC SVC | `Plachta/Seed-VC`, `DiT_seed_v2_uvit_whisper_base_f0_44k_bigvgan_pruned_ft_ema.pth` (about 821 MB, 200M DiT) | None | Primary downstream zero-shot synthesis test. Use F0 conditioning and speech-reference versus singing-reference prompts. The official repo is archived, so pin a tested commit and environment. |
| RVC | `RVC-Project/Retrieval-based-Voice-Conversion-WebUI` plus shared HuBERT/RMVPE/base assets | Per target speaker | Optional specialist comparison on at most two singers. The public assets do not provide a universal target-speaker model, so a 20-singer RVC benchmark is not compute- or protocol-matched. |
| DDSP-SVC | `yxlllc/DDSP-SVC` plus ContentVec/HubertSoft and pretrained vocoder | New single- or multi-speaker model | Optional pitch-preservation sanity check on at most two singers. Useful only if Stage C needs a lightweight trained SVC contrast. |
| so-vits-svc 4.1 | archived `svc-develop-team/so-vits-svc` | Per target speaker | Survey/reference only for this project. It is archived, depends on a legacy environment, and its shared pretrained files are initialization assets rather than complete target models. |

The benchmark gate is satisfied for WavLM, ContentVec, FACodec, kNN-VC, and
Seed-VC because usable code and pretrained weights are public. RVC, DDSP-SVC,
and so-vits-svc should not be core baselines because the relevant target voices
must be trained.

## Compute and Storage Budget

These are planning ranges, not measured benchmarks. They assume one modern
16-24 GB NVIDIA GPU, mixed-precision inference, chunked audio, and local SSD
storage. Calibrate them with the first 100 clips before scheduling the full run.

| Work item | Main Stage A estimate | Notes |
| --- | ---: | --- |
| Manifest, audio controls, F0/energy, alignment parsing | 4-12 CPU hours | Parallel CPU job; no GPU needed except an optional neural F0 extractor. |
| WavLM Base+ extraction, 32.3 h | 3-10 GPU hours | One forward pass can return layers 3/6/9/12. |
| ContentVec extraction, 32.3 h | 3-10 GPU hours | Optional; run after the WavLM/FACodec audit is healthy. |
| FACodec factor extraction, 32.3 h | 2-8 GPU hours | Encoding and quantization only; waveform reconstruction is unnecessary. |
| One-fold linear screening | 1-3 GPU hours or 4-12 CPU hours | Use pooled/segmented examples, class weighting, and fixed regularization grids. |
| Five-fold linear plus MLP confirmation | 5-15 GPU hours | Limit to the retained layers/representations; bootstrap metrics on CPU. |
| Stage B frozen small heads | 10-30 GPU hours | Target less than 5M trainable parameters; one seed on all folds, second seed only for the selected configuration. |
| kNN-VC synthesis subset | 2-6 GPU hours | Zero training; WavLM Large feature extraction plus nearest-neighbor retrieval and HiFi-GAN. |
| Seed-VC 8-step screen | 5-15 GPU hours | Screen conditions cheaply before final-quality inference. |
| Seed-VC 30-step final set | 10-30 GPU hours | Run only selected conditions and clips; official guidance recommends 30-50 steps for SVC. |

Expected aggregate:

- Two-week Stage A: approximately 20-50 GPU hours.
- Four-week Stage A+B+C: approximately 45-120 GPU hours.
- No single experiment requires multiple GPUs.

WavLM Base+ produces approximately 0.276 GB per audio hour per cached 768-D
layer at 50 Hz in float16. Four layers over 32.3 hours therefore require about
36 GB before metadata and indexes; the full 96.75-hour corpus would require
about 107 GB. Cache only selected layers and use float16. FACodec discrete codes
are much smaller; continuous 256-D encoder features should remain below roughly
5-10 GB for the main subset.

## Ordered Ablation Plan

### Stage A1: floors and shortcuts

1. F0, energy, duration, voiced ratio, and clip length alone.
2. ECAPA raw embeddings under the four existing enrollment/query protocols.
3. Raw WavLM pooled features by layer.
4. Class-balanced mode and speaker probes with singer-disjoint test data.

If cheap acoustics explain most mode performance, do not interpret a WavLM
band as a new vocal-mode representation.

### Stage A2: statistical and temporal representations

1. Mean only.
2. Standard deviation only.
3. Mean plus log-standard-deviation.
4. Global normalized residual.
5. Each low-pass scale: 20, 40, 80, 160, 320, 640, and 1280 ms.
6. Each adjacent nonredundant band.
7. Concatenated bands.
8. Best single band.
9. Phone-interior, phone-boundary, and duration-normalized phone trajectories.

The critical comparison is adjacent bands versus their corresponding
low-passes and global statistics. Without that comparison, improved probe
performance could be due only to more smoothing or feature dimensions.

### Stage A3: confound controls

Run only on the shortlisted representations:

1. F0-matched sampling.
2. Fold-trained F0 regression and residualization.
3. Duration-matched sampling.
4. Equal clip-length masks and reflection padding.
5. Vowel-interior-only analysis.
6. Boundary/transition-only analysis.
7. Linear versus MLP probe gap.

### Stage A4: representation-family comparison

Compare the winning WavLM representations against:

- ContentVec legacy 500;
- FACodec content, prosody, timbre, and residual streams;
- raw ECAPA embeddings.

Do not run a full layer-by-scale sweep for ContentVec or FACodec. Their role is
to test whether an explicitly speaker-disentangled SSL model or factorized
codec already provides the same utility/leakage tradeoff.

### Stage B: small stable-core/mode-residual head

Use the existing baselines plus:

1. best single scale;
2. multiscale bands without factorization losses;
3. paired core-consistency loss only;
4. plus mode adversary;
5. plus core/mode decorrelation;
6. plus reconstruction or embedding-reconstruction loss.

Avoid a full loss-factorial experiment. Add losses sequentially, then remove
each component once from the best combined model. Report one seed across all
five folds and a second seed for only the final selected model.

### Stage C: causal intervention

On the fixed 100-item synthesis set:

1. Seed-VC with target speech reference.
2. Seed-VC with target singing reference as oracle.
3. Existing global shift.
4. Existing residual MLP mapper.
5. Proposed stable core plus mode residual adapter.
6. kNN-VC as an independent no-training SSL-space positive contrast.

Use 8 diffusion steps for screening, then 30 steps for the final retained
conditions. Do not synthesize every Stage A ablation.

## What Not to Train

- No WavLM or ContentVec fine-tuning in the first four weeks.
- No new codec, vocoder, FACodec, or HiFi-GAN training.
- No Seed-VC fine-tuning before a frozen representation improves the held-out
  leakage/utility Pareto curve.
- No 20-singer RVC, so-vits-svc, or DDSP-SVC training matrix.
- No WavLM Large full layer-by-scale sweep.
- No full-corpus extraction for every failed representation variant.
- No language-disentanglement head from GTSinger.
- No large subjective listening study before objective gates pass.

If a trained singing-specialist baseline becomes necessary, train RVC or
DDSP-SVC for two representative held-out singers only, using identical target
audio minutes and reporting that it is a speaker-adapted rather than zero-shot
comparison.

## Two-to-Four-Week Plan

### Week 1: pipeline and one-fold screen

- Freeze split manifests and the 3-hour smoke subset.
- Reproduce the ECAPA speech/singing domain gap with the existing command path.
- Extract WavLM Base+ layers 3/6/9/12.
- Validate masking, temporal bands, phone pools, and cheap acoustic controls.
- Run one-fold linear probes.

Deliverable: a small leakage cube and a measured real-time factor/storage
calibration. Stop if splits, masks, or cheap controls expose a shortcut.

### Week 2: confirmatory Stage A

- Extract WavLM Base+ and FACodec for the 32.3-hour balanced subset.
- Retain at most two WavLM layers and four representation families.
- Run five-fold linear/MLP probes, bootstrap intervals, F0/duration controls,
  and the phone-conditioned identity-gap analysis.
- Add ContentVec only if time remains or WavLM/FACodec give contradictory
  results.

Deliverable: the full Stage A leakage cube and a hard Stage B stop/go decision.
This is the minimum defensible two-week project.

### Week 3: lightweight factorization

- Train the less-than-5M-parameter stable-core/mode-residual heads on frozen
  features.
- Compare existing global shift, residual MLP, best single band, and multiscale
  no-loss baselines.
- Run sequential loss additions and final leave-one-loss-out ablations.

Deliverable: held-out cross-mode EER, same-mode EER, mode leakage, and content/
prosody preservation across five folds.

### Week 4: small causal test

- Build the fixed 100-item synthesis manifest.
- Screen Seed-VC conditions at 8 steps.
- Run final Seed-VC outputs at 30 steps for selected conditions.
- Run kNN-VC on the same subset.
- Evaluate with two speaker encoders, F0 preservation, ASR, quality prediction,
  and a small blinded listening check.

Deliverable: intervention evidence or a documented negative result. Do not add
RVC/DDSP-SVC unless the frozen method passes and a speaker-adapted contrast is
scientifically necessary.

## Decision Gates

Proceed from the one-fold screen only if:

- mode/speaker results are not primarily explained by duration or clip length;
- at least one WavLM layer has stable performance across train/validation
  singers;
- feature extraction and cache size extrapolate within the stated budget.

Proceed to Stage B only if at least one multiscale representation changes
off-target predictability by at least five absolute percentage points versus
global mean/std while retaining at least 95% of target-factor performance.

Proceed to synthesis only if the core representation improves cross-mode EER
against raw ECAPA, global shift, and the existing residual mapper without more
than 10% relative degradation in same-mode EER, and both linear and MLP probes
show reduced mode leakage.

## Existing Repository Paths to Reuse

- `arti6_linearvc_demo/prepare_gtsinger_tiny.py`: GTSinger metadata and paired
  file access pattern.
- `arti6_linearvc_demo/run_speaker_domain_eval.py`: ECAPA enrollment/query
  protocols and report structure.
- `arti6_linearvc_demo/run_timbre_shift_mapper.py`: global shift and residual
  MLP baselines.
- `arti6_linearvc_demo/run_seedvc_svc_demo.py`: speech/singing prompt comparison
  and elapsed-time logging.
- `arti6_linearvc_demo/run_seedvc_svc_matrix.py`: reproducible synthesis matrix
  aggregation.

## Primary Sources

- [GTSinger paper](https://proceedings.neurips.cc/paper_files/paper/2024/file/023d2c1a17cf35b11a0cbb43a0677c91-Paper-Datasets_and_Benchmarks_Track.pdf)
- [GTSinger dataset](https://huggingface.co/datasets/AaronZ345/GTSinger)
- [WavLM paper](https://arxiv.org/abs/2110.13900)
- [WavLM Base+ checkpoint](https://huggingface.co/microsoft/wavlm-base-plus)
- [WavLM Large checkpoint](https://huggingface.co/microsoft/wavlm-large)
- [ContentVec paper](https://proceedings.mlr.press/v162/qian22b.html)
- [ContentVec official code and checkpoints](https://github.com/auspicious3000/contentvec)
- [NaturalSpeech 3 / FACodec paper](https://arxiv.org/abs/2403.03100)
- [FACodec pretrained checkpoints](https://huggingface.co/amphion/naturalspeech3_facodec)
- [Amphion FACodec implementation](https://github.com/open-mmlab/Amphion)
- [kNN-VC paper](https://www.isca-archive.org/interspeech_2023/baas23_interspeech.html)
- [kNN-VC official code and release weights](https://github.com/bshall/knn-vc)
- [Seed-VC paper](https://arxiv.org/abs/2411.09943)
- [Seed-VC official code](https://github.com/Plachtaa/seed-vc)
- [Seed-VC checkpoints](https://huggingface.co/Plachta/Seed-VC)
- [RVC official repository](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)
- [DDSP-SVC official repository](https://github.com/yxlllc/DDSP-SVC)
- [so-vits-svc archived repository](https://github.com/svc-develop-team/so-vits-svc)
- [SpeechBrain ECAPA checkpoint](https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb)
