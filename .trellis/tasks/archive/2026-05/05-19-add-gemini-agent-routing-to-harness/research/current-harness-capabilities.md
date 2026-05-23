# Research: Current harness capabilities

- Query: What does the current harness already support for multi-agent, delegation, routing, and Gemini/Codex integration?
- Scope: internal
- Date: 2026-05-19

## Findings

### Existing support

| Area | Evidence | Assessment |
|---|---|---|
| Multi-platform adapters | `.trellis/scripts/common/cli_adapter.py`, `.trellis/spec/agent-collaboration.md` | Supported: Trellis is frontend-agnostic across Codex, Gemini, and others. |
| Shared task/spec brain | `.trellis/spec/agent-collaboration.md`, `.trellis/workflow.md` | Supported: all agents use the same `.trellis/` state. |
| Agent roles | `.codex/agents/*`, `.gemini/agents/*` | Supported: both Codex and Gemini have `trellis-implement`, `trellis-check`, `trellis-research`. |
| Codex sub-agent dispatch | `.codex/config.toml`, `.trellis/workflow.md` | Supported: Codex can use subagents; workflow already models implement/check/research delegation. |
| Gemini CLI command construction | `.trellis/scripts/common/cli_adapter.py:315+` | Partially present: `build_run_command()` has a `gemini` branch. |

### Missing or incomplete support

| Area | Evidence | Gap |
|---|---|---|
| Cross-provider delegation from Codex to Gemini | No local router/dispatcher found | Missing: current workflow talks about subagents inside a platform, not handing work from Codex to Gemini CLI. |
| Model routing | Search across `.trellis`, `.codex`, `.gemini`, `.agents` | Missing: no `search_model`, `edit_model`, provider/model router, or natural-language routing policy found. |
| Gemini as CLI-dispatchable platform in adapter helpers | `.trellis/scripts/common/cli_adapter.py:537+` | Inconsistent: `supports_cli_agents` excludes Gemini despite Gemini command support elsewhere. |
| Search/edit separation | No config or workflow symbols found | Missing. |
| Natural-language override layer | No parsing/policy layer found | Missing. |

## Code Patterns

* The harness already prefers **shared state + thin adapters** rather than duplicate workflows.
* Platform additions are usually made by touching a small registry/configurator surface plus generated templates.
* Current Codex support already distinguishes **coordination** from **implementation/checking** through agent roles; that is the natural seam for provider routing.

## Related Specs

* `.trellis/spec/agent-collaboration.md`
* `.trellis/workflow.md`
* `.trellis/spec/guides/trellis-system-overview_CN.md`

## Caveats / Not Found

* I did not find a local Honeycomb-specific implementation separate from Trellis; in this repo, Trellis appears to be the live harness.
