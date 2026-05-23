# Research: Gemini CLI capabilities relevant to delegation

- Query: What current Gemini CLI capabilities matter for model selection and subagent routing?
- Scope: external
- Date: 2026-05-19

## Findings

* Gemini CLI supports model selection via `/model` and `--model` / `-m`.
* Gemini CLI documentation states that the main model selection does **not** override models used by subagents.
* Gemini CLI has first-class subagents with:
  * automatic delegation by the main agent,
  * explicit forcing via `@agent`,
  * per-agent config overrides such as `modelConfig.model`.
* Current official docs mention `gemini-3.1-pro-preview` as rolling out and available through manual selection when the account has access.

## Implication for our harness

* If we want `search model` and `edit model` separately, a Trellis-level routing layer must carry those choices explicitly; relying only on Gemini's global `--model` is not enough for subagent-specific behavior.
* Gemini is already conceptually aligned with the user's goal: delegate heavy subtasks into isolated context loops and select models per specialist.

## External References

* Official Gemini CLI model-selection docs.
* Official Gemini CLI subagents docs.
* Official Gemini CLI command/reference docs.

## Caveats / Not Found

* Availability of specific preview models is account-dependent and may vary over time.
