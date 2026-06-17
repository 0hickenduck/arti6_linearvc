# Nakano / MiruSinger

## Idea

Early singing-skill work evaluated unknown melodies without relying on a musical
score, using pitch interval accuracy and vibrato as interpretable skill cues.
MiruSinger visualized real-time singing feedback against an estimated vocal
reference from a commercial CD.

## Method

Nakano et al. estimate pitch intervals from vocal F0 and use vibrato features to
classify good versus poor singing. MiruSinger adds real-time F0 visualization,
vocal F0 extraction from CD recordings, manual correction of reference F0, and
vibrato visualization.

## Datasets and Labels

The Interspeech 2006 work reports 600 sung sequences and classification across
male/female partitions. MiruSinger is a system paper rather than an open dataset.

## Metrics and Experiments

Reported classification accuracy is about 83.5 percent under leave-one-out in the
classic setup. The key evaluation pattern is interpretable cue prediction rather
than end-to-end scalar scoring.

## Ablations

Pitch interval features versus vibrato features are the important conceptual
ablation; modern replications should add rhythm and timbre cues.

## Code Availability

No verified reusable modern code/data. Treat as historical survey/reference.

## Relevance

Useful for resisting black-box karaoke scores: actionable feedback should expose
pitch stability, interval control, rhythm stability, vibrato, and expression
instead of only a scalar score.
