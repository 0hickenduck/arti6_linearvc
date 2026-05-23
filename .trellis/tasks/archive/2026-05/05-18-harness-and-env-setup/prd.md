# harness-and-env-setup

## Goal

Set up the execution environment on the GPU server (RTX 6000 Ada), verify the research harness, and ensure all necessary CLI tools (Codex) and Python dependencies are configured correctly for the `arti6` project.

## What I already know

* **Server:** GPU server (Valkyrie08) with NVIDIA RTX 6000 Ada.
* **Working Directory:** `~/bowen_lab/projects/arti6_linearvc/`.
* **OS:** Debian 11 (Bullseye), Python 3.9.2.
* **CUDA:** System-wide `nvidia-smi` is missing from PATH, and GPU access is unverified.
* **Storage:** Home directory is 99% full (1.6T available out of 96T).
* **Memory:** 7.6GiB RAM, mostly used or cached.

## Requirements (evolving)

1. [x] Verify directory structure and harness presence.
2. [x] Remap absolute paths in configs to local server paths. (Checked: none found in YAML)
3. [!] Create a Python venv in `.venv`. (FAILED: System lacks `python3-venv` and `distutils.cmd`)
4. [!] Install dependencies (torch, torchaudio, etc.) for CUDA 12.x. (FAILED: OOM or Pip-less environment)
5. [ ] Verify GPU access via a Python script. (Blocked)
6. [x] Install/Verify `@mindfoldhq/codex-cli`. (Verified: `codex-cli 0.130.0` at `/home/bowen/.nvm/versions/node/v20.20.2/bin/codex`)

## Technical Notes

* Task Directory: `.trellis/tasks/05-18-harness-and-env-setup`
* **Critical Blockers**:
    * The server environment is missing standard Python development packages (`python3-venv`, `python3-pip`).
    * Attempts to bootstrap `pip` manually failed due to missing `distutils` submodules in the base Python 3.9 image.
    * Attempts to install `torch` (768MB+) were killed (likely OOM on 7.6GB system with heavy disk cache/swap activity).
* **Codex**: Successfully installed using a local npm prefix.

## Recommendation

The server requires administrative intervention to install `python3-venv` or `conda` to provide a stable development environment. Running ARTI-6 (PyTorch) is not feasible in the current restricted shell environment.
