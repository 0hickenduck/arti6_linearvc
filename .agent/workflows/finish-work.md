# Finish Work

Wrap up the current session. There are two valid modes:

- **Full wrap-up**: archive the active task and record the session journal.
  Code commits are done before this workflow in `.trellis/workflow.md`
  Phase 3.4.
- **Session-only record**: when the user asks to "create session", "record
  session", or otherwise only wants a journal entry, record the session without
  archiving and without requiring a clean working tree.

Use session-only mode for in-progress work or when current-task code is
intentionally still dirty.

## Step 1: Survey Current State

```bash
python3 ./.trellis/scripts/get_context.py --mode record
```

This prints:

- **My active tasks** - review whether any besides the current one are actually
  done and should be archived this round.
- **Git status** - quick visual on what's dirty.
- **Recent commits** - use work commit hashes in Step 4.

If `--mode record` surfaces other completed tasks not tied to the current
session, ask the user once whether to archive them too. Default is no; the
current active task is always archived in Step 3 when complete.

## Step 2: Sanity Check Dirty Paths

Skip this archive gate in session-only mode. For session-only mode, run Step 4
and Step 5 with `add_session.py --no-commit` so the journal is written without
auto-staging active task directories.

Run:

```bash
git status --porcelain
```

Filter out paths under `.trellis/workspace/` and `.trellis/tasks/`; those are
managed by `add_session.py` and `task.py archive`.

For each remaining dirty path, decide whether it belongs to the current task or
to other parallel work. If any remaining path is current-task work, return to
Phase 3.4 and commit it before running this workflow. If all remaining paths are
unrelated, report them once and continue.

## Step 3: Archive Task

Skip this step in session-only mode.

```bash
python3 ./.trellis/scripts/task.py archive <task-name>
```

At minimum, archive the current active task if it is complete. The script
creates a `chore(task): archive ...` commit when session auto-commit is enabled.

## Step 4: Record Evolution Notes

Before recording the journal, review whether the session exposed operational
problems worth evolving later, for example:

- Gemini/Antigravity/other agent CLI failure
- internet, proxy, paper download, dataset download, or code clone failure
- PDF/LaTeX/Markdown source extraction failure
- benchmark install/reproduction failure
- GPU/CPU utilization, NaN, dead process, or stalled run issue
- missing, stale, noisy, or misleading agent handoff context

If yes, record concise evidence:

```bash
python3 ./.trellis/scripts/research_survey.py record-problem \
  --title "<short problem>" \
  --context "<what we were trying>" \
  --command "<command/backend>" \
  --evidence "<stderr/stdout summary>" \
  --next "<next diagnostic>"
```

If no, say "No evolution notes this session" in the journal content.

## Step 5: Record Session Journal

```bash
python3 ./.trellis/scripts/add_session.py \
  --title "Session Title" \
  --commit "hash1,hash2" \
  --summary "Brief summary"
```

Use the work commit hashes produced in Phase 3.4. Do not include archive commit
hashes from Step 3. Include evolution-note status in the session content or
summary.

For session-only mode, use:

```bash
python3 ./.trellis/scripts/add_session.py \
  --stdin \
  --no-commit \
  --title "Session Title" \
  --commit "-" \
  --summary "Brief summary"
```

This writes the journal/index but does not archive, does not require a clean
working tree, and does not auto-stage active task directories.
