# Directory Structure

> How backend code is organized in this project.

---

## Overview

<!--
Document your project's backend directory structure here.

Questions to answer:
- How are modules/packages organized?
- Where does business logic live?
- Where are API endpoints defined?
- How are utilities and helpers organized?
-->

(To be filled by the team)

---

## Directory Layout

```
<!-- Replace with your actual structure -->
src/
├── ...
└── ...
```

---

## Module Organization

<!-- How should new features/modules be organized? -->

(To be filled by the team)

---

## Naming Conventions

<!-- File and folder naming rules -->

(To be filled by the team)

---

## Examples

<!-- Link to well-organized modules as examples -->

### Scenario: ARTI-6 Research Demo Scripts

#### 1. Scope / Trigger

Research demos live under `arti6_linearvc_demo/` and are executable Python CLI
scripts. Add a new script there when the work reuses the local ARTI-6 checkout,
paired manifests, and `outputs/` report pattern.

This spec applies to scripts such as:

- `arti6_linearvc_demo/prepare_gtsinger_tiny.py`
- `arti6_linearvc_demo/run_arti6_smoke.py`
- `arti6_linearvc_demo/run_linearvc_floor.py`
- `arti6_linearvc_demo/run_timbre_shift_mapper.py`
- `arti6_linearvc_demo/run_speaker_domain_eval.py`
- `arti6_linearvc_demo/run_seedvc_svc_demo.py`
- `arti6_linearvc_demo/run_seedvc_svc_matrix.py`
- `arti6_linearvc_demo/build_subjective_eval.py`

#### 2. Signatures

Use explicit argparse CLIs. A timbre-shift mapper run has this command shape:

```bash
.venv/bin/python arti6_linearvc_demo/run_timbre_shift_mapper.py \
  --manifest data/manifests/cmu_arctic_6pairs.csv \
  --output-dir outputs/timbre_shift_mapper/tiny_5train_1test \
  --train-count 5 \
  --test-index 5 \
  --epochs 400
```

#### 3. Contracts

Manifest rows must include:

- `utterance_id`: stable paired utterance identifier.
- `source_wav`: source-side wav path.
- `target_wav`: target-side wav path.

Optional manifest fields should be preserved in summaries when useful:

- `speaker_id`
- `source_domain`
- `target_domain`
- `source_speaker`
- `target_speaker`

Output directories should contain:

- `summary.json`: machine-readable run metadata, metrics, and artifact paths.
- `index.html`: local inspection report when the demo produces listening or plot artifacts.
- `audio/`: generated wav conditions.
- `arrays/`: saved numpy arrays and small model state files.
- `plots/`: diagnostic figures.
- `<output-dir-name>_report.zip`: optional portable bundle for downloading server-side demos locally.
- `subjective_eval.html` and `subjective_eval_key.json`: optional blind listening-test page and condition key when subjective evaluation is part of the run.

Timbre-shift mapper runs may also include optional Route A slider-sweep wav files
when `--synthesize-sweep-audio` is passed. These belong in `audio/` beside the
main comparison conditions and should be referenced by `summary.json` and
`index.html`.

Speaker-domain objective evaluation outputs use the same report convention but
do not write audio. They should contain:

- `selection_manifest.csv`: exact GTSinger speech/singing rows used for enrollment and query.
- `summary.json`: protocol metrics, extractor metadata, and artifact paths.
- `index.html`: compact metrics report for local viewing.
- `arrays/embeddings.npz`: extracted embedding matrix plus speaker/domain/split labels.
- `plots/speaker_domain_protocols.png`: identification and EER comparison.
- `<output-dir-name>_report.zip`: optional portable bundle for downloading server-side metrics locally.

Seed-VC pivot demos use the same report convention for singing-aware conversion.
They should contain:

- `selection_manifest.csv`: exact GTSinger source and target rows.
- `summary.json`: selected rows, Seed-VC parameters, conversion logs, audio
  paths, audio metadata, and speaker-similarity scores.
- `index.html`: compact listening report.
- `audio/`: source singing, speech/singing references, and converted singing outputs.
- `logs/`: Seed-VC stdout/stderr per conversion condition.
- `seedvc_raw/`: raw Seed-VC output wavs before renaming.
- `subjective_eval.html` and `subjective_eval_key.json`: optional blind listening page.
- `<output-dir-name>_report.zip`: portable bundle for local listening.

Seed-VC matrix demos aggregate several Seed-VC pair runs into one listening
bundle. They should contain:

- `matrix_summary.json`: aggregate parameters, per-pair rows, run summary paths,
  and aggregate speaker-similarity stats.
- `matrix_metrics.csv`: compact per-pair metrics for spreadsheet comparison.
- `index.html`: aggregate HTML report linking each pair report and blind eval.
- `runs/<pair-id>/`: one normal Seed-VC pair output directory per pair.
- `logs/`: stdout/stderr logs for each pair run and subjective-eval build.
- `<output-dir-name>_report.zip`: portable aggregate bundle containing the
  matrix files and every pair run artifact.

#### 4. Validation & Error Matrix

- Missing CSV header -> raise `ValueError`.
- Missing required manifest column -> raise `ValueError` naming the column.
- `train-count < 1` -> raise `ValueError`.
- `train-count` greater than row count -> raise `ValueError`.
- `test-index` outside manifest -> raise `ValueError`.
- Test row inside the training slice -> raise `ValueError` unless the script exposes an explicit smoke-test override.
- Zero-norm embedding -> raise `ValueError` before synthesis.

#### 5. Good/Base/Bad Cases

- Good: held-out run where `test-index >= train-count`, summary records no train/test overlap, and all audio/plot paths exist.
- Base: overlap run allowed only for bookkeeping smoke tests via an explicit flag.
- Bad: silently training and evaluating on the same row in a claimed held-out result.

#### 6. Tests Required

At minimum:

- `python -m compileall -q arti6_linearvc_demo`
- `run_timbre_shift_mapper.py --help` for CLI parse visibility.
- `run_speaker_domain_eval.py --help` when the speaker-domain objective script changes.
- `run_seedvc_svc_demo.py --help` when the Seed-VC pivot script changes.
- `run_seedvc_svc_matrix.py --help` when the Seed-VC matrix script changes.
- A summary validation that loads `summary.json`, checks referenced audio and plot files exist, and asserts the feasibility flags expected by the run.
- For Seed-VC matrix runs, load `matrix_summary.json`, check that each `rows[*]`
  report path exists, and check that `matrix_metrics.csv` contains one row per
  requested pair.
- If `--bundle-zip` is used, inspect the zip listing and confirm it contains `index.html`, `summary.json` or `matrix_summary.json`, plots, arrays, and any audio/model-state files that the specific run is expected to emit.

For model-heavy scripts, a full ARTI-6 run is the integration test. Record the exact
command and result path in the active task's `research/` directory.

#### 7. Wrong vs Correct

Wrong:

```python
rows = list(csv.DictReader(open(args.manifest)))
test_pair = rows[args.test_index]
```

This accepts malformed manifests and can silently use an overlapping train/test row.

Correct:

```python
rows = read_manifest(args.manifest)
if args.test_index < args.train_count and not args.allow_train_test_overlap:
    raise ValueError("test-index is inside the training slice")
```

Validation belongs near the CLI boundary so failed demo assumptions are visible
before ARTI-6 model loading starts.

### Scenario: VTuber Dataset Pipeline Scripts

#### 1. Scope / Trigger

Data collection and processing scripts live under `vtuber_pipeline/src/`. Use this pattern for automated pipelines that scrape, separate, or segment audio from external sources (like YouTube).

This spec applies to scripts such as:

- `vtuber_pipeline/src/scrape_vtuber_audio.py`
- `vtuber_pipeline/src/purify_audio.py`

#### 2. Signatures

Use explicit argparse CLIs with mandatory safety flags.

```bash
# Scraper signature
python vtuber_pipeline/src/scrape_vtuber_audio.py \
  --urls "URL1" "URL2" \
  --output-dir data/raw \
  --sleep-requests 20 \
  --domain "Speech"

# Purifier signature
python scripts/data_collection/purify_audio.py \
  --manifest data/raw/manifest.json \
  --output-dir data/purified
```

#### 3. Contracts

**Manifest (JSON) fields:**
- `video_id`: Unique identifier (e.g., YouTube ID).
- `channel_id`: Source channel identifier.
- `domain`: "Speech", "Singing", etc.
- `filename`: Local path to the raw audio file.
- `upload_date`: (Optional) YYYYMMDD.

**Output Structure:**
Processed chunks MUST be organized as:
`{output_dir}/{channel_id}/{domain}/{video_id}_chunkXXX.wav`

**Safety Mechanisms (Mandatory for Scrapers):**
- `--sleep-requests`: Delay between metadata/page requests (minimum 15s recommended).
- `--sleep-interval`: Delay between downloads (minimum 15s recommended).
- No parallel downloads.

#### 4. Validation & Error Matrix

- Missing manifest file -> raise `FileNotFoundError`.
- Missing required column in manifest (`video_id`, `channel_id`, `filename`) -> raise `ValueError` naming the column.
- Demucs/Silero failure -> log `ERROR` and raise `RuntimeError` or continue based on pipeline flag.
- Rate limit detected (HTTP 429) -> log `CRITICAL` and exit or wait.

#### 5. Good/Base/Bad Cases

- Good: Sequential download with pacing, manifest updated incrementally, output organized by domain.
- Bad: Parallel scraping, hardcoded URLs in script, discarding source metadata.

#### 6. Tests Required

- `python -m py_compile vtuber_pipeline/src/*.py`
- `python vtuber_pipeline/src/scrape_vtuber_audio.py --help`
- `python vtuber_pipeline/src/purify_audio.py --help`
- Validate manifest schema after a dry-run or mock extraction.

#### 7. Wrong vs Correct

Wrong:

```python
# Downloading without pacing
for url in urls:
    download(url)
```

Correct:

```python
# Enforcing safety delays
for url in urls:
    download(url)
    time.sleep(args.sleep_requests)
```

### Scenario: VTuber Conservative Curation From Existing WAVs

#### 1. Scope / Trigger

Use this pattern when existing raw WAVs and optional Demucs vocal stems already
exist, and the task is to create training candidates without re-downloading from
YouTube. This is especially important for singing data, where ASR text presence
must not be used as the primary segmentation gate.

#### 2. Signatures

```bash
.venv/bin/python vtuber_pipeline/src/curate_existing_audio.py \
  --input-dir data/raw_audio \
  --vocal-dir data/temp_demucs \
  --vocal-dir data/demucs_tmp \
  --output-dir data/vtuber_curated_conservative \
  --max-source-sec 1200 \
  --skip-existing
```

#### 3. Contracts

Input layout:

- `data/raw_audio/{channel_id}/{domain}/{video_id}.wav`
- Optional vocal stem: `{vocal_dir}/{video_id}_vocals.wav`

The curation script must prefer existing vocal stems when available and fall
back to raw WAV only when a stem is missing. It must not invoke downloaders or
source separation.

Output layout:

- `{output_dir}/clean_candidate/{channel_id}/{domain}/{video_id}_chunkNNNN.wav`
- `{output_dir}/review/{channel_id}/{domain}/{video_id}_chunkNNNN.wav`
- `{output_dir}/quarantine/{channel_id}/{domain}/{video_id}_chunkNNNN.wav`
- `{output_dir}/manifest.jsonl`
- `{output_dir}/summary.json`
- `{output_dir}/sources.json`
- `{output_dir}/skipped_sources.json`

Manifest rows must include:

- `segment_id`
- `channel_id`
- `domain`
- `video_id`
- `status`
- `reason`
- `source_wav`
- `processing_wav`
- `processing_kind`
- `output_wav`
- `start_sec`
- `end_sec`
- `duration_sec`
- `active_ratio`
- `threshold_db`
- `segmentation_strategy`

#### 4. Validation & Error Matrix

- Missing `--input-dir` -> raise `FileNotFoundError`.
- WAV outside `{channel}/{domain}/{video_id}.wav` layout -> log `WARNING` and skip.
- Source longer than `--max-source-sec` when set -> skip and record in `skipped_sources.json`.
- Segment shorter than `--min-segment-sec` -> do not export.
- Existing output with `--skip-existing` -> keep file and still emit manifest row.

#### 5. Good/Base/Bad Cases

- Good: Singing is segmented by vocal activity from an existing vocal stem, with
  phrase-gap merging and padding, and output is tagged `clean_candidate`,
  `review`, or `quarantine`.
- Base: Short speech clips can be `clean_candidate` only when they come from
  short sources; long speech should be `review` until diarization or target
  speaker verification is applied.
- Bad: Filtering singing by Whisper transcript text, discarding humming/ad-libs
  only because they have no recognized linguistic content, or mixing FuwaMoco
  twin audio into a single-speaker clean set.

#### 6. Tests Required

- `.venv/bin/python -m py_compile vtuber_pipeline/src/*.py`
- `.venv/bin/python vtuber_pipeline/src/curate_existing_audio.py --help`
- Run one curation pass and verify:
  - `summary.json` exists and has nonzero `segment_count`.
  - `manifest.jsonl` row count matches generated WAV count.
  - No generated WAV file is zero bytes.
  - Segment durations are within the configured min/max bounds.

#### 7. Wrong vs Correct

Wrong:

```bash
python vtuber_pipeline/src/segment_audio.py --input data/vtuber_clean
```

This uses ASR text as a semantic gate and can remove valid singing material.

Correct:

```bash
.venv/bin/python vtuber_pipeline/src/curate_existing_audio.py \
  --input-dir data/raw_audio \
  --vocal-dir data/temp_demucs \
  --output-dir data/vtuber_curated_conservative
```

This reuses existing vocal stems and segments singing by acoustic vocal activity
instead of transcript availability.
