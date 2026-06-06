---
name: trellis-research-survey
description: "Build source-grounded deep-learning survey artifacts: paper/code/source evidence stores, human-readable survey synthesis, experiment shortlists, and optional Gemini/Antigravity survey delegation. Use when surveying papers, extracting paper methods/experiments, judging benchmark candidates, or preparing idea-generation context."
---

# Research Survey

Use this skill for the survey part of the research system. The goal is a
human-readable survey plus a file-backed evidence store, not a private chat
summary.

## Workflow

1. Resolve the active task:
   ```bash
   python3 ./.trellis/scripts/task.py current --source
   ```
2. Create task-local survey folders:
   ```bash
   python3 ./.trellis/scripts/research_survey.py init
   ```
3. For broad scouting or extraction, optionally delegate:
   ```bash
   python3 ./.trellis/scripts/research_survey.py delegate \
     --backend auto \
     --topic "<research topic>"
   ```
   `auto` tries Gemini first when available, then Antigravity. Use
   `--backend gemini`, `--backend antigravity`, or `--backend local` for an
   explicit path.
4. For important papers, create or update:
   ```text
   {TASK_DIR}/survey/papers/<paper-id>/
     metadata.yaml
     source.md
     code.md
     extraction.md
     summary.md
     relevance.md
   ```
5. Write the human-readable synthesis in:
   ```text
   {TASK_DIR}/survey/reports/survey.md
   ```
6. Promote only experiment-relevant papers into:
   ```text
   {TASK_DIR}/survey/shortlists/experiment-<name>.md
   ```

## Extraction Contract

For each important paper, preserve:

- idea
- method
- experiment-design pattern
- datasets
- metrics
- ablations
- implementation/code availability
- arXiv/OpenReview/DOI/source links
- benchmark role: broad context, related-work evidence, possible pivot/baseline,
  experiment-critical reference, or rejected/archived candidate

The human-readable survey should be selective: enough for human judgment, not a
dump of every extraction field.

## Benchmark Rule

A paper without usable open-source code defaults to `survey/reference only`.
Do not treat it as a baseline candidate unless the user explicitly accepts the
cost/risk of reimplementation.

## Delegation Failures

If Gemini, Antigravity, internet access, source extraction, or code cloning
fails, record it:

```bash
python3 ./.trellis/scripts/research_survey.py record-problem \
  --title "<short problem>" \
  --context "<what we were trying>" \
  --command "<command or backend>" \
  --evidence "<stderr/stdout summary>" \
  --next "<next diagnostic>"
```

The script appends to `{TASK_DIR}/evolution.md` and the developer workspace
evolution backlog when available.
