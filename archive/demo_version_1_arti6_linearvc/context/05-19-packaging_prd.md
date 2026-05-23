# Package LinearVC demo results

## Goal

Turn the completed tiny ARTI-6 + LinearVC floor experiment into a reproducible local demo package: a user should be able to run the existing tiny experiment, generate a readable results page, listen to the six audio conditions, inspect plots, and understand the current evidence without reading raw JSON first.

## What I already know

* The tiny floor experiment has already run successfully under `outputs/linearvc_floor/tiny_5train_1test/`.
* Existing experiment entrypoints live under `arti6_linearvc_demo/`.
* `run_linearvc_floor.py` already writes `summary.json`, arrays, plots, and six audio conditions.
* The held-out `a0006` aligned-frame metrics are already recorded: source identity MSE `0.23069`, mean/std `0.22125`, diagonal affine `0.16811`, full affine `0.15701`.
* The demo must not overclaim scientific success; this is a tiny floor with crude truncation alignment.
* Gemini delegation can run and inspect the repo, but the local Gemini CLI reports a corrupted credentials file at `/home/bowen/.gemini/gemini-credentials.json`.

## Assumptions (temporary)

* A static HTML report generated from `summary.json` is the smallest useful demo packaging step.
* The report should live beside an experiment output directory so relative audio/image paths resolve locally without a server.
* The README should document how to regenerate the report after rerunning the experiment.
* No new model run is required for this task unless validation reveals stale or missing outputs.

## Open Questions

* None blocking for the MVP. Default choice: generate a local static report beside the output directory.

## Requirements (evolving)

* Add a small report-generation command under `arti6_linearvc_demo/`.
* Read an existing `summary.json` and validate that referenced audio and plot files exist.
* Generate a static `index.html` with:
  * experiment metadata and reproducibility details
  * aligned test metrics table
  * audio players for all generated conditions
  * embedded plot references for trajectories, mean/std comparison, and full affine heatmap
  * an explicit limitations/status note
* Extend the floor audio condition matrix so the demo can separate pure articulatory transformation from target speaker embedding injection:
  * pure controls using source speaker embedding
  * oracle controls using target articulation with source/average embedding
  * average speaker embedding controls
  * hybrid controls using target speaker embedding
* Update `arti6_linearvc_demo/README.md` with the report generation command and demo viewing path.
* Keep the generated page honest: no invented benchmarks, no claim beyond the tiny floor.
* Use Gemini only for narrow, low-risk drafting or file inventory; Codex remains responsible for final logic and code review.

## Acceptance Criteria (evolving)

* [ ] `summary.json` can be converted into a local `index.html`.
* [ ] The generated page links to existing audio and plots using relative paths.
* [ ] Missing referenced files cause a clear failure unless explicitly allowed.
* [ ] README documents the command needed to rebuild the page.
* [ ] The generator can run with the project `.venv` Python.
* [ ] The generated page exists for `outputs/linearvc_floor/tiny_5train_1test/`.
* [ ] The floor run writes pure, oracle, average-embedding, and hybrid audio conditions.

## Definition of Done (team quality bar)

* Tests added/updated when appropriate for the generator logic.
* Lint / syntax checks pass for changed Python files.
* Docs updated for the new command.
* Demo output is reproducible from existing artifacts.

## Out of Scope (explicit)

* Scaling the experiment beyond the existing tiny split.
* Adding perceptual evaluation, MOS, or claims about real conversion quality.
* Changing ARTI-6 model internals.
* Reworking the broader Trellis/Gemini harness in this task.

## Technical Notes

* Relevant files inspected:
  * `arti6_linearvc_demo/README.md`
  * `arti6_linearvc_demo/run_linearvc_floor.py`
  * `outputs/linearvc_floor/tiny_5train_1test/summary.json`
  * `.trellis/tasks/05-18-tiny-linearvc-floor-experiment/prd.md`
  * `.trellis/tasks/05-18-server-readiness-validation/prd.md`
  * `scripts/valkyrie-status.sh`
* Existing output layout:
  * `audio/*.wav`
  * `plots/*.png`
  * `arrays/*.npy`
  * `summary.json`
* Gemini delegation test result: usable for basic scanning, but credentials warning should be treated as a readiness issue rather than ignored.
