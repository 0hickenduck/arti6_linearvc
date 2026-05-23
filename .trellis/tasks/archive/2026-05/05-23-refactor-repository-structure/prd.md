# Refactor Repository Structure for VTuber Pipeline

## Goal

Restructure the repository to cleanly separate the legacy `arti6_linearvc` demo project from the newly introduced VTuber cross-domain dataset pipeline. Currently, both projects and their respective test files/scripts are mixed at the repository root, creating a confusing structure.

## What I already know

* The VTuber extraction pipeline (task from the 23rd) was completed by an agent and committed/archived. It introduced `scripts/data_collection/` and some uncommitted test files like `scripts/run_vtuber_demo.py`, `test_silero.py`, `cookies_netscape.txt`.
* The `arti6_linearvc_demo/` directory contains existing demo scripts (e.g. `run_linearvc_floor.py`, `build_linearvc_report.py`).
* There is an `external/` directory containing models (`arti-6`, `seed-vc`).
* The root directory has a mix of scripts for both projects.
* The user attempted to rewind the last task but failed, leaving some uncommitted files.

## Assumptions (temporary)

* The `arti6_linearvc_demo` and VTuber pipeline are conceptually separate projects that just happen to share the same repository right now.
* We want to create two distinct top-level directories (or similar logical separation) so scripts from one don't pollute the other.
* Uncommitted files related to the VTuber pipeline (like `test_silero.py` and `run_vtuber_demo.py`) should be preserved but moved to the right place.

## Open Questions

* All open questions resolved.

## Requirements

* Identify all root-level and `scripts/`-level files and categorize them into either the `arti6` project or the `vtuber` project.
* Create a new `vtuber_pipeline/` directory at the root.
* Move all VTuber pipeline files (e.g. `scripts/data_collection/`, `test_silero.py`, `cookies_netscape.txt`, `run_vtuber_demo.py`, `convert_cookies.py`) into `vtuber_pipeline/`.
* Leave `arti6_linearvc_demo/` as is, but ensure no VTuber scripts are mixed in it.
* Keep shared folders like `external/`, `data/`, `outputs/` at the root.
* Update import paths (e.g., `sys.path` or relative imports) in the moved Python scripts so they continue to work from their new locations.
* Revert the uncommitted change to `.trellis/spec/backend/directory-structure.md` since it was a mistaken rewind attempt, or update it to reflect the new structure.

## Decision (ADR-lite)

**Context**: The repository contains two distinct projects (a legacy arti6 demo and a new VTuber data pipeline) mixed at the root and in the `scripts/` directory. We needed a clean way to separate them.
**Decision**: We will use a "Two root folders" structure. We keep `arti6_linearvc_demo/` as is, create a new `vtuber_pipeline/` folder at the root for the new project, and leave shared data/model directories (`external/`, `data/`, `outputs/`) at the root.
**Consequences**: This maintains a flat, accessible root while clearly scoping domain-specific code. Scripts that depend on the `external/` or `data/` directories might need path adjustments.

## Acceptance Criteria

* [ ] `vtuber_pipeline/` is created.
* [ ] VTuber scripts (`data_collection`, demo scripts) are moved to `vtuber_pipeline/`.
* [ ] Root is clean of VTuber-specific test files (`test_silero.py`, `cookies_netscape.txt`, etc. are moved).
* [ ] The moved scripts can still correctly import local modules and resolve paths to `external/`, `data/`, and `outputs/`.

## Definition of Done

* No data loss for uncommitted files.
* Python scripts compile and run without ModuleNotFoundError.

## Out of Scope

* We are not rewriting the internal logic of the scripts, only restructuring their locations.
* We are not modifying the internal workings of the `arti6_linearvc_demo/` code.

## Technical Approach

We will execute the following file movements:
1. `mkdir vtuber_pipeline`
2. `mv scripts/data_collection vtuber_pipeline/src` (or similar)
3. `mv scripts/run_vtuber_demo.py vtuber_pipeline/`
4. `mv scripts/convert_cookies.py vtuber_pipeline/`
5. `mv test_silero.py vtuber_pipeline/`
6. `mv cookies_netscape.txt vtuber_pipeline/`
7. Check `scripts/valkyrie-status.sh`. If it's general, leave it in a `tools/` or `scripts/` dir, or move it to `.trellis/`.
8. Check and update the `sys.path` appending logic in `run_vtuber_demo.py`, `batch_process.py`, etc., to point to the correct `external/` path.

## Technical Notes

* `scripts/data_collection/` is the core of the new VTuber pipeline.
* Uncommitted files: `cookies_netscape.txt`, `dummy.wav`, `scripts/convert_cookies.py`, `scripts/run_vtuber_demo.py`, `test_silero.py`.
* `.trellis/spec/backend/directory-structure.md` was modified (a reversion was left uncommitted by the user's rewind attempt).
