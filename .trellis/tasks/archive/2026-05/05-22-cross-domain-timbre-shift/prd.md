# Implement Cross-Domain Timbre Shift Mapper

## Goal
Implement a deep learning solution (Micro-Mapper) and a statistical baseline (Latent Steering) to handle cross-lingual and singing timbre shift in Voice Synthesis/Conversion, bypassing the ARTI-6 negative result.

## Clarified Objective
The current ARTI-6 demo is not a full speech-to-singing converter. ARTI-6 target
reconstruction does not preserve convincing singing melody/prosody, so the
defensible target for this ARTI-6 sandbox was narrower: predict or steer the same
speaker's **singing vocal-mode timbre embedding** from their speech embedding,
then apply that embedding as a controllable timbre/style condition.

Follow-up listening rejected this as an audible demo path. The embedding moves
objectively, but ARTI-6 does not render the moved embedding as perceptible
singing/timbre change. The target reconstruction sounds like stretched,
speech-like vocalization rather than singing, and source articulation plus target
embedding remains perceptually close to the source speaking voice. Future audio
demos should use a singing-aware decoder or foundation model rather than trying
to make ARTI-6 sing.

## What I already know
* We are moving away from linear transforms on articulatory features.
* The user prefers Deep Learning/End-to-End representation learning.
* The detailed technical pipeline and context are recorded in `research/brainstorming_minutes.md`.

## Open Questions
* Which same-speaker cross-domain dataset will we use for the real experiment?
* Which pre-trained embedding extractor will be used (e.g., ECAPA-TDNN, WavLM)?

## Requirements
* Implement Route A: "Difference of Means" statistical slider.
* Implement Route B: "Micro-Mapper" (small MLP/Transformer) to predict shifted embeddings.
* Set up a pipeline to run inference and pass modified embeddings into an off-the-shelf TTS/VC decoder.

## Acceptance Criteria
* [x] The base architecture is scaffolded.
* [x] The generic paired-audio manifest loader is built.
* [x] The Micro-Mapper model trains successfully.
* [x] A demo pipeline produces comparative audio (baseline vs. shifted).
* [x] The demo output is packaged as a portable zip for local download.
* [x] A true same-speaker cross-domain dataset is selected and converted to the manifest schema.
* [x] The Route A / Route B demo is re-run on same-speaker cross-language or speech-to-singing data.
* [x] A first subjective listening-evaluation page is generated and packaged.
* [x] A first speaker-recognition objective evaluation is implemented, run, and packaged.
* [x] The first singing-aware decoder pivot demo is implemented, run, and packaged.

## Demo Results
* Implemented the feasibility demo in `arti6_linearvc_demo/run_timbre_shift_mapper.py`.
* Ran the 5-train/1-test CMU ARCTIC engineering smoke check and wrote results to `outputs/timbre_shift_mapper/tiny_5train_1test/`.
* Packaged the demo for local download at `outputs/timbre_shift_mapper/tiny_5train_1test/tiny_5train_1test_report.zip`.
* Route A slider improved held-out cosine from `-0.0311` to `0.6212`.
* Route B Micro-Mapper improved held-out cosine to `0.7416`.
* Full run notes are recorded in `research/feasibility_demo_results.md`.
* Dataset candidates are recorded in `research/cross_domain_dataset_candidates.md`.

## GTSinger Same-Speaker Dabble Results
* Implemented `arti6_linearvc_demo/prepare_gtsinger_tiny.py` to download paired speech/singing rows from GTSinger and emit the project manifest schema.
* Generated `data/manifests/gtsinger_english_en_alto_1_6pairs.csv` for singer `EN-Alto-1`.
* Ran the 5-train/1-test speech-to-singing demo at `outputs/timbre_shift_mapper/gtsinger_en_alto_1_tiny_5train_1test/`.
* Packaged the downloadable report at `outputs/timbre_shift_mapper/gtsinger_en_alto_1_tiny_5train_1test/gtsinger_en_alto_1_tiny_5train_1test_report.zip`.
* Source speech embedding cosine to held-out singing target: `0.4469`.
* Route A slider cosine: `0.6646`.
* Route B Micro-Mapper cosine: `0.7166`.
* Added a blind subjective evaluation page at `subjective_eval.html` inside the same output directory and zip.
* Full run notes are recorded in `research/gtsinger_dabble_experiment.md`.

## GTSinger Round-Robin Validation Results
* Added `--selection-strategy round-robin-songs` to `prepare_gtsinger_tiny.py` so a same-singer manifest can span many songs instead of adjacent segments from one song.
* Generated `data/manifests/gtsinger_english_en_alto_1_roundrobin_31pairs.csv`.
* Ran a 30-train/1-test validation with `hidden_dim=128`, `epochs=1200`, and Route A alpha sweep.
* Output bundle: `outputs/timbre_shift_mapper/gtsinger_en_alto_1_roundrobin_30train_1test_e1200/gtsinger_en_alto_1_roundrobin_30train_1test_e1200_report.zip`.
* Source speech embedding cosine: `0.6516`.
* Route A slider cosine: `0.7364`.
* Route B Micro-Mapper cosine: `0.6966`.
* Route A alpha sweep peaks around `alpha=1.0`; over-steering to `1.25` or `1.5` hurts.
* Added `--synthesize-sweep-audio` and produced a new audio-sweep bundle with
  wav files for Route A alpha `0.00`, `0.25`, `0.50`, `0.75`, `1.00`, `1.25`,
  and `1.50`.
* Audio-sweep output bundle:
  `outputs/timbre_shift_mapper/gtsinger_en_alto_1_roundrobin_30train_1test_e1200_audio_sweep/gtsinger_en_alto_1_roundrobin_30train_1test_e1200_audio_sweep_report.zip`.
* Listening feedback on 2026-05-23: the alpha sweep is objectively measurable but
  not perceptually salient. Target reconstruction does not sound like real
  singing, and the target-embedding oracle does not create a convincing audible
  timbre shift. This turns the ARTI-6 audio route into a negative result rather
  than a demo to scale.
* Full interpretation is recorded in `research/objective_clarification_and_roundrobin_validation.md`.

## Speaker-Domain Objective Evaluation Results
* Implemented `arti6_linearvc_demo/run_speaker_domain_eval.py` to evaluate
  whether a modern speaker recognizer degrades across speech/singing domain
  mismatch.
* The script selects same-singer GTSinger speech/singing pairs, extracts
  SpeechBrain ECAPA embeddings, and reports closed-set speaker-identification
  accuracy plus speaker-verification EER.
* Ran a 20-speaker seeded-random evaluation with 2 enroll and 2 query pairs per
  domain.
* Output bundle:
  `outputs/speaker_domain_eval/gtsinger_20spk_seed17_2enroll_2query/gtsinger_20spk_seed17_2enroll_2query_report.zip`.
* Speech enroll -> speech query: ID accuracy `0.950`, EER `0.024`.
* Singing enroll -> singing query: ID accuracy `0.825`, EER `0.074`.
* Speech enroll -> singing query: ID accuracy `0.700`, EER `0.125`.
* Singing enroll -> speech query: ID accuracy `0.750`, EER `0.100`.
* Interpretation: the speech/singing mismatch is objectively visible even before
  synthesis evaluation, so this can become a formal metric for whether a timbre
  shift makes cross-domain identity easier or harder to recover.
* Full run notes and literature positioning are recorded in
  `research/speaker_domain_objective_eval.md`.

## Seed-VC Singing-Aware Pivot Results
* Cloned Seed-VC into `external/seed-vc` and installed the minimal inference
  dependencies without downgrading the current CUDA torch stack.
* Implemented `arti6_linearvc_demo/run_seedvc_svc_demo.py`.
* Ran an external Seed-VC example smoke test at
  `outputs/seedvc_pivot/smoke_example/`.
* Ran a GTSinger EN-Alto-1 -> EN-Tenor-1 zero-shot singing voice conversion demo
  using real singing as source content/melody and target speech/singing
  references as timbre prompts.
* Generated an 8-step smoke bundle:
  `outputs/seedvc_pivot/gtsinger_en_alto1_to_en_tenor1_8steps/gtsinger_en_alto1_to_en_tenor1_8steps_report.zip`.
* Generated the main 30-step bundle:
  `outputs/seedvc_pivot/gtsinger_en_alto1_to_en_tenor1_30steps/gtsinger_en_alto1_to_en_tenor1_30steps_report.zip`.
* Generated a second 30-step bundle in the reverse direction:
  `outputs/seedvc_pivot/gtsinger_en_tenor1_to_en_alto2_30steps/gtsinger_en_tenor1_to_en_alto2_30steps_report.zip`.
* Implemented `arti6_linearvc_demo/run_seedvc_svc_matrix.py` and ran a
  three-pair English triangle matrix.
* English triangle bundle:
  `outputs/seedvc_pivot/english_triangle_30steps/english_triangle_30steps_report.zip`.
* English triangle aggregate: speech-prompt target advantage mean `0.320`,
  singing-prompt target advantage mean `0.439`, and source-prompt source-speech
  similarity mean `0.741`.
* Ran a related English -> Japanese cross-language Seed-VC probe:
  `outputs/seedvc_pivot/gtsinger_en_alto1_to_ja_tenor1_30steps/gtsinger_en_alto1_to_ja_tenor1_30steps_report.zip`.
* English -> Japanese probe: Japanese speech prompt similarity to target singing
  reference `0.444`, Japanese singing prompt similarity to target singing
  reference `0.608`, and source-speech prompt similarity to source speech
  reference `0.690`.
* Added a blind subjective-evaluation page to the 30-step bundle using target
  singing reference as the visible reference.
* The speaker-similarity probe behaves as expected: target-speech-reference
  conversion is closest to the target speech reference, target-singing-reference
  conversion is closest to the target singing reference, and source-speech
  conversion stays close to source identity.
* Full run notes are recorded in `research/seedvc_pivot_demo.md`.

## Cross-Language Speech/Singing Axis
* Recorded the user's narrower English/Japanese speech/singing identity idea in
  `research/cross_language_speech_singing_axis.md`.
* Literature check: JukeBox already studies multilingual singer recognition and
  shows spoken-voice speaker recognizers degrade on singing, including language
  effects. Therefore the broad "speaker ID drops under singing/language
  mismatch" claim is not novel by itself.
* More plausible novelty: use a controlled speech/singing × language grid as an
  evaluation target for speech-reference-to-singing-timbre transfer.
* Local GTSinger status: English metadata currently covers `EN-Alto-1`,
  `EN-Alto-2`, `EN-Tenor-1`; Japanese metadata covers `JA-Soprano-1`,
  `JA-Tenor-1`. This supports English/Japanese cross-language Seed-VC demos, but
  not yet strict same-person English/Japanese speech/singing claims.

## Current Limitation
The current manifest is cross-speaker speaking data (`bdl` to `slt`), not true
same-speaker cross-domain data. It validates the pipeline mechanics and supports
the feasibility of the direction, but a real thesis experiment still needs a
same-speaker cross-language or speech-to-singing dataset.

The GTSinger dabble resolves this limitation for the first demo by using
same-singer speech-to-singing pairs. The remaining limitation is scale: one
singer and one held-out segment is not enough for a thesis claim.

The larger round-robin split suggests the current strongest direction is the
Route A singing-mode slider. Route B should be treated as a nonlinear refinement
that needs multi-singer training before it can be expected to beat the slider.

However, after listening to the audio-sweep bundle, the ARTI-6 synthesis path is
not perceptually viable. Route A can remain as an embedding-space baseline and
diagnostic, but the next audible demo needs a decoder/model whose latent space
actually carries singing pitch, breath, phonation, timing, and musical prosody.

The speaker-domain objective evaluation resolves a separate question: the
research problem is not invented by the demo. Speaker-recognition systems do
degrade under genre/domain and language mismatch, and our GTSinger probe
reproduces that effect on the exact speech/singing setting needed here.

The ARTI-6 negative result is recorded in
`research/arti6_perceptual_negative_result.md`.

The Seed-VC pivot establishes the new baseline harness: singing source in,
speech/singing reference prompts in, converted singing out, subjective page,
speaker-similarity diagnostics, and portable zip. The next scale-up should make
this multi-speaker and multi-song, then test whether speech references can
reliably control singing timbre.

## Out of Scope
* Training large foundation models from scratch.
* Pure DSP (WORLD/VTLN) techniques.
