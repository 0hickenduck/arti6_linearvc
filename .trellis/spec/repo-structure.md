# Repository Structure Guidelines

## Core Principles
1. **Workspace With Separate Research Lanes**: This repository now carries more
   than the original ARTI-6 + LinearVC demo. Keep VTuber data curation, ARTI6
   demo work, and Trellis harness work separated by directory and by Trellis
   package metadata.
2. **Trellis as the Source of Truth**: The `.trellis/` directory governs
   workflow, architectural knowledge, package boundaries, and task management.
3. **Large Data Outside Git**: Raw audio/video, separated stems, generated
   datasets, checkpoints, caches, and archives stay out of normal git. Commit
   code, docs, task notes, manifests, and small reproducibility metadata.

## Directory Layout

- `.trellis/`: Workspace harness, specs, tasks, active workflow, scripts, and
  task memory.
  - `.trellis/spec/`: Project-wide and package-specific architectural/policy
    documents.
  - `.trellis/tasks/`: Active task execution, scoping, and task-specific
    research.
- `.agent/`: Antigravity workflows and skills for this workspace.
- `.agents/skills/`: Shared Trellis skills used by Codex and compatible tools.
- `vtuber_pipeline/`: Current VTuber speech/singing data pipeline. This is the
  active lane for YouTube audio discovery, source separation orchestration,
  conservative segmentation, and curation manifests.
- `arti6_linearvc_demo/`: Original ARTI-6 + LinearVC research demo lane.
- `projects/`: Human-readable lane index and future split points. Do not put
  generated datasets here.
- `external/`: External dependencies, submodules, and cloned repositories
  (for example `seed-vc` and `trellis`).
- `docs/`: Operational notes such as local/server GitHub sync.
- `archive/research_notes/`: Legacy, pre-Trellis research notes. Read-only.
- `data/`, `outputs/`, `.venv/`: Local-only generated/runtime material, ignored
  by git.

## Code Migration

When scaffolded code in a task directory is verified and approved, migrate it to
the relevant lane:

- VTuber curation, manifests, and YouTube audio processing -> `vtuber_pipeline/`
- ARTI-6 / LinearVC reproduction and demo scripts -> `arti6_linearvc_demo/`
- Trellis/platform integration -> `.trellis/`, `.agents/`, `.codex/`,
  `.gemini/`, `.agent/`, or the relevant platform directory

Avoid physical moves that break runnable scripts unless the task explicitly
includes path migration and validation.
