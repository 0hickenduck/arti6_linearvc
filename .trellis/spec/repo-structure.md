# Repository Structure Guidelines

## Core Principles
1. **Single-Purpose Repository**: This repository is dedicated solely to the ARTI-6 + LinearVC research engineering demo. Do not mix other distinct research projects here.
2. **Trellis as the Source of Truth**: The `.trellis/` directory governs workflow, architectural knowledge, and task management.

## Directory Layout
- `.trellis/`: The Trellis harness (specs, tasks, active workflow).
  - `.trellis/spec/`: Project-wide architectural and policy documents.
  - `.trellis/tasks/`: Active task execution, scoping, and task-specific research.
- `arti6_linearvc_demo/`: The primary source code for the local preparation and execution of the demo. All AI-generated implementation code eventually lands here.
- `external/`: External dependencies, submodules, and cloned repositories (e.g., `arti-6`, `trellis`).
- `archive/research_notes/`: Legacy, pre-Trellis research notes. Read-only.

## Code Migration
When scaffolded code in a task directory (e.g., `.trellis/tasks/0x-scaffold/...`) is verified and approved, it should be cleanly migrated into `arti6_linearvc_demo/`.