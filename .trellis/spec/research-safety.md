# Research Safety Constraints

## Scenario: host-aware experiment execution

### 1. Scope / Trigger

- Trigger: before any model execution, dependency install, checkpoint download, or dataset download.
- This repository is used from multiple hosts that share the same `/home` tree. Do **not**
  infer the active machine from copied files, old notes, or repository location alone.

### 2. Signatures

- Host verification commands:
  - `hostname`
  - `nvidia-smi`
  - `python3 --version`
- Project environment commands:
  - `python3 -m venv .venv`
  - `.venv/bin/python -m pip ...`
- Smoke-test entrypoints:
  - `.venv/bin/python arti6_linearvc_demo/run_arti6_smoke.py ...`
  - `.venv/bin/python arti6_linearvc_demo/prepare_cmu_arctic_tiny.py ...`

### 3. Contracts

- `athena`
  - Treat as a non-GPU preparation host unless re-verified otherwise.
  - Suitable for repo organization, planning, and light code edits.
- `valkyrie08`
  - Verified GPU host for this project.
  - Expected GPU surface: `/usr/bin/nvidia-smi`, `/dev/nvidia0`, and PyTorch CUDA visibility.
- Shared storage
  - `~/bowen_lab/...` is shared project storage, not proof of which host is active.
- Python dependencies
  - Install project dependencies inside `.venv`, never into global Python.
  - A copied `.venv` is not trusted until `.venv/bin/python -m pip --version` succeeds.

### 4. Validation & Error Matrix

| Condition | Required response |
| --- | --- |
| `hostname` is not the expected execution host | Stop claiming server readiness; verify the target host explicitly |
| `nvidia-smi` missing on a supposed GPU run | Check host identity before diagnosing GPU failure |
| `.venv/bin/python -m pip --version` fails | Rebuild the venv before installing dependencies |
| Multiple same-prompt wavs share a basename | Use collision-safe output names before batch execution |
| Dataset ids differ from on-disk filenames | Verify one real file path before generating a larger manifest |

### 5. Good / Base / Bad Cases

- Good: SSH to `valkyrie08`, verify GPU, rebuild `.venv`, run Gate A and Gate B smoke tests.
- Base: edit code from a shared home directory, but defer GPU claims until the active host is checked.
- Bad: inspect `athena`, conclude `valkyrie08` lacks GPU tooling, then escalate to administrators.

### 6. Tests Required

- Before claiming GPU readiness:
  - assert `torch.cuda.is_available()` is `True`
  - record `torch.cuda.get_device_name(0)`
- Before trusting project isolation:
  - install one package in a temporary venv
  - verify it is absent from global Python
- Before larger experiments:
  - run one built-in sample through ARTI-6
  - run one real dataset pair through the same wrapper

### 7. Wrong vs Correct

#### Wrong

```bash
hostname           # athena
python3 -m venv .venv
# venv fails here, therefore "the GPU server is unusable"
```

#### Correct

```bash
ssh valkyrie08
hostname
nvidia-smi
python3 -m venv .venv
.venv/bin/python -m pip --version
```

## Operational Rules

1. Do not use `sudo` for project setup unless the user explicitly changes the operating model.
2. Prefer the smallest experiment that proves the next unknown.
3. Large downloads are allowed only when they directly serve an approved validation step.
4. Archive stale context files instead of letting them mislead later agents.
