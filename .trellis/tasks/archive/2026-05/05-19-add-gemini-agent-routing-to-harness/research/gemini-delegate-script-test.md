# Research: Gemini delegate script test

- Query: Did K's added harness skill/tool actually allow Codex to call Gemini as a delegated worker/sub-agent?
- Scope: internal execution probe
- Date: 2026-05-19

## Entry points found

### Project instructions

`AGENTS.md` defines two agent classes:

- Native GPT sub-agents: invoked through native subagent protocols.
- Gemini worker bees: invoked through the bash tool with:

```bash
~/.gemini/extensions/superpowers/skills/delegate-to-gemini/delegate.sh --model <model> --prompt "<instructions>"
```

### Global wrapper

`~/.gemini/extensions/superpowers/skills/delegate-to-gemini/delegate.sh` exists and is executable. It searches upward for `.trellis/scripts/delegate_to_gemini.sh` and execs it.

### Project-local delegate script

`.trellis/scripts/delegate_to_gemini.sh` exists and launches Gemini CLI headless through:

```bash
gemini --skip-trust --extensions "" --approval-mode <mode> --output-format text [-m <model>] -p <prompt>
```

It supports model aliases:

- `auto` -> omit `--model`
- `flash` -> `${GEMINI_FLASH_MODEL:-gemini-3-flash-preview}`
- `pro` -> `${GEMINI_PRO_MODEL:-gemini-3.1-pro-preview}`
- custom model id -> passed through directly

## Tests run

### 1. Exact global script, read-only probe

Command used the exact `AGENTS.md` path with `--model flash --approval-mode plan`.

Result:

- Gemini launched successfully.
- Trellis SessionStart hook injected context.
- Gemini saw the repo root.
- `.trellis` existed.
- Active task PRD title was readable.

### 2. Project-local script, safe write probe

Command used `--approval-mode auto_edit` and asked Gemini to create one file under active task `research/`.

Result:

- Gemini created `.trellis/tasks/05-19-add-gemini-agent-routing-to-harness/research/gemini-delegate-write-probe.md`.
- It did not modify code/config/specs.
- Output included a Gemini CLI stream warning (`Invalid stream...`) after the file was written, but process exit code was `0` and the artifact existed.

### 3. `@trellis-research` probe

Prompt asked Gemini to use `@trellis-research` if available and create one task-local research file.

Result:

- Gemini created `.trellis/tasks/05-19-add-gemini-agent-routing-to-harness/research/gemini-trellis-research-agent-probe.md`.
- The generated report claimed a Gemini sub-agent was invoked, but this evidence is not fully conclusive from stdout alone because Gemini CLI did not emit a structured agent invocation trace in text output.

### 4. Active-task handoff fix

Initial script tried to infer active task via legacy `.trellis/current_task`. Current Trellis uses `task.py current --source`, so the script was patched to:

- call `python3 ./.trellis/scripts/task.py current --source`,
- extract the task path,
- prepend `Active task: <task path>` as the first line of the Gemini prompt.

After the fix, a probe without manually adding an `Active task:` line confirmed Gemini received:

```text
.trellis/tasks/05-19-add-gemini-agent-routing-to-harness
```

and could read the active task PRD title.

## Verdict

YES: K's added delegate path is real and usable from Codex through bash. It can launch Gemini as an external worker, pass model aliases, read the Trellis harness, receive active task context, and write bounded task-local artifacts.

Caveats:

- The current mechanism is best described as **Gemini worker delegation through a shell skill/script**, not a native Codex `spawn_agent` sub-agent.
- `--model flash/pro` currently maps to Gemini 2.5 defaults unless `GEMINI_FLASH_MODEL` / `GEMINI_PRO_MODEL` are set or a full model id is passed.
- Gemini CLI text output sometimes reports `Invalid stream` after successful writes; treat artifact existence and exit code as the verification source.
- In plan mode Gemini read tools work, but shell tool calls are not available; use `auto_edit` or stronger modes only for trusted bounded write tasks.
