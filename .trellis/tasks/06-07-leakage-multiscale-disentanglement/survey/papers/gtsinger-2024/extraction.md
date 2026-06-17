# GTSinger (2024)

## Idea

GTSinger provides a high-quality global, multi-technique singing dataset with
paired speech, phoneme alignments, music scores, technique labels, and benchmark
tasks for singing research.

## Method/Data Design

The dataset includes 80.59 hours of singing, 20 professional singers, nine
languages, six technique annotations, phoneme-to-audio alignments, global style
labels, realistic music scores, and 16.16 hours of paired speech.

## Experiment Design

The paper runs benchmark experiments for technique-controllable singing voice
synthesis, technique recognition, style transfer, and speech-to-singing
conversion.

## Datasets and Metrics

GTSinger itself is the dataset. Metrics vary by benchmark task and include
technique recognition metrics, synthesis/style metrics, and speech-to-singing
conversion evaluation.

## Ablations

Benchmark and dataset analyses demonstrate task suitability. For the current
project, the critical design is singer-disjoint, song-aware, phone-aware
evaluation rather than reusing GTSinger's original benchmark splits blindly.

## Code Availability

The GitHub repository provides dataset/code and processed data links. Usable as
the primary dataset after confirming local data access and manifest integrity.

## Relevance

GTSinger supports the speech-versus-singing claim but not independent language
disentanglement: each singer is associated with a language in the local notes, so
speaker and language are confounded for language-leakage claims.

Sources: https://arxiv.org/abs/2409.13832,
https://papers.nips.cc/paper_files/paper/2024/hash/023d2c1a17cf35b11a0cbb43a0677c91-Abstract-Datasets_and_Benchmarks_Track.html,
https://github.com/AaronZ345/GTSinger

