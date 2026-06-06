# Research System Contract

## Scope

Applies to deep-learning research workflow automation in this repository:
survey, idea review, benchmark selection, experiment design, implementation,
experiment monitoring, result analysis, and claim audit.

## Core Principles

1. **Automate engineering, not judgment**: automate search, extraction,
   bookkeeping, monitoring, and reproducibility checks. Keep human checkpoints
   for theme choice, idea judgment, novelty judgment, and expensive compute.
2. **Survey has two outputs**: a human-readable survey for judgment and a
   file-backed evidence store for agents and reproducibility.
3. **Open-source code gates benchmarks**: papers without usable code can inform
   ideas and related work, but default to `survey/reference only`, not baseline.
4. **Correspondence is end-to-end**: sources, prior claims, benchmark behavior,
   method changes, experiment design, code, metrics, plots, analysis, and paper
   claims must map to one another.
5. **Evolution comes from real failures**: record operational problems at
   session finish or when they happen; promote repeated problems into new hooks,
   skills, workflow gates, or specs later.

## Survey Evidence Store

Task-local survey artifacts live under:

```text
{TASK_DIR}/survey/
  papers/<paper-id>/
    metadata.yaml
    source.md
    code.md
    extraction.md
    summary.md
    relevance.md
  reports/survey.md
  shortlists/experiment-<name>.md
```

`extraction.md` preserves detailed paper evidence: idea, method, experiment
setup, datasets, metrics, ablations, and implementation availability. The
human-readable `reports/survey.md` should summarize only the decision-relevant
parts.

## Experiment Design Boundary

Survey can record how prior papers design experiments, but our experiment
design is created later, after selecting a theme, idea, and benchmark candidate.
The design must state the exact question, codebase to modify, borrowed
ablations, minimal baseline delta, fixed metrics/datasets/splits/compute, and
support/failure signals.

## Evolution Backlog

Operational problems should be recorded as evidence, not immediately baked into
the main workflow. Good entries include:

- failed Gemini/Antigravity/other agent command
- internet/proxy/download/code-clone failure
- source extraction failure
- benchmark install or reproduction failure
- GPU/CPU utilization, NaN, dead process, or stalled run
- stale/noisy/missing handoff context

Record task-local entries in `{TASK_DIR}/evolution.md` and cross-session entries
in `.trellis/workspace/<developer>/evolution-backlog.md`.

## Scenario: Task-Local Research Survey CLI

### 1. Scope / Trigger

Use `.trellis/scripts/research_survey.py` when a task needs a survey evidence
store, paper templates, delegated scouting, or an operational-problem record.

### 2. Signatures

```bash
python3 ./.trellis/scripts/research_survey.py init [--task <task-dir>]
python3 ./.trellis/scripts/research_survey.py paper [--task <task-dir>] [paper metadata]
python3 ./.trellis/scripts/research_survey.py delegate \
  [--task <task-dir>] --backend auto|gemini|antigravity|local \
  --topic "<topic>" [--instructions "<text>"] [--output <path>] [--timeout <seconds>]
python3 ./.trellis/scripts/research_survey.py record-problem \
  [--task <task-dir>] --title "<title>" [evidence fields]
```

### 3. Contracts

- Without `--task`, resolve the current task through `task.py current --source`.
- `init` creates `survey/papers`, `survey/reports`, `survey/shortlists`, and
  `research` without overwriting an existing survey report.
- `delegate --backend local` prints the prompt and does not invoke an external
  CLI or write a delegated report.
- Successful external delegation writes UTF-8 Markdown under
  `survey/reports/`, unless `--output` is supplied.
- Default delegated filenames keep at most 80 topic-slug characters, append a
  stable 10-character SHA-256 prefix, then append a timestamp. The complete
  filename must remain below common 255-byte component limits.
- `record-problem` appends to the task evolution file and, when a developer is
  configured, the developer evolution backlog.

### 4. Validation & Error Matrix

- No active task and no `--task` -> exit with a task-resolution error.
- Requested Gemini/Antigravity CLI absent -> record an evolution problem and
  return status `2`.
- External command timeout -> record evidence and continue to the next backend.
- External command failure or empty output -> record evidence and return
  nonzero if no backend succeeds.
- Long topic -> truncate only the filename slug; preserve the full topic in the
  delegated prompt.

### 5. Good/Base/Bad Cases

- Good: Gemini returns Markdown; the helper writes a bounded, hashed report
  filename and prints its repository-relative path.
- Base: `--backend local` emits the exact read-only survey prompt for manual or
  native-agent use.
- Bad: deriving the full output filename directly from an unbounded topic can
  raise `OSError: [Errno 63] File name too long`.

### 6. Tests Required

- `python3 -m py_compile .trellis/scripts/research_survey.py`
- Assert a report name generated from a very long topic is below 255 UTF-8
  bytes, includes the hash and timestamp, and ends in `.md`.
- Run `delegate --backend local` and assert the output includes the read-only
  role, candidate-paper requirements, and no-modification instruction.
- Use a fake successful backend with a temporary task directory and assert
  default delegated output is written successfully for a very long topic.

### 7. Wrong vs Correct

Wrong:

```python
filename = f"delegated-{slugify(topic)}-{timestamp}.md"
```

Correct:

```python
slug = slugify(topic)[:80].rstrip("-")
digest = sha256(topic.encode("utf-8")).hexdigest()[:10]
filename = f"delegated-{slug}-{digest}-{timestamp}.md"
```
