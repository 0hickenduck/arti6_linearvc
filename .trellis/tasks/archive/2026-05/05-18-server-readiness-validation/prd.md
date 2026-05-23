# server-readiness-validation

## Goal

Validate whether the new lab-server setup is genuinely ready for research work, not merely installed: confirm harness/tooling completeness, environment isolation, GPU usability, file/workflow conventions, and then prove the stack with a real acoustic project smoke test from clone through tiny benchmark execution.

## What I already know

* The user wants an actual acceptance test of the server, not a critique of another agent's report.
* Validation should cover harness engineering, virtual environments / dependency isolation, GPU availability, and whether real project workflows run cleanly.
* A convincing proof should use a real acoustic project: fetch code, set up dependencies in an isolated environment, run a minimal example, then run a tiny slice of its benchmark/data path.
* Current repository already contains ARTI-6 materials and a provisional research harness, but those alone do not prove the broader server workflow.

## Assumptions (temporary)

* The acoustic project is an external repo the user already has in mind, but its exact identity is not yet derivable from the current repo.
* We should prefer a tiny, bounded benchmark slice over a full expensive run.
* The test should avoid polluting global Python or shared system state.

## Open Questions

* No remaining blocking question: user clarified the acoustic demo is the ARTI-6 repo already present under `external/arti-6/`.

## Requirements (evolving)

* Verify harness/tooling structure and basic engineering readiness.
* Verify whether project-local isolated environments can be created and used.
* Verify whether dependencies can be installed without contaminating other projects.
* Verify whether GPU access is available from shell and Python.
* Use ARTI-6 under `external/arti-6/` as the end-to-end acceptance test.
* Run the smallest meaningful example and the smallest meaningful benchmark/data slice.
* Use a two-gate smoke design: Gate A = built-in ARTI-6 example wav for model-chain validation; Gate B = a 1-pair same-prompt CMU ARCTIC slice (`bdl`→`slt`) for dataset-chain validation.
* Produce a concrete readiness verdict with blockers, if any.
* Clarify the long-term storage model: what belongs in shared home/project storage versus what is host-specific on `valkyrie08`.
* Clean the repository root by archiving already-finished, out-of-scope material so the active project shape is legible.

## Acceptance Criteria (evolving)

* [x] We can state whether harness engineering is ready, partially ready, or not ready, with evidence.
* [x] We can state whether isolated project environments work on the server.
* [x] We can state whether GPU is usable from both system and Python perspectives.
* [x] One external acoustic project is identified: `external/arti-6/`.
* [x] Its dependencies are installed in an isolated environment.
* [x] Gate A runs: built-in example wav completes inversion+synthesis on GPU.
* [x] Gate B runs: one aligned CMU ARCTIC source/target pair is prepared from dataset code and both dataset wavs complete ARTI-6 processing.
* [x] Final report distinguishes server issues from project-specific issues.

## Definition of Done (team quality bar)

* Evidence is command-backed, not inferred from memory.
* Any created environments or downloads are kept scoped and documented.
* The benchmark run is intentionally small and reproducible.
* Findings are recorded clearly enough that future projects can reuse the path.

## Out of Scope (explicit)

* Full-scale benchmark reproduction.
* Large model or dataset downloads unless needed and explicitly justified.
* General server administration beyond what is required to establish readiness.

## Technical Notes

* User clarified the intended acoustic demo is ARTI-6 itself, already vendored under `external/arti-6/`.
* Root currently also contains finished report artifacts (`reports/`, `reports_context/`) that are unrelated to the ARTI-6 + LinearVC research demo and are candidates for archival.
* Initial Codex shell was on `athena`, but the actual target GPU host `valkyrie08` is reachable by SSH and differs materially from `athena`.
* On `valkyrie08`: `/usr/bin/nvidia-smi` exists; `/dev/nvidia0` exists; GPU is `NVIDIA RTX 6000 Ada Generation`; memory is 62 GiB RAM + 127 GiB swap.
* On `valkyrie08`: system Python 3.9.2 has `venv`, `ensurepip`, `distutils.cmd`, and `/usr/bin/pip3`; temporary venv creation works.
* Isolation probe succeeded: package installed inside a temporary venv was importable there and absent from global Python afterward.
* Trellis/Codex/Gemini adapters are present in the repo; remote CLI binaries resolve on `valkyrie08`.
* `archive/provisional_research_harness/` is only a legacy archived YAML config; the live harness is the Trellis + adapter structure, not that archived folder.
* Rebuilt the project `.venv` on `valkyrie08`; the previously copied `.venv` was malformed and lacked `pip`.
* Gate A result: example wav processed on CUDA with feature shape `(1, 275, 6)` and speaker embedding shape `(1, 192)`.
* Gate B result: prepared one aligned CMU ARCTIC pair (`a0001`, `bdl`/`slt`) and processed both wavs on CUDA with output summaries under `outputs/smoke/`.
* Smoke testing found and fixed two wrapper issues before larger experiments: relative-path duplication after `chdir`, and output filename collision for same-prompt paired wavs.

## Experiment Design Chosen

1. Gate A — repository smoke: run ARTI-6 on `external/arti-6/example_gt.wav`, capture GPU/device info, `(B,T,6)` feature shape, speaker embedding shape, and reconstructed wav.
2. Gate B — dataset smoke: use CMU ARCTIC because the later LinearVC idea needs paired same-prompt speakers; prepare the minimum aligned `bdl`/`slt` manifest with one pair, then run ARTI-6 over the tiny slice.
3. Only after both gates pass do we move on to implementing the actual LinearVC experiment.
