# Trellis Harness Guidelines

## Scope

Applies to `.trellis/`, `.agents/`, `.codex/`, `.gemini/`, `.agent/`, and other
AI-platform integration files generated or maintained for this workspace.

## Pre-Development Checklist

Read these before changing the harness:

- `.trellis/spec/repo-structure.md`
- `.trellis/spec/guides/trellis-system-overview_CN.md`
- `.agents/skills/trellis-meta/SKILL.md`

## Local Rules

- Treat `.trellis/workflow.md` as the workflow source of truth.
- Keep platform entry points aligned with the workflow and with
  `.trellis/scripts/common/cli_adapter.py`.
- Prefer project-local edits over changing upstream Trellis source unless the
  user explicitly asks for an upstream contribution.
- Antigravity uses `.agent/workflows/` for user-invoked Trellis workflows,
  `.agent/skills/` for auto-triggered Trellis skills, and `agy --print` for
  non-interactive CLI prompt execution.

## Scenario: Antigravity Local Platform Support

### 1. Scope / Trigger

Use this contract when adding or updating local support for Google Antigravity in
this workspace. The integration spans platform entry files and the Trellis CLI
adapter, so changes must keep `.agent/` files and
`.trellis/scripts/common/cli_adapter.py` consistent.

### 2. Signatures

Workflow files:

- `.agent/workflows/start.md`
- `.agent/workflows/continue.md`
- `.agent/workflows/finish-work.md`

Skill root:

- `.agent/skills/trellis-*/SKILL.md`

CLI adapter signatures:

```python
CLIAdapter("antigravity").build_run_command(
    agent="trellis-implement",
    prompt="<prompt>",
    session_id=None,
    skip_permissions=True,
)
CLIAdapter("antigravity").build_resume_command("<conversation-id>")
```

Generated command shape:

```bash
agy --print --dangerously-skip-permissions "<prompt>"
agy --print --conversation "<conversation-id>" --dangerously-skip-permissions "<prompt>"
agy --conversation "<conversation-id>"
```

### 3. Contracts

- Antigravity workflow files must pass `--platform antigravity` when loading
  step-specific Trellis workflow guidance.
- Non-interactive prompt execution uses `agy --print` with the prompt as the
  final positional argument.
- Resume-by-id uses `agy --conversation <conversation-id>`.
- If `skip_permissions=True`, include `--dangerously-skip-permissions`.
- The adapter must not require Antigravity agent definition files; Antigravity
  uses workflows/skills rather than Trellis sub-agent files.

### 4. Validation & Error Matrix

- `agy` missing from `PATH` -> document as an environment/setup problem; do not
  silently fall back to another platform.
- `.agent/workflows/` missing -> Antigravity users cannot invoke Trellis
  workflows; restore workflow files.
- `.agent/skills/` missing -> auto-triggered Trellis skills are unavailable in
  Antigravity; restore skill files.
- `build_run_command("antigravity")` raises unsupported-platform errors -> local
  CLI adapter is stale and must be updated.

### 5. Good/Base/Bad Cases

- Good: `.agent/` contains workflows/skills, `agy --help` works, and the adapter
  emits `agy --print` commands.
- Base: Workflows are present but non-interactive CLI use is not needed for the
  current task.
- Bad: Only `.gemini/` or `.codex/` is configured and Antigravity has no local
  `.agent/` entry points.

### 6. Tests Required

- `agy --help`
- `python3 -m py_compile .trellis/scripts/common/cli_adapter.py`
- Python assertion that `CLIAdapter("antigravity").build_run_command(...)`
  returns an `agy --print ...` command.
- `python3 ./.trellis/scripts/get_context.py --mode phase --step 2.1 --platform antigravity`
- `find .agent -maxdepth 5 -type f`

### 7. Wrong vs Correct

Wrong:

```python
elif self.platform == "antigravity":
    raise ValueError("CLI agent run is not supported.")
```

Correct:

```python
elif self.platform == "antigravity":
    cmd = ["agy", "--print"]
    if session_id:
        cmd.extend(["--conversation", session_id])
    if skip_permissions:
        cmd.append("--dangerously-skip-permissions")
    cmd.append(prompt)
```
