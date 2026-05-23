# Related Work Questions And Search Plan

Status: PARTIAL GO

This is a practical literature-search plan, not a completed literature review.

## Core Search Questions

1. Has articulatory inversion already been used for voice conversion?
2. Are low-dimensional articulatory trajectories known to encode speaker-dependent traits?
3. Do explicit linear or affine transforms in articulatory space have precedent?
4. Does speaker embedding conditioning dominate low-dimensional articulatory conditioning in neural synthesis?
5. What evidence would make ARTI-6 + LinearVC a meaningful interpretability contribution rather than just another VC demo?

## Search Queries

### Articulatory Voice Conversion

- `"articulatory voice conversion"`
- `"articulatory features" "voice conversion"`
- `"articulatory inversion" "voice conversion"`
- `"vocal tract" "voice conversion" articulatory`
- `"EMA" "voice conversion" articulatory`
- `"rtMRI" "voice conversion" speech`

### Articulatory Inversion For Voice Conversion

- `"speech inversion" "voice conversion"`
- `"acoustic-to-articulatory inversion" "voice conversion"`
- `"articulatory inversion" speaker conversion`
- `"articulatory representation" speaker adaptation speech synthesis`

### Low-Dimensional Articulatory Features

- `"low-dimensional articulatory features" speech synthesis`
- `"six-dimensional articulatory" speech`
- `"regions of interest" articulatory speech synthesis`
- `"vocal tract constriction variables" speech synthesis`
- `"task dynamics" articulatory phonology speech synthesis`

### Interpretable Voice Conversion

- `"interpretable voice conversion"`
- `"disentangled voice conversion" speaker content articulatory`
- `"explainable voice conversion"`
- `"controllable voice conversion" articulatory`
- `"speaker embedding" "articulatory" synthesis`

### WavLM / SSL Feature Based VC

- `"WavLM" "voice conversion"`
- `"self-supervised speech representation" "voice conversion"`
- `"SSL features" "voice conversion"`
- `"HuBERT" "voice conversion" speaker embedding`
- `"content encoder" "speaker embedding" voice conversion`

### Speaker Embedding Controlled Synthesis

- `"ECAPA-TDNN" "speaker embedding" speech synthesis`
- `"speaker embedding controlled" speech synthesis`
- `"HiFi-GAN" "speaker embedding" conditioning`
- `"global speaker embedding" "voice conversion"`

### Linear Transformations In Articulatory Or Acoustic Feature Space

- `"linear transform" "articulatory features"`
- `"affine transform" "voice conversion"`
- `"linear regression" "voice conversion" acoustic features`
- `"GMM" "voice conversion" linear transformation`
- `"piecewise linear transformation" voice conversion`
- `"frequency warping" "voice conversion" linear transform`

### MRI / EMA Articulatory Datasets

- `"USC-TIMIT" "articulatory synthesis"`
- `"USC Long Single-Speaker" rtMRI speech synthesis`
- `"MOCHA-TIMIT" voice conversion`
- `"mngu0" articulatory speech synthesis`
- `"EMA dataset" "speech synthesis"`
- `"rtMRI" "speech synthesis" "HiFi-GAN"`

## Likely Venues

- ICASSP
- Interspeech
- IEEE/ACM TASLP
- Speech Communication
- Computer Speech & Language
- ASRU
- SLT
- ISCA workshops on speech synthesis, articulatory phonology, and speech production
- NeurIPS/ICLR only for broader SSL/representation papers, less likely for articulatory-specific VC

## Evidence That Would Support This Project

- Prior work shows articulatory features carry speaker-specific or style-specific information.
- Prior work uses articulatory inversion as a controllable intermediate representation for synthesis.
- Voice conversion work shows simple transforms in acoustic feature space can produce measurable speaker/style changes.
- SSL-based VC papers establish embedding-only baselines, making our main ablation meaningful.
- Articulatory datasets or models show low-dimensional trajectories are interpretable enough to analyze dimension-wise.
- Papers report that speaker embeddings alone do not fully control converted output, leaving room for articulatory trajectory effects.

## Evidence That Would Weaken This Project

- Strong evidence that ARTI-6 trajectories are intentionally speaker-invariant and carry little speaker-specific information.
- Prior work already demonstrates nearly the same ARTI-6 linear-transform VC idea.
- Synthesis model ignores small variations in 6D articulatory features when target speaker embedding is fixed.
- Target speaker embedding fully dominates perceived speaker identity, making articulatory transforms inaudible.
- Paired-prompt linear transforms are known to be unstable or uninterpretable without precise articulatory alignment.
- ARTI-6 inversion error is too high for transform effects to survive synthesis.

## Novelty Risks

- The project may be a straightforward reapplication of classic GMM/linear VC transforms to ARTI-6 rather than a new method.
- If related work already uses articulatory inversion for VC, novelty must shift to interpretability, ARTI-6 compactness, and ablation design.
- If ARTI-6 was trained partly for speaker-agnostic inversion, the transform may not encode speaker traits strongly.
- If synthesis conditioning is dominated by ECAPA embeddings, the main result may be negative.
- A paper-level claim will need more than audio demos: diagnostics, ablations, and possibly articulatory interpretability metrics.

## Practical Review Workflow

1. Start with recent surveys and papers using queries above in Google Scholar, Semantic Scholar, ACL Anthology, IEEE Xplore, ISCA Archive, and arXiv.
2. Build a table with columns: paper, task, articulatory representation, dataset, model, speaker control, transform method, evidence relevant to ARTI-6 LinearVC.
3. Prioritize papers using real articulatory data: EMA, ultrasound, rtMRI, USC-TIMIT, MOCHA-TIMIT, mngu0, LSS.
4. Then review SSL/WavLM VC baselines to define the embedding-only comparison.
5. Only after the demo works, decide whether the claim is:
   - interpretable contribution,
   - better VC quality,
   - feasibility of explicit articulatory manipulation,
   - or a negative result about speaker embedding dominance.
