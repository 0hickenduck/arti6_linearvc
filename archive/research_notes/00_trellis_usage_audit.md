# Trellis Usage Audit

Status: GO

Scope: local audit of whether Trellis actually orchestrated previous work in this workspace. No ARTI-6 code was run. No models, checkpoints, or datasets were downloaded.

## Conclusion

Trellis was only cloned and audited. It was not actually used to orchestrate the previous ARTI-6 and dataset audit work.

The existing work followed a lightweight file-based workflow: root safety files, `PROJECT_STATE.json`, markdown research notes, and a provisional YAML task spec under `research_harness/`. The workspace does not show a root `.trellis/` initialization, active Trellis task, Trellis PRD, Trellis workspace journal, or Trellis-generated task state.

Trellis usage status: `CLONED_ONLY`

## Evidence

| Evidence item | Observation | Conclusion |
|---|---|---|
| `pwd` | Current workspace is `/Users/bowen/research/arti6_linearvc_work`. | Audit was performed in the intended local workspace. |
| `git status` | Root repo has untracked `.gitignore`, `AGENTS.md`, `LOCAL_CONTEXT.md`, `PROJECT_STATE.json`, `external/`, `research_harness/`, and `research_notes/`. | No committed Trellis project state exists yet. |
| `find external/trellis -maxdepth 2 -type f \| head -80` | Trellis source exists under `external/trellis/`, including `README.md`, `.trellis/config.yaml`, `.trellis/workflow.md`, `.codex/config.toml`, and `.codex/hooks.json`. | Trellis was cloned locally for inspection. |
| `find . -maxdepth 3 -type f \| sort \| head -120` | Root files include research notes and `research_harness/configs/task_arti6_linearvc.yaml`; there is no root `.trellis/` file in the listing. | The current project root has not been initialized as a Trellis workspace. |
| `PROJECT_STATE.json` | `primary_harness` is `Trellis`, but `known_unknowns` says `Trellis npm install/init has not been run in this workspace.` | Project intent names Trellis, but actual Trellis initialization was not performed. |
| `research_notes/00_trellis_audit.md` | Previous audit says Trellis is sufficient as a harness but lists missing local Trellis initialization and ARTI-6 project specs. | Prior work audited Trellis, but did not migrate the project into Trellis. |
| `research_harness/configs/task_arti6_linearvc.yaml` | Contains gate definitions for ARTI-6 LinearVC in a custom YAML structure. | This is not Trellis-native task state. |
| Trellis README | README says Trellis uses `.trellis/spec/`, `.trellis/tasks/`, and `.trellis/workspace/`. | These expected root structures are absent from the current project. |
| Trellis workflow doc | `.trellis/workflow.md` says tasks live under `.trellis/tasks/{MM-DD-name}/` and developer journals under `.trellis/workspace/<developer>/`. | No such root task or workspace journal exists here. |

## Trellis Entry Points

Verified from `external/trellis/README.md`, `external/trellis/.trellis/workflow.md`, and lightweight command output:

| Entry point | Evidence | Notes |
|---|---|---|
| npm CLI install | README lists `npm install -g @mindfoldhq/trellis@latest`. | Not run in this workspace. |
| repo initialization | README lists `trellis init -u your-name` and `trellis init --cursor --opencode --codex -u your-name`. | Not run in this workspace. |
| developer identity | Workflow doc lists `python3 ./.trellis/scripts/init_developer.py <your-name>`. | Would create `.trellis/.developer` and `.trellis/workspace/<developer>/` after Trellis init. |
| task creation | Workflow doc lists `python3 ./.trellis/scripts/task.py create "<title>" [--slug <name>]`. | Would create `.trellis/tasks/{MM-DD-name}/`. |
| task lifecycle | `python3 .trellis/scripts/task.py --help` in the cloned Trellis repo listed `create`, `add-context`, `validate`, `list-context`, `start`, `current`, `finish`, `set-branch`, `set-base-branch`, `set-scope`, `archive`, `list`, `add-subtask`, `remove-subtask`, and `list-archive`. | Lightweight help command ran inside `external/trellis`; it did not initialize this project. |
| task files | Workflow doc says each task directory contains `prd.md`, `implement.jsonl`, `check.jsonl`, `task.json`, optional `research/`, and `info.md`. | This is the likely migration target for current notes. |
| specs | README and workflow doc describe `.trellis/spec/` as injected shared project guidance. | ARTI-6 safety and research workflow rules should live there after initialization. |
| workspace journals | Workflow doc describes `.trellis/workspace/<developer>/journal-N.md` and `index.md`. | No root Trellis workspace journal exists yet. |
| Codex platform support | Cloned Trellis source includes `.codex/config.toml` and `.codex/hooks.json`; README lists Codex as an init target via `--codex`. | Root Codex/Trellis integration has not been generated. |

## Minimal Trellis-Native Representation

The minimal Trellis-native representation for ARTI-6 LinearVC would be:

1. Initialize Trellis in the workspace root with Codex support, after approval for local npm/Trellis setup:
   ```bash
   trellis init --codex -u bowen
   ```
2. Initialize developer identity if needed:
   ```bash
   python3 ./.trellis/scripts/init_developer.py bowen
   ```
3. Create one planning task:
   ```bash
   python3 ./.trellis/scripts/task.py create "ARTI-6 LinearVC feasibility planning" --slug arti6-linearvc-feasibility
   ```
4. Put the current project brief, gates, risk register, and audit summaries into:
   - `.trellis/tasks/<task>/prd.md`
   - `.trellis/tasks/<task>/research/`
   - `.trellis/tasks/<task>/task.json`
   - `.trellis/tasks/<task>/implement.jsonl`
   - `.trellis/tasks/<task>/check.jsonl`
5. Add durable safety and research engineering rules to `.trellis/spec/`, including:
   - no model/dataset downloads without explicit approval
   - no ARTI-6 execution until checkpoints, dataset paths, sample rates, and environment are verified
   - no lab-server assumptions
   - required failure-reporting format
   - ARTI-6 LinearVC gate definitions and acceptance criteria

## Files To Keep

Keep these files as useful project records:

- `AGENTS.md`: current safety policy and workspace assumptions.
- `LOCAL_CONTEXT.md`: local context marker.
- `.gitignore`: excludes data, models, caches, logs, and checkpoints.
- `PROJECT_STATE.json`: current compact machine-readable state until Trellis task state replaces or mirrors it.
- `research_notes/00_trellis_audit.md`: Trellis capability audit.
- `research_notes/00_project_brief.md`: project brief.
- `research_notes/01_arti6_audit.md`: ARTI-6 source audit.
- `research_notes/02_dataset_audit.md`: dataset audit.
- `research_notes/03_related_work_questions.md`: related-work search plan.
- `research_notes/04_experiment_design.md`: minimal demo design.
- `research_notes/06_risk_register.md`: risk register.
- `research_notes/07_human_in_the_loop_questions.md`: decision questions.
- `research_notes/08_verdict_and_scope.md`: scope and verdict notes.
- `external/trellis/`: cloned reference source, unless later replaced by installed Trellis templates.
- `external/arti-6/`: cloned source audit target, with no model/checkpoint downloads.

## Provisional Files Or Migration Targets

These files are useful but not Trellis-native:

- `research_harness/configs/task_arti6_linearvc.yaml`: migrate into a Trellis task PRD plus task metadata. It should not become a parallel custom harness.
- `PROJECT_STATE.json`: keep during transition, but avoid duplicating Trellis task state long term. It can remain as a research state summary if it is explicitly synchronized.
- `research_notes/*.md`: keep as source notes, then copy or reference the high-signal parts under `.trellis/tasks/<task>/research/` and `.trellis/spec/`.

## Next Trellis Task

The next Trellis task should be:

`ARTI-6 LinearVC feasibility planning and safety-gated smoke-test design`

Task purpose:

- Migrate the existing ARTI-6 and dataset audit notes into Trellis task research files.
- Convert the existing gate list into a Trellis PRD.
- Add Trellis specs for no-download, no-lab-assumption, checkpoint approval, dataset approval, and exact failure reporting.
- Stop before running ARTI-6, downloading checkpoints, downloading datasets, or installing heavyweight GPU packages.

This should remain a planning/research task until the human explicitly approves environment setup and small controlled downloads.

## Is Trellis Worth Continuing?

Yes, if the workspace is expected to continue into multi-step research engineering, lab-server handoff, and gated implementation. Trellis gives a stronger structure for PRDs, research records, specs, task state, and session journals than the current ad hoc files.

The current lightweight markdown/script workflow is adequate for early audits, but it already created a split-brain state: Trellis is declared as primary, while actual work is tracked in `research_notes/`, `PROJECT_STATE.json`, and `research_harness/`. Continuing this way risks unclear task state and duplicated harness concepts.

## Recommendation

Recommendation: A. Use Trellis from now on and migrate current notes/tasks into Trellis.

Rationale:

- Trellis purpose is clear enough from local README and workflow docs.
- Trellis was not used yet, so migration is still cheap.
- Current files should be treated as seed material, not as a replacement harness.
- The custom `research_harness/` YAML should not be expanded further unless Trellis proves unsuitable after actual initialization.

## Remaining UNKNOWN

- Whether `trellis init --codex -u bowen` succeeds in this workspace without unexpected side effects.
- Whether the local installed npm package version matches the cloned Trellis source.
- Whether the lab server has compatible Node, Python, and Codex/Trellis support.
- Whether Trellis task hooks should be enabled in this repo or kept manual for safety.
- Whether `PROJECT_STATE.json` should remain as a separate state artifact after Trellis migration.

## Final Status

GO: Trellis usage clarified
