# Speaker-Domain Objective Evaluation

**Date:** 2026-05-22  
**Reason:** The ARTI-6 singing reconstruction is not good enough to use as the
main evidence. We need an objective check for the core research claim: speaker
identity becomes harder to recover when speech and singing domains are mismatched.

## Literature Positioning

This is not an untouched problem, but it is a useful objective for this project.

- CN-Celeb frames genre mismatch as a major speaker-recognition challenge,
  including cases such as reading-speech enrollment and singing-audio testing.
  It reports a large multi-genre corpus with 3,000 speakers and 11 genres:
  https://arxiv.org/abs/2012.12468
- A Mandarin text-dependent speaker-verification study directly compares normal
  reading speech and singing speech for ASV:
  https://www.mdpi.com/2076-3417/9/13/2636
- Cross-lingual speaker-verification papers also show that language mismatch
  degrades verification and motivates adaptation or calibration, for example
  ADDA-based cross-lingual SV:
  https://arxiv.org/abs/1908.01447
- GTSinger is a strong fit for this task because it has 20 professional singers,
  nine languages, 80.59 hours of singing, and 16.16 hours of paired speech:
  https://arxiv.org/abs/2409.13832

Interpretation: we should not claim novelty for "speaker ID drops under domain
mismatch" by itself. Instead, use it as an objective evaluation target: a good
speech-to-singing timbre mapper should make cross-domain same-speaker identity
more consistent under a speaker recognizer, while not collapsing different
speakers.

## Implemented Script

Script:

```text
arti6_linearvc_demo/run_speaker_domain_eval.py
```

It:

1. Selects GTSinger same-singer speech/singing paired rows.
2. Writes `selection_manifest.csv`.
3. Extracts `speechbrain/spkrec-ecapa-voxceleb` embeddings for every selected
   speech and singing file.
4. Builds per-speaker centroids from enrollment rows.
5. Reports closed-set speaker-identification accuracy.
6. Reports speaker-verification EER from same-speaker versus impostor centroid
   trials.
7. Writes an HTML report, plot, embedding arrays, summary JSON, and optional zip.

The script supports deterministic metadata order and seeded-random selection:

```bash
.venv/bin/python arti6_linearvc_demo/run_speaker_domain_eval.py --help
```

## Main 20-Speaker Run

Command:

```bash
.venv/bin/python arti6_linearvc_demo/run_speaker_domain_eval.py \
  --root data/gtsinger_domain_eval \
  --output-dir outputs/speaker_domain_eval/gtsinger_20spk_seed17_2enroll_2query \
  --num-speakers 20 \
  --enroll-per-domain 2 \
  --query-per-domain 2 \
  --selection-strategy seeded-random \
  --seed 17 \
  --bundle-zip
```

Output bundle:

```text
outputs/speaker_domain_eval/gtsinger_20spk_seed17_2enroll_2query/gtsinger_20spk_seed17_2enroll_2query_report.zip
```

Run metadata:

- Dataset: GTSinger (`AaronZ345/GTSinger`)
- Languages: Chinese, English, French, German, Italian, Japanese, Korean,
  Russian, Spanish
- Speakers: 20
- Enrollment/query pairs per domain: 2 / 2
- Device: CUDA
- Extractor: `speechbrain/spkrec-ecapa-voxceleb`
- Elapsed time: 289.65 seconds
- Query trials per protocol: 40 closed-set queries, 800 verification scores

## Main Results

| Protocol | ID accuracy | EER | Same-speaker score | Impostor score | Mean margin |
| --- | ---: | ---: | ---: | ---: | ---: |
| speech enroll -> speech query | 0.950 | 0.024 | 0.722 | 0.176 | 0.251 |
| singing enroll -> singing query | 0.825 | 0.074 | 0.607 | 0.233 | 0.123 |
| speech enroll -> singing query | 0.700 | 0.125 | 0.390 | 0.124 | 0.055 |
| singing enroll -> speech query | 0.750 | 0.100 | 0.385 | 0.118 | 0.079 |

The strongest domain-internal condition is speech->speech. Singing->singing is
already harder, and the two cross-domain protocols are worse still. The largest
visible shift is the same-speaker score: roughly `0.72` in speech->speech versus
roughly `0.39` in cross-domain protocols.

## Earlier 10-Speaker Sanity Run

Command:

```bash
.venv/bin/python arti6_linearvc_demo/run_speaker_domain_eval.py \
  --root data/gtsinger_domain_eval \
  --output-dir outputs/speaker_domain_eval/gtsinger_10spk_2enroll_2query \
  --num-speakers 10 \
  --enroll-per-domain 2 \
  --query-per-domain 2 \
  --bundle-zip
```

Output bundle:

```text
outputs/speaker_domain_eval/gtsinger_10spk_2enroll_2query/gtsinger_10spk_2enroll_2query_report.zip
```

| Protocol | ID accuracy | EER | Same-speaker score | Impostor score | Mean margin |
| --- | ---: | ---: | ---: | ---: | ---: |
| speech enroll -> speech query | 1.000 | 0.006 | 0.706 | 0.170 | 0.333 |
| singing enroll -> singing query | 1.000 | 0.061 | 0.604 | 0.239 | 0.150 |
| speech enroll -> singing query | 0.950 | 0.097 | 0.460 | 0.136 | 0.153 |
| singing enroll -> speech query | 0.900 | 0.150 | 0.435 | 0.163 | 0.120 |

This smaller run showed the same direction, but the 20-speaker run is a better
baseline because it spans all available GTSinger singers with seeded sampling.

## Interpretation for the Research Direction

This objective probe supports three decisions:

1. Keep speaker-recognition robustness as an objective evaluation metric.
2. Use cross-domain EER and same-speaker score recovery to judge timbre-shift
   models, not just ECAPA cosine to one target embedding.
3. Move true audio-demo work away from ARTI-6 reconstruction and toward a
   singing-capable decoder or foundation model. ARTI-6 can still serve as a
   controlled embedding-injection sandbox, but it cannot be the final singing
   synthesis path.

## Next Experiments

- Evaluate current Route A and Route B shifted embeddings with the same
  speaker-domain protocol: does shifting speech embeddings toward singing reduce
  speech->singing mismatch without increasing impostor confusion?
- Repeat the objective evaluation with a second embedding extractor, such as
  WavLM-based speaker embeddings, to avoid overfitting the conclusion to ECAPA.
- For the actual listening demo, replace the ARTI-6 decoder with a singing-aware
  synthesis or voice-conversion foundation model and keep this speaker-domain
  protocol as the objective metric.
