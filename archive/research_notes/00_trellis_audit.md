# Trellis Audit

Status: PARTIAL GO

Scope: local audit of cloned Trellis source at `external/trellis/`. No ARTI-6 implementation was started. No model checkpoints or datasets were downloaded.

## What Is Trellis?

Trellis is an AI coding-agent harness/project layer. Its README describes it as "The harness that makes coding agents production-ready" and lists core features: auto-injected specs, task-centered workflow, project memory, team-shared standards, and multi-platform setup. In source, it is implemented as an npm CLI package plus repo-local `.trellis/` Python scripts, generated agent skills/hooks, task files, spec files, and workspace journals.

## Installation Method

README says to install with:

```bash
npm install -g @mindfoldhq/trellis@latest
trellis init -u your-name
trellis init --cursor --opencode --codex -u your-name
```

Local source evidence:
- `external/trellis/README.md:49-65`
- `external/trellis/packages/cli/package.json:1-11`
- `external/trellis/packages/cli/src/cli/index.ts:61-99`

This workspace did not install Trellis dependencies. The cloned CLI source was inspected only.

## Runtime Requirements

Verified from local files:
- Node.js >= 18 from README.
- Python >= 3.9 from README.
- npm package engine says Node >= 18.17.0.
- Local shell has `python3` as Python 3.14.5, but `python` is not on PATH.

Evidence:
- `external/trellis/README.md:49-52`
- `external/trellis/packages/cli/package.json:75-77`
- command output: `python --version` failed with `zsh:1: command not found: python`
- command output: `python3 --version` returned `Python 3.14.5`

## Capability Table

| Capability | Trellis support | Evidence | Gap / action needed |
|---|---|---|---|
| What is Trellis? | YES | README lists harness features and four-phase loop in `README.md:42-85`. | Use as workflow harness, not as ARTI-6 implementation. |
| Installation method | YES | README install/init commands in `README.md:54-65`; CLI package/bin in `packages/cli/package.json:1-11`; init flags in `packages/cli/src/cli/index.ts:61-99`. | Do not install yet; later install in venv/conda-compatible local setup or use npm only after approval. |
| Runtime requirements | YES | README says Node.js >= 18 and Python >= 3.9 in `README.md:49-52`; package engine says Node >= 18.17.0 in `packages/cli/package.json:75-77`. | `python` is missing locally; use `python3` or configure `TRELLIS_PYTHON_CMD` if installing. |
| Shell execution | PARTIAL | Task lifecycle hooks are shell commands in `.trellis/config.yaml:21-33`; hook runner uses `subprocess.run(..., shell=True)` in `.trellis/scripts/common/task_utils.py:218-249`. | Trellis can run configured lifecycle hooks, but normal research commands still run through the host agent shell. Add local safety policy for large downloads/GPU/lab paths. |
| File editing | PARTIAL | CLI writes generated files through `writeFile` in `packages/cli/src/utils/file-writer.ts:104-180`; Codex configurator writes `.agents`, `.codex`, hooks, config in `packages/cli/src/configurators/codex.ts:22-138`. | Trellis scaffolds/updates files. Actual code edits are done by the AI coding host. Need ARTI-6-specific specs before implementation. |
| Logs | YES | Workspace journals are documented in `.trellis/workflow.md:78-87`; README calls project memory/journals in `README.md:45`. | Good enough for session notes; add experiment log conventions later under local specs. |
| State tracking | YES | Task directories contain `prd.md`, `implement.jsonl`, `check.jsonl`, `task.json` in `.trellis/workflow.md:40-76`; active-task state uses `.trellis/.runtime/sessions/` in `.trellis/scripts/common/active_task.py:1-7`. | Map this to `PROJECT_STATE.json` or decide whether Trellis task state replaces it after audit. |
| Task queues or staged prompts | PARTIAL | Workflow phases and required steps in `.trellis/workflow.md:142-220`; task queue helpers list by status/assignee in `.trellis/scripts/common/task_queue.py:1-160`. | It supports task tracking and staged workflow, not a full autonomous job queue. Add research queue conventions if needed. |
| Human approval before risky actions | PARTIAL | File conflict prompts in `writeFile` ask/skip/overwrite/append in `packages/cli/src/utils/file-writer.ts:104-180`; Codex hooks require `/hooks` approval per `packages/cli/src/configurators/codex.ts:113-129`. | No verified general approval gate for arbitrary risky shell actions/downloads. Keep AGENTS.md policy and add explicit Trellis spec/gate. |
| Gates/checkpoints | YES | README says workflow gates in `README.md:99-103`; workflow requires phase steps and dirty-tree finish gate in `.trellis/workflow.md:197-235`; `trellis-check` skill requires lint/type/test checks in `.agents/skills/trellis-check/SKILL.md`. | Gates are mostly procedural, not hard enforcement. Add research-specific gates: no large downloads, no checkpoints, no lab assumptions. |
| Safe local disposable workspace | YES | Trellis stores project-local `.trellis/`, `.agents/`, `.codex/` files and task/workspace files; task path safety rejects absolute/traversal paths in `.trellis/scripts/common/task_utils.py:27-69`. | Safe if initialized only inside current repo. Need decide whether to keep `external/trellis/` tracked or ignore external clones. |
| Later lab server use | LIKELY | Trellis is repo-local and platform-aware; README multi-platform setup in `README.md:47`; config supports monorepo/polyrepo paths in `.trellis/config.yaml:39-59`. | UNKNOWN until lab server OS, Node, Python, Codex/agent setup, and filesystem paths are verified on-server. |
| Define project/task | YES | `task.py create/start/current/finish/archive/list` documented in `.trellis/workflow.md:40-74`; `task.py --help` executed successfully and listed those commands. | Need initialize developer identity before creating real tasks. Do not create ARTI-6 task yet in this phase. |
| ARTI-6 + LinearVC usage | PARTIAL | Trellis provides PRD, task JSON, spec, research, implementation/check JSONL, and journals. Evidence: `.trellis/workflow.md:40-95` and `README.md:82-85`. | Add project-specific Trellis specs for research safety, environment capture, dataset/checkpoint policies, lab handoff, and ARTI-6/LinearVC acceptance criteria later. |
| Missing pieces we need to add | YES | Gaps above plus no ARTI-specific specs found in cloned Trellis; this workspace is intentionally not specialized yet. | Add local Trellis setup only after this audit is accepted: init Trellis, add research engineering specs, define safe task templates, and keep downloads/cache policy explicit. |

## How To Define A Project/Task In Trellis

Based on local workflow docs, the normal sequence is:

1. Install Trellis and initialize in repo with relevant platforms.
2. Initialize developer identity:
   ```bash
   python3 ./.trellis/scripts/init_developer.py <your-name>
   ```
3. Create a task:
   ```bash
   python3 ./.trellis/scripts/task.py create "<title>" [--slug <name>] [--parent <dir>]
   ```
4. Write/iterate `prd.md`.
5. Curate `implement.jsonl` and `check.jsonl` for sub-agent-capable platforms, unless using Codex inline mode.
6. Start task:
   ```bash
   python3 ./.trellis/scripts/task.py start <task-dir>
   ```
7. Implement/check/update spec/commit/finish according to workflow phases.

Evidence:
- `external/trellis/.trellis/workflow.md:17-95`
- `external/trellis/.trellis/workflow.md:152-220`
- command output from `python3 ./.trellis/scripts/task.py --help`

## How Trellis Should Be Used For ARTI-6 + LinearVC

Recommended use:

1. Use Trellis as the primary workflow harness.
2. Keep the initial local setup disposable and lab-independent.
3. Add local Trellis specs before ARTI-6 implementation:
   - environment capture and reproducibility rules
   - no-GPU/no-lab-server assumptions unless verified
   - no large downloads/checkpoints without explicit approval
   - dataset/model cache locations
   - failure reporting format
   - LinearVC and ARTI-6 task acceptance criteria
4. Use Trellis tasks for each bounded research step:
   - environment inventory
   - dependency review
   - paper/source audit
   - minimal smoke test planning
   - lab-server migration checklist
5. Keep experiment outputs in configured ignored directories only: `data/`, `models/`, `cache/`, `outputs/`, `logs/`.

## What Is Missing That We Need To Add Ourselves

- A local Trellis initialization for this workspace.
- ARTI-6 + LinearVC project specs.
- Research-specific safety gates for datasets, checkpoints, GPU/CUDA, lab paths, and external services.
- A lab-server handoff checklist.
- A clear policy for whether `external/trellis/` is tracked, ignored, or replaced by installed Trellis templates.
- Verification of npm install/init in this workspace.
- Verification on the actual lab server.

## Recommendation

Recommendation: extend Trellis.

Trellis is sufficient as the primary harness framework for structured research engineering preparation: it provides task PRDs, staged workflow, specs, journals, hooks, and state tracking. It is not sufficient by itself for our research safety constraints; add local Trellis specs/gates before implementing ARTI-6 or running LinearVC-related code.

Final status: PARTIAL GO
