# Sing-MD / VocalVerse / QwenFeat-Vocal-Score

## Idea

VocalVerse reframes singing assessment as multi-dimensional expert critique and
popular-timbre assessment using multimodal foundation models. It is closer to
teacher-like feedback than pure karaoke scoring.

## Method

The released implementation includes a QwenAudio-based comment-generation and
scoring module plus a MuQ/SongEval-style audio scoring and ranking module. The
paper and README describe amateur pleasantness MOS, professional scores, textual
critiques, and model variants with LoRA fine-tuning.

## Datasets and Labels

The README describes an original pool of more than 100,000 a cappella KTV
recordings, a pre-screened set of 10,000 clips, and an open top-10-percent subset
of about 1,000 recordings. Labels include amateur MOS from 165 annotators, each
recording rated by five annotators, and professional 1-5 scores plus critiques
for timbre, breath, emotion, and technique. The Hugging Face dataset repository is
public, ungated, and contains visible WAV files. The dataset card README endpoint
returned `Entry not found`, recorded in `evolution.md`.

## Metrics and Experiments

Likely metrics include MOS/regression correlation, ranking accuracy, and
dimension-wise scoring accuracy. A local lightweight study should use the data
and smaller encoders, not the full QwenAudio model, unless compute allows.

## Ablations

The README notes MuQ scoring with and without speaker-identity decoupling via
gradient reversal. Other natural ablations: audio-only versus audio-plus-comment,
professional dimensions versus amateur MOS, and high-proficiency subset bias.

## Code Availability

Usable but heavy. GitHub and Hugging Face model repositories are reachable, the
model repository is public/ungated, and the model API lists code, weights, and
training scripts. The QwenAudio path depends on Qwen2-Audio-7B-Instruct and LoRA
weights; the MuQ/SongEval path is more plausible for a single-GPU adaptation.
License is non-commercial/no-derivatives.

## Relevance

Strong modern reference for multi-dimensional critique labels. It is not the
first small-GPU benchmark because the main model stack is large and the open
subset is pre-filtered toward technically proficient singers.
