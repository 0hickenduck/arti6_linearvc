# Research: Gemini 3 model alias update

- Query: What model IDs should `delegate_to_gemini.sh --model flash/pro` use by default?
- Scope: external + local implementation
- Date: 2026-05-19

## Official model IDs confirmed

- Gemini 3.1 Pro Preview model code: `gemini-3.1-pro-preview`.
- Gemini 3 Flash Preview model code: `gemini-3-flash-preview`.
- Google AI docs say Gemini 3 Pro Preview was deprecated and shut down on 2026-03-09; migrate to Gemini 3.1 Pro Preview.
- Gemini CLI docs say `--model` / `/model` do not override sub-agent models, so `.gemini/settings.json` agent overrides also need the updated Pro model.

## Local changes made

- `.trellis/scripts/delegate_to_gemini.sh`
  - `flash` default: `gemini-3-flash-preview`
  - `pro` default: `gemini-3.1-pro-preview`
- `AGENTS.md`
  - Updated user-facing model alias docs.
- `.gemini/settings.json`
  - `trellis-research`: `gemini-3-flash-preview`
  - `trellis-implement`: `gemini-3.1-pro-preview`
  - `trellis-check`: `gemini-3.1-pro-preview`
- `external/trellis/packages/cli/src/templates/gemini/settings.json`
  - Synced generated template default overrides.
- `external/trellis/packages/cli/test/configurators/platforms.test.ts`
  - Synced expected Pro model IDs.
- `external/trellis/packages/cli/test/regression.test.ts`
  - Synced expected Pro model IDs.

## Verification

- `bash -n .trellis/scripts/delegate_to_gemini.sh` passed.
- `delegate_to_gemini.sh --help` shows:
  - `flash  ${GEMINI_FLASH_MODEL:-gemini-3-flash-preview}`
  - `pro    ${GEMINI_PRO_MODEL:-gemini-3.1-pro-preview}`
- `.gemini/settings.json` and external Gemini template both parse as JSON and show the updated overrides.
- Runtime probe with `--model flash` logged:
  - `model=gemini-3-flash-preview`
  - Gemini read the active task PRD title successfully.

## Test caveat

Attempted to run Trellis package tests through Corepack/Pnpm, but the local Corepack invocation entered a recursive `pnpm@10.12.4` loop and had to be killed. No test result is available from that command in this environment.
