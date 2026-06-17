---
name: trellis-finish-work
description: "Wrap up the current session: verify quality gate passed, remind user to commit, archive completed tasks, and record session progress to the developer journal. Use when done coding and ready to end the session."
---

# Finish Work

Wrap up the current session. There are two valid modes:

- **Full wrap-up**: archive the active task and record the session journal. Code commits are NOT done here — those happen in workflow Phase 3.4 before this mode.
- **Session-only record**: when the user asks to "create session", "record session", or otherwise only wants a journal entry, record the session without archiving and without requiring a clean working tree.

Use session-only mode for in-progress work or when current-task code is intentionally still dirty.

## Step 1: Survey current state

```bash
python3 ./.trellis/scripts/get_context.py --mode record
```

This prints:

- **My active tasks** — review whether any besides the current one are actually done (code merged, AC met) and should be archived this round.
- **Git status** — quick visual on what's dirty.
- **Recent commits** — you'll need their hashes in Step 4 for `--commit`.

If `--mode record` surfaces other completed tasks not tied to the current session, surface them to the user with a one-shot confirmation: "These N tasks look done — archive them too in this round? [y/N]". Default is no; the current active task is always archived in Step 3 regardless.

## Step 2: Sanity check — classify dirty paths

Skip this archive gate in session-only mode. For session-only mode, run Step 4
and Step 5 with `add_session.py --no-commit` so the journal is written without
auto-staging active task directories.

Run:

```bash
git status --porcelain
```

Filter out paths under `.trellis/workspace/` and `.trellis/tasks/` — those are managed by `add_session.py` and `task.py archive` auto-commits and will appear dirty as part of this skill's own work.

For each remaining dirty path, decide whether it belongs to **the current task** or to **other parallel work** (e.g., another terminal window editing the same repo). Heuristics:

- Paths referenced in the current task's `prd.md` / `implement.jsonl` / `check.jsonl` → current task
- Paths in code areas matching the task's stated scope, or that you remember editing this session → current task
- Paths in unrelated areas you have no recollection of touching this session → other parallel work

Then route:

- **Any remaining path looks like current-task work** — bail out with:
  > "Working tree has uncommitted code changes from this task: `<list>`. Return to workflow Phase 3.4 to commit them before running ``finish-work` (Trellis command)`."

  Do NOT run `git commit` here. Do NOT prompt the user to commit. The user goes back to Phase 3.4 and the AI drives the batched commit there.
- **All remaining paths look unrelated** (other parallel-window work) — report them once and continue to Step 3:
  > "FYI, dirty files outside this task's scope — leaving them for the other window: `<list>`."
- **Genuinely unsure** — ask the user once: "Are `<list>` this task's work I forgot to commit, or another window's? (commit / ignore)" — then route per their answer.

## Step 3: Archive task(s)

Skip this step in session-only mode.

```bash
python3 ./.trellis/scripts/task.py archive <task-name>
```

At minimum: the current active task (if any). Plus any extra tasks the user confirmed in Step 1. Each archive produces a `chore(task): archive ...` commit via the script's auto-commit.

If there is no active task and the user did not confirm any cleanup archives, skip this step.

## Step 4: Record evolution notes

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

## Step 5: Record session journal

```bash
python3 ./.trellis/scripts/add_session.py \
  --title "Session Title" \
  --commit "hash1,hash2" \
  --summary "Brief summary"
```

Use the work-commit hashes produced in Phase 3.4 (visible in Step 1's `Recent commits` list, or via `git log --oneline`) for `--commit`. Do not include the archive commit hashes from Step 3. This produces a `chore: record journal` commit. Include evolution-note status in the session content or summary.

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

Final git log order: `<work commits from 3.4>` → `chore(task): archive ...` (one or more) → `chore: record journal`.
