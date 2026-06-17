# GTSinger

## Idea

GTSinger is a large professional-singer corpus intended to support singing voice
synthesis and singing technique control. For singing-skill work, its value is the
structured technique annotation rather than overall ability scoring.

## Method

The dataset contains professional vocals with phoneme-level alignments, realistic
scores, paired speech for part of the corpus, and explicit technique labels. The
paper defines benchmark tasks for technique-controllable SVS, technique
recognition, style transfer, and speech-to-singing conversion.

## Datasets and Labels

80.59 hours from 20 professional singers in 9 languages. Technique labels cover
mixed voice, falsetto, breathy voice, pharyngeal voice, vibrato, and glissando.
Hugging Face metadata includes per-segment fields such as `mix_tech`,
`falsetto_tech`, `breathy_tech`, `pharyngeal_tech`, `vibrato_tech`,
`glissando_tech`, `language`, `singer`, `emotion`, `singing_method`, `pace`, and
`range`.

## Metrics and Experiments

Technique recognition can use accuracy, macro-F1, UAR, and per-technique
confusion matrices. Splits must be singer-disjoint to avoid learning artist
identity. For transfer to amateur assessment, evaluate only technique detection,
not overall skill quality.

## Ablations

Relevant ablations: SSL embedding choice, F0/vibrato feature additions, segment
duration, singer-disjoint versus random splits, and cross-language transfer.

## Code Availability

Usable. `git ls-remote https://github.com/AaronZ345/GTSinger` succeeded. The repo
contains data processing and technique-recognition code, and the README points to
released full and processed data on Hugging Face and Google Drive with a
non-commercial license.

## Relevance

Strong benchmark for technique/attribute classifiers, but it is not a direct
amateur skill dataset because all singers are professionals.
