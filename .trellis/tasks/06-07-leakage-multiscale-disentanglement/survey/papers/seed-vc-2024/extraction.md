# Seed-VC (2024)

## Idea

Zero-shot VC fails when content features leak source timbre, reference timbre is
under-modeled, and training/reconstruction differs from inference. Seed-VC
addresses these issues with a timbre shifter during training and a diffusion
transformer conditioned on full reference context.

## Method

The model uses Whisper-small semantic features, CAM++ speaker/timbre vectors,
BigVGAN vocoding, flow matching diffusion transformer blocks, and reference
audio context. The SVC extension adds F0 conditioning from RMVPE and pitch-shift
adjustments.

## Experiment Design

Zero-shot speech VC is evaluated against OpenVoice and CosyVoice. Singing VC is
evaluated with F0 conditioning and compared against RVCv2-style baselines. The
paper emphasizes speaker similarity, intelligibility, quality, and F0
preservation.

## Datasets and Metrics

Training uses Emilia-101k. Evaluation includes LibriTTS test-clean sources and
seed-tts-eval references. Metrics include SECS, WER, CER, DNSMOS P.835, F0
correlation/RMSE, and singing quality measures.

## Ablations

The paper reports or discusses ablations for timbre shifter, full reference
enrollment, and timbre shifter methods. Some ablations are listed as future work
or limited.

## Code Availability

Open-source code and pretrained models are available. The local repository
already has Seed-VC GTSinger pivot scripts and matrix results, making Seed-VC the
right downstream target for Stage C.

## Relevance

Seed-VC is both enabling infrastructure and novelty risk. A Stage C paper cannot
only show that speech and singing references condition Seed-VC differently; it
must show that a stable-core plus predicted singing-mode residual improves over
raw speech reference, global shift, residual MLP, and singing-reference oracle
gap metrics on unseen singers.

Sources: https://arxiv.org/abs/2411.09943,
https://github.com/Plachtaa/seed-vc,
https://plachtaa.github.io/seed-vc/

