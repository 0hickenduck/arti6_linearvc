# Research: GPT auxiliary dispatch test

- Query: Can the parent Codex session call a GPT/Codex auxiliary worker for search or code-writing, and does it share harness/tools/context?
- Scope: internal execution probe
- Date: 2026-05-19

## Summary

A local auxiliary GPT/Codex worker can be launched successfully via `codex exec` from the parent session. It can see the repository, see `.trellis/.codex/.gemini/.agents`, use shell tools, read the active task PRD when the active task is explicitly passed, and write a harmless code artifact inside the active task research directory.

## What worked

### Local Codex CLI availability

- `codex-cli 0.130.0` is installed at `/home/bowen/.nvm/versions/node/v20.20.2/bin/codex`.
- `gemini 0.42.0` is also installed, but this test focused on GPT/Codex auxiliary dispatch.

### Auxiliary worker via `codex exec`

The parent launched:

```bash
codex exec \
  --cd /home/bowen/bowen_lab/projects/arti6_linearvc \
  --skip-git-repo-check \
  --sandbox workspace-write \
  --output-last-message <report-file> \
  'Active task: .trellis/tasks/05-19-add-gemini-agent-routing-to-harness
   ...task prompt...'
```

Results:

- CWD visible: `/home/bowen/bowen_lab/projects/arti6_linearvc`
- Harness directories visible:
  - `.trellis`
  - `.codex`
  - `.gemini`
  - `.agents`
- Shell tools worked.
- Active task PRD was readable when `Active task: ...` was included in the dispatch prompt.
- A harmless code-writing probe succeeded inside `research/`:
  - `.trellis/tasks/05-19-add-gemini-agent-routing-to-harness/research/codex_exec_aux_code_probe.py`

## What did not work / caveats

### Platform `spawn_agent` path was unreliable in this run

Several `spawn_agent` probes timed out or shut down without writing the requested artifact. One minimal spawned agent reported stale/incorrect task state. This channel should not be treated as the reliable execution substrate for this harness until separately debugged.

### Active task is not automatically inherited by new Codex exec sessions

A first `codex exec` probe without explicit task handoff saw:

```text
Current task: (none)
Source: none
```

Root cause: Trellis current-task state is session-scoped. A new `codex exec` process creates a new Codex session and does not inherit the parent session's active-task pointer.

### Fix

Always prepend the dispatch prompt with:

```text
Active task: <task path>
```

This matches the existing Trellis class-2 sub-agent protocol. With that line, the auxiliary worker can read the task PRD and task-local research files directly.

## Verdict

YES, the parent Codex session can call a GPT/Codex auxiliary model through local `codex exec` for search-like work, harness inspection, and code-writing tasks. It is not identical to the parent process: task context is not automatically inherited. The reliable fix is explicit context handoff via `Active task: ...` plus any role/model/router metadata in the dispatch prompt.

This is a viable pattern for the future router:

```text
Codex parent
  -> builds dispatch prompt with Active task + role + safety policy + model/provider
  -> launches codex exec or gemini CLI
  -> captures final report via --output-last-message / output file
  -> parent reviews and integrates
```
