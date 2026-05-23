# Agent Collaboration Policy

## Harness Frontend Agnosticism
This repository utilizes Trellis as the core operational brain. Multiple agent frontends (e.g., Codex CLI, Gemini CLI) are configured to operate against this repository. 

## Rules for Agents
1. **Shared Brain**: All state, workflow phases, and project specifications are stored in `.trellis/`. Agents must consult `.trellis/workflow.md` and `.trellis/spec/` before taking significant action.
2. **Hook Execution**: Both `.codex/` and `.gemini/` adapters map back to common `.trellis/scripts/hooks/` to ensure consistent lifecycle events (e.g., `session-start.py`). Do not bypass hooks unless explicitly requested.
3. **Shared vs Platform-Specific Agent Files**: Shared workflow skills live under `.agents/skills/`, but executable sub-agent definitions remain platform-specific (`.codex/agents/*.toml`, `.gemini/agents/*.md`, etc.) because each frontend has its own schema and runtime knobs. Keep their intent aligned, but allow backend-specific settings such as model overrides where the platform supports them.
4. **Task Hand-offs**: If one agent starts a task and it must be resumed later, use `trellis-continue` to ensure context is correctly re-established based on `.trellis/tasks/` state, irrespective of the CLI tool used previously.
