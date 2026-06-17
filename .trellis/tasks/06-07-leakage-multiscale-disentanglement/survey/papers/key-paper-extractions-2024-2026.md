# Key Paper Extractions: 2024-2026 Speech/Singing Voice Field Map

Date: 2026-06-08.

Benchmark rule used here: papers without usable public code or checkpoints are
classified as `survey/reference only` unless the method can be evaluated through
an official dataset, official challenge artifacts, or a released baseline.

## GTSinger: A Global Multi-Technique Singing Corpus with Realistic Music Scores for All Singing Tasks

- Source links: https://arxiv.org/abs/2409.13832, https://proceedings.neurips.cc/paper_files/paper/2024/hash/023d2c1a17cf35b11a0cbb43a0677c91-Abstract-Datasets_and_Benchmarks_Track.html, https://github.com/AaronZ345/GTSinger, https://huggingface.co/datasets/AaronZ345/GTSinger
- Venue/status: NeurIPS 2024 Datasets and Benchmarks Track, spotlight.
- Idea: provide a controlled multilingual singing corpus with technique labels, realistic scores, manual alignments, and paired speech so multiple singing tasks can share the same data base.
- Method/resource: 80.59 hours of studio-recorded singing, 20 professional singers, nine languages, all four vocal ranges, six technique annotations, global style labels, musicxml scores, TextGrid/JSON annotations, and 16.16 hours of paired speech.
- Experiment-design pattern: dataset paper with four benchmark tasks: technique-controllable SVS, technique recognition, style transfer, and speech-to-singing conversion.
- Datasets: the released GTSinger corpus; the Hugging Face metadata exposes 28.6k rows and labels such as language, singer, technique indicators, speech paths, emotion, pace, range, phonemes, durations, and music-note fields.
- Metrics: task-dependent benchmark metrics in the paper; for this project the key reusable metrics are technique macro-F1, phone/alignment quality, F0 and duration controls, and cross-mode speaker verification.
- Ablations: dataset/task ablations are in the paper; the most important design ablation for this task is singer-disjoint versus singer-overlap splitting because GTSinger confounds singer and language.
- Code/data availability: public dataset on Hugging Face and Google Drive; public processing and benchmark code. Dataset license is noncommercial-style; verify use constraints before publication.
- Benchmark role: experiment-critical dataset and benchmark anchor.
- Relevance: best available public corpus for speech-versus-singing identity-gap analysis, technique leakage probes, and small-GPU frozen-feature studies. It does not support independent same-speaker language-leakage claims because language and singer are not independently crossed.

## Singing Voice Conversion Challenge 2025 / Evaluation Analysis

- Source links: https://vc-challenge.org/, https://arxiv.org/abs/2509.15629
- Venue/status: SVCC 2025 challenge; ICASSP 2026 challenge paper and 2026 extended analysis preprint.
- Idea: move the community beyond singer-identity conversion into singing style conversion, with in-domain and zero-shot style tracks.
- Method/resource: controlled challenge dataset drawn from GTSinger; seven singing styles: breathy, falsetto, mixed voice, pharyngeal, glissando, vibrato, and control; provided baselines Serenade and Vevo1.5.
- Experiment-design pattern: common training/evaluation data, submitted systems, crowd-sourced subjective tests, and objective metric correlation analysis.
- Datasets: Task 1 singer A with about 4.5 hours across seven styles; about 70 hours from other singers; no Task 2 singer B training data; waveform plus aligned phoneme/MIDI and style labels for training, waveform-only test set.
- Metrics: naturalness MOS, singer identity AB, style similarity XAB, objective metrics including chroma alignment and speaker-embedding non-match metrics.
- Ablations: challenge analysis compares systems, tracks, styles, and metric correlations. The key finding is that top systems can reach ground-truth-like singer identity but style and naturalness remain hard, especially breathy, glissando, and vibrato dynamics.
- Code/data availability: baseline systems are open-sourced; challenge data access is registration-controlled and GTSinger use is restricted by challenge rules.
- Benchmark role: current field benchmark for singing style conversion; useful as evaluation-design reference rather than a direct open dataset for all experiments.
- Relevance: establishes that subjective listening is still the gold standard and that objective metrics are not reliable replacements for singing style similarity.

## Serenade: A Singing Style Conversion Framework Based on Audio Infilling

- Source links: https://arxiv.org/abs/2503.12388, https://github.com/lesterphillip/serenade
- Venue/status: EUSIPCO 2025; SVCC 2025 baseline.
- Idea: formulate singing style conversion as audio infilling so target-style evidence can guide masked mel-spectrogram prediction while preserving melody.
- Method: flow-matching mel infilling with target mel complement plus disentangled acoustic features; cyclic training uses synthetic converted samples to reconstruct source targets; optional source-filter vocoder resynthesis with original F0.
- Experiment-design pattern: generalized SSC evaluation on GTSinger/SVCC-style data with subjective similarity/naturalness and style-specific comparisons.
- Datasets: GTSinger recipe in repo; SVCC 2025 baseline context.
- Metrics: overall similarity, naturalness, style-specific subjective tests; F0-resynthesis tradeoff measured through naturalness and style similarity.
- Ablations: F0 post-processing improved out-of-tune naturalness but slightly traded off target-style similarity; cyclic style-disentanglement and infilling setup are core design pieces.
- Code availability: public repository with install instructions and a GTSinger SSC recipe; noncommercial CC BY-NC-SA style license.
- Benchmark role: usable open baseline for singing style conversion.
- Relevance: strong baseline for technique/style leakage and a reminder that preserving source melody can conflict with target-style dynamics.

## Vevo / Vevo1.5 / Vevo2

- Source links: https://openreview.net/forum?id=anQDiQZhDP, https://arxiv.org/abs/2508.16332, https://github.com/open-mmlab/Amphion/tree/main/models/svc/vevosing, https://github.com/open-mmlab/Amphion/tree/main/models/svc/vevo2, https://huggingface.co/RMSnow/Vevo2
- Venue/status: Vevo ICLR 2025; Vevo2 arXiv 2025, revised 2026, accepted to IEEE/ACM TASLP according to arXiv.
- Idea: self-supervised disentanglement of content, style, prosody, and timbre enables controllable zero-shot speech and singing generation.
- Method: discrete tokenizers over SSL features; style/content tokens, prosody tokenizer, AR content-style modeling, flow-matching acoustic modeling, and timbre reference conditioning. Vevo2 adds unified prosody learning across speech/singing and multi-objective post-training.
- Experiment-design pattern: broad multi-task demonstration: TTS, SVS, VC, SVC, editing, style conversion, melody control, humming/instrument-to-singing.
- Datasets: Vevo trained on large audiobook speech; Vevo1.5/2 combine Emilia-101k with open-source singing data and internal SingNet subsets. Vevo2 model card lists Emilia-101k plus SingNet-7k.
- Metrics: subjective quality/similarity and task-specific objective measures in papers; for this project, the useful operational metrics are controllability versus timbre preservation and ASR/intelligibility checks.
- Ablations: Vevo uses tokenizer bottleneck/codebook choices as the disentanglement lever; Vevo2 reports explicit/implicit prosody learning and post-training task effects.
- Code availability: Amphion has inference recipes and pretrained models for Vevo1.5/2; training data includes internal SingNet, so full reproduction is limited.
- Benchmark role: usable inference baseline and architectural reference; not ideal for small-GPU full training.
- Relevance: strongest open family for unified speech/singing controllability, but large-model scale makes it a reference/baseline rather than a thesis-sized method to retrain.

## S2Voice: Style-Aware Autoregressive Modeling with Enhanced Conditioning for Singing Style Conversion

- Source links: https://arxiv.org/abs/2601.13629, https://honee-w.github.io/SVC-Challenge-Demo/
- Venue/status: accepted to ICASSP 2026; winning SVCC 2025 system for in-domain and zero-shot singing style conversion tracks.
- Idea: improve Vevo-style SSC by strengthening fine-grained style conditioning and timbre preservation.
- Method: FiLM-style layer-norm conditioning and style-aware cross-attention inside the AR LLM; global speaker embedding in flow-matching transformer; large curated singing corpus; supervised fine-tuning plus DPO.
- Experiment-design pattern: challenge system report with subjective listening, track-wise ranking, and ablations for style fidelity, timbre preservation, and generalization.
- Datasets: SVCC 2025 plus large internally curated web singing corpus.
- Metrics: naturalness, style similarity, singer similarity; leader on Task 1 style/singer similarity and Task 2 naturalness/style/singer similarity.
- Ablations: paper reports ablations supporting enhanced style conditioning, global speaker embedding, training data curation, and preference optimization.
- Code availability: no usable public implementation identified in this pass; audio demo available.
- Benchmark role: survey/reference only.
- Relevance: current high-water mark for singing style conversion, but its method relies on large data and training not aligned with a small-GPU thesis unless used as a design reference.

## Seed-VC: Zero-shot Voice Conversion with Diffusion Transformers

- Source links: https://arxiv.org/abs/2411.09943, https://github.com/Plachtaa/seed-vc
- Venue/status: arXiv 2024; active open-source project.
- Idea: reduce timbre leakage in zero-shot VC by perturbing source timbre during training and using a diffusion transformer over full reference context.
- Method: external timbre shifter during training, diffusion transformer, in-context reference modeling, and optional F0 conditioning for SVC.
- Experiment-design pattern: zero-shot speech VC against OpenVoice/CosyVoice and SVC extension with F0 conditioning.
- Datasets: paper-specific training data; repository supports public pretrained checkpoints and fine-tuning on custom data.
- Metrics: speaker similarity, WER/intelligibility, SVC qualitative/objective comparisons, real-time latency measurements in repo.
- Ablations: timbre shifter and reference-context usage are central; repo exposes multiple model sizes and content encoders.
- Code availability: public repo, Hugging Face demos/checkpoints, command-line and Web UI inference, fine-tuning path.
- Benchmark role: usable baseline for speech- and singing-prompted conversion.
- Relevance: directly matches the local Seed-VC path and timbre-leakage framing; best open baseline for testing whether multiscale residual conditioning helps.

## FreeSVC: Towards Zero-shot Multilingual Singing Voice Conversion

- Source links: https://arxiv.org/abs/2501.05586, https://github.com/freds0/free-svc, https://huggingface.co/alefiury/free-svc
- Venue/status: ICASSP 2025.
- Idea: zero-shot multilingual SVC through stronger separation of language/content and speaker identity.
- Method: enhanced VITS with Speaker-invariant Clustering based on HuBERT/ContentVec, ECAPA2 speaker encoder, RMVPE pitch extraction, and trainable language embeddings.
- Experiment-design pattern: multilingual/cross-lingual SVC with comparisons showing the importance of a multilingual content extractor.
- Datasets: AISHELL-1/3, CML-TTS, HiFiTTS, JVS, LibriTTS-R, NUS NHSS, OpenSinger, Opencpop, PopBuTFy, POPCS, VCTK, VocalSet.
- Metrics: paper reports cross-language conversion quality; practical repo supports metadata-driven source/target language and speaker conversion.
- Ablations: multilingual content extractor is highlighted as crucial; language embeddings and speaker encoder are the main disentanglement components.
- Code availability: public MIT-licensed repo, Docker path, training and inference scripts, Hugging Face checkpoint references.
- Benchmark role: usable cross-lingual SVC baseline, but not proof of same-speaker language disentanglement.
- Relevance: best open option for stress-testing cross-lingual content/speaker leakage, while keeping GTSinger language claims constrained.

## HQ-SVC: Towards High-Quality Zero-Shot Singing Voice Conversion in Low-Resource Scenarios

- Source links: https://arxiv.org/abs/2511.08496, https://ojs.aaai.org/index.php/AAAI/article/view/40249, https://github.com/ShawnPi233/HQ-SVC, https://huggingface.co/shawnpi/HQ-SVC
- Venue/status: AAAI 2026.
- Idea: high-quality zero-shot SVC can be achieved under lower resource budgets by jointly using a decoupled codec and synthesis refinements instead of large fully separate content/speaker modeling.
- Method: unified decoupled codec, pitch and volume modeling, differentiable signal processing, diffusion refinement, and voice super-resolution support.
- Experiment-design pattern: zero-shot SVC and super-resolution evaluations under low-resource training claims.
- Datasets: paper claims less than 80 hours and single consumer GPU; exact training data details require the paper for full audit.
- Metrics: naturalness, speaker similarity, efficiency/resource use, and super-resolution naturalness.
- Ablations: codec, pitch/volume, DSP, and diffusion refinements are the key components to test.
- Code availability: public inference code and pretrained models; training code marked unreleased as of the checked README.
- Benchmark role: usable inference baseline; limited for reproduction until training code is public.
- Relevance: strong comparison for FACodec-based low-resource SVC and a useful upper baseline for a small-GPU project.

## DAFMSVC: One-Shot Singing Voice Conversion with Dual Attention Mechanism and Flow Matching

- Source links: https://www.isca-archive.org/interspeech_2025/chen25d_interspeech.html
- Venue/status: Interspeech 2025.
- Idea: one-shot SVC must reduce timbre leakage while preserving melody and lyrics for unseen targets.
- Method: replace source SSL features with nearest target SSL features to suppress source-timbre leakage; dual cross-attention fuses speaker embeddings, melody, and linguistic content; flow matching generates audio.
- Experiment-design pattern: one-shot any-to-any SVC with subjective and objective comparisons against SOTA.
- Datasets: paper-specific SVC data; source page does not expose full dataset details.
- Metrics: timbre similarity, naturalness, subjective and objective evaluations.
- Ablations: expected components are target-SSL replacement, dual attention, and flow matching; detailed ablation requires paper PDF.
- Code availability: no official public code identified in this pass.
- Benchmark role: survey/reference only.
- Relevance: method is conceptually close to leakage control but not immediately benchmarkable.

## R2-SVC: Towards Real-World Robust and Expressive Zero-shot Singing Voice Conversion

- Source links: https://arxiv.org/abs/2510.20677
- Venue/status: arXiv 2025.
- Idea: clean-data SVC is brittle under real-world separated-vocal artifacts and expressive singing variation.
- Method: random F0 perturbation, music-separation artifact simulation such as reverb/echo, DNSMOS-filtered separated vocals and public corpora for speaker representation, and NSF harmonic/noise modeling.
- Experiment-design pattern: compare clean and noisy conditions on multiple SVC benchmarks.
- Datasets: clean vocals, separated vocals filtered by DNSMOS, and public singing corpora.
- Metrics: clean/noisy SVC benchmark scores, speaker/timbre preservation, naturalness, robustness.
- Ablations: robustness simulation, speaker representation enrichment, and NSF modeling.
- Code availability: no official public implementation identified in this pass.
- Benchmark role: survey/reference only.
- Relevance: useful threat model for robust evaluation; local Stage A should include separated-vocal/noise stress tests only after clean leakage results are stable.

## NaturalSpeech 3 / FACodec

- Source links: https://arxiv.org/abs/2403.03100, https://speechresearch.github.io/naturalspeech3/, https://github.com/lifeiteng/naturalspeech3_facodec, https://huggingface.co/amphion/naturalspeech3_facodec
- Venue/status: arXiv 2024; FACodec open implementation/checkpoints.
- Idea: speech generation improves when waveform representation is factorized into content, prosody, timbre, and residual acoustic detail.
- Method: FACodec with factorized vector quantization and gradient-reversal-style disentanglement, plus factorized diffusion generation in NaturalSpeech 3.
- Experiment-design pattern: zero-shot TTS at scale plus codec reconstruction and controllability tests.
- Datasets: NaturalSpeech 3 scales to large internal data; FACodec released for 16 kHz speech.
- Metrics: speech quality, similarity, prosody, intelligibility, codec reconstruction, zero-shot TTS comparisons.
- Ablations: factorized codec, subspace-specific diffusion, scaling to larger model/data.
- Code availability: FACodec public package, pretrained checkpoints on Hugging Face, runnable test and voice-conversion examples. Full NaturalSpeech 3 training is not open.
- Benchmark role: usable factorized-codec baseline for representation analysis; not a singing model by itself.
- Relevance: best immediate factorized-codec comparison for the proposed multiscale decomposition. Need validate behavior on singing because the released codec is speech-centered.

## SingMOS-Pro: A Comprehensive Benchmark for Singing Quality Assessment

- Source links: https://arxiv.org/abs/2510.01812, https://huggingface.co/datasets/TangRain/SingMOS-Pro
- Venue/status: accepted to ICASSP 2026.
- Idea: automatic singing quality assessment needs a stronger dataset than overall MOS-only labels.
- Method/resource: 7,981 generated singing clips from 41 models across 12 datasets, each rated by at least five experienced annotators; annotations cover lyrics, melody, and overall quality.
- Experiment-design pattern: benchmark objective quality estimators and strategies for heterogeneous MOS labels.
- Datasets: SingMOS-Pro public Hugging Face dataset.
- Metrics: MOS prediction and correlation metrics for overall, lyric, and melody quality; evaluator reliability.
- Ablations: data-standardization and MOS utilization strategies.
- Code availability: dataset public; baseline code availability not confirmed in this pass.
- Benchmark role: dataset/reference for evaluator calibration, not a conversion baseline.
- Relevance: useful if the task pivots toward singing quality/skill assessment or needs an auxiliary quality gate for generated outputs.

## Singing to Speech Conversion with Generative Flow

- Source links: https://link.springer.com/article/10.1186/s13636-025-00400-x
- Venue/status: EURASIP Journal on Audio, Speech, and Music Processing, 2025, open access.
- Idea: define singing-to-speech conversion as reducing pitch, rhythm, and timbre variation while retaining phonetic information.
- Method: generative flow model inspired by Glow-TTS with adjusted monotonic alignment search and duration prediction for singing/speech duration mismatch.
- Experiment-design pattern: compare against signal-processing and transcribe-and-synthesize baselines; test downstream lyrics-transcription augmentation.
- Datasets: paper-specific singing/speech resources; article emphasizes cross-domain S2S rather than singer conversion.
- Metrics: subjective naturalness, phonetic similarity to original singing, and low-resource lyrics transcription improvement.
- Ablations: alignment/duration handling and augmentation role.
- Code availability: no public code identified in this pass.
- Benchmark role: survey/reference only.
- Relevance: strong conceptual support for treating speech/singing as a controlled mode gap; not directly usable as a baseline without reimplementation.
