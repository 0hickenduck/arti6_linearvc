# Cross-Language Speech/Singing Axis

**Date:** 2026-05-23

## User Hypothesis

The next niche angle is not only:

- English singer sings English songs.
- English speaker speaks English.

It should also consider a controlled language/domain grid:

- English speaker speaks English.
- English speaker sings English.
- English speaker speaks Japanese.
- English singer sings Japanese.

The research question is whether speaker/singer identity becomes less stable as
we cross both **vocal mode** (`speech` vs. `singing`) and **language** (`English`
vs. `Japanese`), and whether a timbre-transfer model can recover the identity
cue that speaker-recognition models lose.

## Literature Check

This is not a blank area.

- JukeBox is a multilingual singer-recognition dataset. The paper reports that
  speaker-recognition systems trained only on spoken voice perform poorly on
  singing voice, and it explicitly evaluates language effects in singing voice:
  https://www.isca-archive.org/interspeech_2020/chowdhury20b_interspeech.pdf
- The JukeBox dataset page also frames the same issue: singing has broader
  vocal dynamics than everyday speech, and current spoken-voice speaker
  recognizers struggle on singing data:
  https://iprobe.cse.msu.edu/dataset_detail.php?%3Ftitle=JukeBox%3A_A_Speaker_Recognition_Dataset_with_Multi-lingual_Singing_Voice_Audio&id=8
- GTSinger provides a useful controlled corpus for this project: 80.59 hours of
  singing, 20 singers, nine languages, and 16.16 hours of paired speech:
  https://arxiv.org/abs/2409.13832
- The public GTSinger Hugging Face page confirms the same nine-language and
  paired-speech structure:
  https://huggingface.co/datasets/AaronZ345/GTSinger

Implication: do not claim novelty for the broad statement "speaker ID degrades
for singing or language mismatch." That has prior work. The more defensible
novelty is a narrower, controlled protocol and demo around **speech-reference
to singing-timbre transfer under language/domain mismatch**.

## Local Data Status

Downloaded metadata currently available under `data/gtsinger_seedvc/`:

- English: `EN-Alto-1`, `EN-Alto-2`, `EN-Tenor-1`.
- Japanese: `JA-Soprano-1`, `JA-Tenor-1`.

This supports English/Japanese cross-language Seed-VC demos, but it does **not**
yet prove the strict same-person condition across English and Japanese. The
current singer IDs are language-specific, so the first cross-language demo should
be framed as cross-singer and cross-language, not same-speaker multilingual.

## Near-Term Demo Path

Use the current Seed-VC harness for an English/Japanese conversion matrix:

- English source singing -> Japanese target speech prompt.
- English source singing -> Japanese target singing prompt.
- Japanese source singing -> English target speech prompt.
- Japanese source singing -> English target singing prompt.

This asks whether speech prompts remain useful as singing timbre prompts when the
target reference language changes. It is directly relevant to the user-facing
demo, even though it is not the strict same-person multilingual objective.

## First Related Demo

Ran one English -> Japanese Seed-VC probe:

```text
outputs/seedvc_pivot/gtsinger_en_alto1_to_ja_tenor1_30steps/gtsinger_en_alto1_to_ja_tenor1_30steps_report.zip
```

Selected items:

- English source singing: `EN-Alto-1`, song `yesterday once more`.
- Japanese target reference: `JA-Tenor-1`, song `Heartful Song`.

Speaker-similarity probe:

| Converted output | Source singing | Target speech ref | Target singing ref | Source speech ref |
| --- | ---: | ---: | ---: | ---: |
| source singing -> target speech ref | 0.208 | 0.317 | 0.444 | 0.127 |
| source singing -> target singing ref | 0.175 | 0.269 | 0.608 | 0.154 |
| source singing -> source speech ref | 0.753 | 0.075 | 0.045 | 0.690 |

Interpretation:

- Cross-language target prompting is technically feasible in the current
  Seed-VC harness.
- The Japanese speech prompt is not useless; it moves away from source identity
  and closer to the Japanese target references.
- The Japanese singing prompt is still stronger, so the core research gap
  remains: how to predict or recover singing-timbre conditioning from speech
  references, especially when language changes.

## Objective Evaluation Path

Extend `run_speaker_domain_eval.py` from a 2-domain protocol:

```text
speech enroll -> speech query
singing enroll -> singing query
speech enroll -> singing query
singing enroll -> speech query
```

to a domain/language protocol when a same-person multilingual dataset is found:

```text
English speech -> English speech
English speech -> English singing
English speech -> Japanese speech
English speech -> Japanese singing
English singing -> Japanese singing
Japanese speech -> Japanese singing
```

Primary metrics:

- closed-set ID accuracy;
- speaker-verification EER;
- same-speaker cosine score and impostor score;
- target-identity recovery after conversion.

## Dataset Search Direction

If GTSinger does not provide the strict same-person English/Japanese grid, this
becomes a dataset/research contribution:

1. Find a dataset where the same person has speech and singing in multiple
   languages.
2. If no dataset exists, automatically mine candidate singers with multilingual
   songs plus interview/speech clips, then verify identity with speaker
   embeddings and human spot checks.
3. Treat the mined dataset as an evaluation resource for speech/singing/language
   identity robustness.

This is adjacent to JukeBox but different in emphasis: JukeBox targets
multilingual singer recognition, while the proposed resource would target
same-person speech/singing/language transfer and evaluation.
