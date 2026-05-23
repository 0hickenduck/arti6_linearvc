# Cross-Domain Dataset Candidates

**Date:** 2026-05-22  
**Purpose:** Correct the CMU ARCTIC smoke-test limitation and identify datasets
that can support the actual same-speaker cross-domain timbre-shift claim.

## Local Data Check

The current repository does not contain a valid target dataset for this thesis
question. Local data is limited to CMU ARCTIC `bdl`/`slt` manifests and generated
outputs. CMU ARCTIC is useful for exercising the pipeline, but it is
cross-speaker speaking data, not same-speaker cross-language or same-speaker
speech-to-singing data.

## Best Immediate Direction: Speech to Singing

| Dataset | Fit | Notes |
| --- | --- | --- |
| NHSS / NUS-HLT Speak-Sing | Strong | Parallel speech and singing by the same singers. Official page says it has 100 songs sung and spoken by 10 singers, 7 hours total, plus utterance/word annotations. This is the cleanest next demo target. |
| GTSinger | Strong | Large modern corpus: 80.59 hours of singing, 20 professional singers, nine languages, and 16.16 hours of paired speech. Best for a larger thesis-grade experiment if access and preprocessing are manageable. |
| JVS + JVS-MuSiC | Strong for Japanese speech/singing | JVS-MuSiC has 100 singers; the announcement says their reading voices are stored in the JVS corpus. Good same-speaker Japanese speech-to-singing target. Check license constraints before packaging audio examples. |
| NUS-48E | Medium | 169 minutes of sung and spoken lyrics by 12 subjects. Smaller than NHSS and older, but still aligned with the speech/singing question. |
| RAVDESS | Medium smoke test | Same actors perform speech and song, but the content is short, emotional, and stylized. Useful for a tiny sanity check, less ideal for the main thesis claim. |

Recommendation: use NHSS first. It is explicitly parallel speech/singing, small
enough to preprocess quickly, and close to the exact Route A / Route B setup.

## Cross-Language Same-Speaker Options

| Dataset | Fit | Notes |
| --- | --- | --- |
| TidyVoiceX_ASV | Strong for embedding analysis | Built from Common Voice for cross-lingual speaker verification. Page states about 5,000 speakers have recordings in more than one language, across 40 languages. Usage restrictions forbid speaker identification or recovering identity, so use this for verification/embedding analysis only unless license review allows the planned synthesis outputs. |
| VoxTube | Good mining target | Multilingual speaker recognition dataset from CC BY YouTube videos: 5,040 POIs, over 4.4M utterance segments, more than 10 languages. It has language/gender labels, but metadata and YouTube availability can drift. License is CC BY-NC-SA 4.0. |
| TELVID | Good if accessible | Interspeech 2025 description says 300 multilingual speakers each have multiple telephone/video recordings in Tunisian Arabic, North African French and/or English. It is expected through the LDC catalog, so access may require institutional membership. |

Recommendation: treat cross-language data discovery as a separate research track.
TidyVoiceX is promising for analyzing whether ECAPA/WavLM speaker embeddings drift
with language. VoxTube and TELVID are better for mining real speaker-language
pairs, but they introduce licensing, identity, and availability constraints.

## Automatic Dataset Discovery Track

The user is right that automatically finding same-speaker cross-domain data can
itself be a research direction. A concrete version:

1. Collect candidate corpora with `audio_path`, `domain`, `language`, and any
   available `speaker_id` / `person_id`.
2. Run VAD and quality filters: mono speech/singing, duration range, SNR floor,
   no heavy music bed for speech experiments.
3. Extract speaker embeddings with ECAPA-TDNN and optionally WavLM/x-vector.
4. If speaker IDs exist, pair the same ID across domains; if not, cluster by
   speaker-verification cosine and manually audit high-confidence pairs.
5. Verify domain labels with ASR/language ID for multilingual speech and
   speech-vs-singing classification for singing corpora.
6. Emit the project manifest schema:
   `utterance_id, speaker_id, source_domain, target_domain, source_wav, target_wav`.
7. Score the candidate set by number of speakers, pairs per speaker, language or
   singing coverage, audio quality, license, and whether redistribution of demo
   audio is allowed.

This is publishable as a dataset-mining / benchmark-building contribution if the
main modeling result needs a stronger data foundation.

## Sources

- NHSS official page: https://hltnus.github.io/NHSSDatabase/index.html
- GTSinger paper: https://arxiv.org/abs/2409.13832
- JVS-MuSiC paper: https://arxiv.org/abs/2001.07044
- JVS-MuSiC release announcement: https://hts.sp.nitech.ac.jp/hts-users/spool/2020/msg00000.html
- NUS-48E paper/PDF: https://smcnus.comp.nus.edu.sg/archive/pdf/2012-2013/2013_05-Pub-NUS-48E.pdf
- RAVDESS Zenodo page: https://zenodo.org/records/1188976
- TidyVoiceX_ASV page: https://mozilladatacollective.com/datasets/cmihtsewu023so207xot1iqqw
- VoxTube page: https://idrnd.github.io/VoxTube/
- TELVID Interspeech page: https://www.isca-archive.org/interspeech_2025/jones25_interspeech.html
