# Research: Gemini agent model routing

- **Query**: Can Gemini CLI use Flash for search-like work and Pro for code editing, with natural-language routing?
- **Scope**: mixed
- **Date**: 2026-05-19

## Findings

### Relevant repo files

| File Path | Description |
|---|---|
| `.gemini/agents/trellis-research.md` | Existing research sub-agent definition. |
| `.gemini/agents/trellis-implement.md` | Existing implementation sub-agent definition. |
| `.gemini/agents/trellis-check.md` | Existing verification sub-agent definition. |
| `.gemini/settings.json` | Current Gemini project settings; hooks exist, but no agent model overrides yet. |
| `.trellis/workflow.md` | Already tells Gemini main sessions to dispatch `trellis-research`, `trellis-implement`, and `trellis-check`. |

### External references

- Gemini CLI supports explicit model selection via `/model` / `--model`, but that does **not** override sub-agent models.
- Gemini CLI sub-agents can be configured independently via `agents.overrides.<agent>.modelConfig.model`.
- Custom local sub-agent definition files may also set `model:` in frontmatter.
- Gemini CLI docs describe automatic delegation from the main agent when a task matches a specialist's expertise, plus explicit `@agent-name` forcing syntax.
- Current official Gemini CLI docs list `gemini-3-flash-preview` and `gemini-3.1-pro-preview` among Gemini 3 model options.

### Implications for this repo

A clean first version is feasible without changing the harness architecture:

1. Pin `trellis-research` to `gemini-3-flash-preview`.
2. Pin `trellis-implement` and likely `trellis-check` to `gemini-3.1-pro-preview`.
3. Strengthen routing instructions so natural user language like “look into X” prefers the research agent, while “change/fix/build X” prefers the implementation path.
4. Optionally add lightweight user-facing shortcuts later, but they are not required for the MVP because Gemini already supports automatic delegation and `@agent` forcing.

## Caveats / Not Found

- The docs show the primitives, but the exact quality of automatic natural-language routing depends on prompt design and should be tested locally.
- `/model` changes the main session model only; it is not sufficient by itself for role-specific routing.
