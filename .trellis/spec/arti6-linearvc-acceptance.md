# ARTI-6 + LinearVC Acceptance Contract

## Scenario: first floor experiment

### 1. Scope / Trigger

- Trigger: before scaling beyond smoke tests or claiming that the LinearVC idea is runnable.
- The first floor must test **6D articulatory feature transforms**, not generic acoustic-feature transforms.

### 2. Signatures

- Prepare manifest:
  - `.venv/bin/python arti6_linearvc_demo/prepare_cmu_arctic_tiny.py --root <dir> --source-speaker bdl --target-speaker slt --num-pairs <N> --manifest <csv>`
- Run floor:
  - `.venv/bin/python arti6_linearvc_demo/run_linearvc_floor.py --manifest <csv> --output-dir <dir> --train-count <N> --test-index <I>`
- Optional regularized/swept floor:
  - `.venv/bin/python arti6_linearvc_demo/run_linearvc_floor.py --manifest <csv> --output-dir <dir> --train-count <N> --test-index <I> --ridge-lambda <L> --alpha <A>`
  - `--ridge-lambda` and `--alpha` may be repeated.

### 3. Contracts

- Input manifest fields:
  - `utterance_id`
  - `source_speaker`
  - `source_wav`
  - `target_speaker`
  - `target_wav`
- Core representation:
  - articulatory features must be shaped `(T, 6)` with dimensions `[LA, TT, TB, VL, TR, LX]`
  - speaker embeddings must be shaped `(1, 192)`
- Required audio outputs:
  - source reconstruction
  - target reconstruction
  - embedding-only VC
  - oracle target articulation + source speaker embedding
  - source articulation + average speaker embedding
  - target articulation + average speaker embedding
  - pure mean/std transform + source speaker embedding
  - pure diagonal affine transform + source speaker embedding
  - pure full affine transform + source speaker embedding
  - average mean/std transform + average speaker embedding
  - average diagonal affine transform + average speaker embedding
  - average full affine transform + average speaker embedding
  - hybrid mean/std transform + target speaker embedding
  - hybrid diagonal affine transform + target speaker embedding
  - hybrid full affine transform + target speaker embedding
- Pure LinearVC means transformed articulation with the source speaker embedding; hybrid means transformed articulation with the target speaker embedding.
- Ridge full affine maps use a full affine transform with L2 regularization on weights and no penalty on the bias.
- Alpha residual variants use `source + alpha * (transformed - source)` and are pure conditions with the source speaker embedding.

### 4. Validation & Error Matrix

| Condition | Required response |
| --- | --- |
| Source / target durations differ | Truncate each paired training utterance to shared minimum length for the first floor |
| Same-prompt wavs share a basename | Prefix output filenames so paired outputs cannot overwrite each other |
| Any tensor contains NaN / Inf | Stop and inspect before scaling the experiment |
| Held-out transformed MSE does not beat source identity | Do not claim the transform helps yet; inspect alignment and map design |
| Pure LinearVC sounds unchanged from source | Treat as evidence that the current ARTI-6 decoder relies on speaker embedding for voice identity |
| Oracle target articulation + source speaker still sounds like source | Treat as evidence that speaker embedding dominates over 6D articulation for timbre |
| Ridge/alpha improves trajectory MSE but audio remains unintelligible | Treat the metric as insufficient for voice-conversion quality; prioritize listening/ASR/speaker-sim diagnostics |

### 5. Good / Base / Bad Cases

- Good: `5 train / 1 test` runs, writes pure, oracle, average, and hybrid audio conditions, plots, arrays, and summary metrics.
- Scaling: `20 train / 1 test` runs with ridge lambdas and alpha residuals, then writes all additional condition audio paths into `summary.json`.
- Base: `1 pair` sanity run uses the same utterance for train and test only to debug the pipeline.
- Bad: scale to many utterances before one-pair outputs, plots, and overwrite behavior are verified.

### 6. Tests Required

- Smoke:
  - one-pair run must complete end-to-end
- Tiny floor:
  - five training pairs + one held-out pair must complete end-to-end
- Scaling probe:
  - twenty training pairs + one held-out pair should run before drawing conclusions from the five-pair floor
  - ridge and alpha settings must be recorded in `summary.json`
- Assertions:
  - CUDA visibility recorded
  - output wav files exist
  - summary JSON contains tensor ranges and aligned test metrics
  - transformed outputs preserve finite numeric ranges

### 7. Wrong vs Correct

#### Wrong

```text
Fit a large model first, then inspect whether manifests, plots, and files were correct.
```

#### Correct

```text
1 pair sanity -> 5 train / 1 test floor -> inspect metrics and plots -> only then scale.
```

## Scenario: local static report packaging

### 1. Scope / Trigger

- Trigger: after a floor experiment writes `summary.json`, audio outputs, and plots.
- Purpose: package existing artifacts for local listening and inspection without rerunning ARTI-6 or starting a web server.

### 2. Signatures

- Build report:
  - `.venv/bin/python arti6_linearvc_demo/build_linearvc_report.py --summary <output-dir>/summary.json`
- Optional output override:
  - `.venv/bin/python arti6_linearvc_demo/build_linearvc_report.py --summary <output-dir>/summary.json --output <path>/index.html`
- Optional missing-file tolerance:
  - `.venv/bin/python arti6_linearvc_demo/build_linearvc_report.py --summary <output-dir>/summary.json --allow-missing`
- Optional portable bundle:
  - `.venv/bin/python arti6_linearvc_demo/build_linearvc_report.py --summary <output-dir>/summary.json --bundle-zip`

### 3. Contracts

- Input `summary.json` must contain:
  - `aligned_test_metrics`: object keyed by condition name with `mse`, `mae`, and `aligned_frames`
  - `audio_outputs`: object mapping condition names to wav paths
  - `plots`: object mapping plot names to image paths
  - experiment metadata such as `train_utterance_ids`, `test_utterance_id`, `train_frames`, and `alignment_policy`
- Report output:
  - default path is `index.html` beside the input `summary.json`
  - links to audio, plots, and summary must be relative to the generated HTML file
  - generated HTML must include an explicit limitation/status note for the tiny floor
- Portable bundle output:
  - default path is `<output-dir>/<output-dir-name>_report.zip`
  - archive root must contain `index.html`, `summary.json`, `audio/*.wav`, and `plots/*.png`
  - extracted `index.html` must work locally without access to the server filesystem

### 4. Validation & Error Matrix

| Condition | Required response |
| --- | --- |
| `summary.json` is not a JSON object | Fail with a clear error |
| `audio_outputs` or `plots` is missing/not an object | Fail with a clear error |
| Referenced audio or plot path is missing | Fail by default |
| Missing referenced path with `--allow-missing` | Render report and include missing-artifact warning |
| `--output` points outside the experiment directory | Still render links relative to that HTML location |
| `--bundle-zip` is used with artifacts outside the HTML directory | Fail with a clear error; use the default output location for portable bundles |

### 5. Good / Base / Bad Cases

- Good: `tiny_5train_1test/summary.json` generates an `index.html` with metrics, six audio players, three plots, and a limitations note.
- Base: a custom `--output` path still links back to the real `summary.json` and artifact files.
- Portable: `--bundle-zip` creates a zip that can be downloaded, unzipped locally, and opened through `index.html`.
- Bad: copy absolute artifact paths into HTML in a way that breaks when the report is moved with its output directory.

### 6. Tests Required

- Syntax/import:
  - `py_compile` or equivalent syntax check for the generator script
- Integration:
  - run the generator against `outputs/linearvc_floor/tiny_5train_1test/summary.json`
  - assert `index.html` exists
  - assert expected relative links exist for `summary.json`, `audio/*.wav`, and `plots/*.png`
  - assert `--bundle-zip` includes `index.html`, `summary.json`, all six wav files, and all plot files
- Validation:
  - missing referenced files fail unless `--allow-missing` is passed

### 7. Wrong vs Correct

#### Wrong

```text
Manually edit a static HTML page with copied absolute paths and unchecked claims.
```

#### Correct

```text
Generate index.html from summary.json, validate artifact paths, use relative links, optionally create a portable zip bundle, and state the tiny-floor limitation explicitly.
```
