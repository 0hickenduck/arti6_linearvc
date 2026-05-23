# Research: Existing orchestration tools

- Query: Is there an existing tool we can reuse so Codex can delegate to Gemini with routing/model control instead of building everything ourselves?
- Scope: external
- Date: 2026-05-19

## Findings

| Candidate | What it already gives | Fit for our need |
|---|---|---|
| AWS Labs CLI Agent Orchestrator (CAO) | Cross-provider workers across Codex/Gemini/etc.; supervisor-worker model; MCP control plane; synchronous `handoff` and async `assign`; per-agent model honored at launch | Closest fit as a reusable **delegation substrate** |
| Maestro Orchestrate | Rich workflow/orchestration plugin that runs on Gemini, Claude, Codex, Qwen from one canonical tree | Good workflow system, but appears more like “same orchestrator on each runtime” than “Codex calls Gemini worker” |
| Forge / ACP | Unified way to launch multiple coding agents | Useful interoperability layer, but not a task router/orchestrator by itself; Gemini model selection via ACP is still limited |
| Overstory | Full multi-agent platform with pluggable runtimes, coordinator/orchestrator, worktrees, mail system | Powerful but likely overkill and would compete with Trellis as the harness |
| wraptc | Lightweight multi-provider router with fallback and MCP server | Interesting inspiration for provider routing, but looks like a young personal utility rather than a mature base to bet the harness on |

## Best current interpretation

* If we want **maximum reuse** and **closest behavior to native delegation**, CAO is the strongest candidate to spike first.
* If we want **minimum disruption** to the current Trellis harness, we probably should not adopt a whole second workflow system like Overstory or Maestro as the new brain.
* A promising hybrid is:
  * Trellis stays the project memory/task/spec layer.
  * Codex stays the human-facing coordinator.
  * CAO becomes the worker-launch/delegation substrate behind the scenes.
  * A thin project-local routing policy decides when to hand off search/edit/review work and which provider/model profile to use.

## Caveats / Not Found

* I did not find a mature tool that already drops directly into Trellis and gives exactly “Codex-led natural-language router with Gemini worker profiles” out of the box.
* Any reuse path will still need a small adapter layer so Trellis task context, routing policy, and safety rules survive the handoff.

## Additional option: Gemini-as-MCP bridge

* A third-party `gemini-cli-mcp-server` exposes Gemini CLI as MCP tools such as `gemini_prompt`, `gemini_cli`, `gemini_summarize_files`, and accepts explicit `model=` arguments.
* This is especially attractive for **search / analysis / review** delegation because Codex already supports connecting to MCP servers, so Gemini can feel like a callable native tool from the Codex side.
* It is less obviously a full replacement for **stateful implementation workers** because it is primarily a tool bridge, not a full cross-provider session orchestrator with task lifecycle and worker control.

## Refined recommendation shape

1. **If the first goal is near-native Gemini search from Codex:** use or borrow from a Gemini MCP bridge.
2. **If the first goal is true worker delegation, including editing and parallel workers:** evaluate CAO first.
3. **If both are desired:** the architecture can be layered — MCP bridge for light delegation, CAO or a thin custom worker runner for heavier execution.
