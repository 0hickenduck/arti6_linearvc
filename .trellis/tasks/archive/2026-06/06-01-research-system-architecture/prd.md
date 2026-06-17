# brainstorm: research system architecture

## Goal

Design a deep-learning research system that uses multiple AI agents aggressively while preventing the workflow from turning into untraceable, polished rubbish. The system should separate survey and idea work from implementation and experiment work, with a strong contract layer between them so every idea, method, result, and claim stays source-grounded and reproducible.

## What I Already Know

- The user wants to start from the most important part of the system rather than designing a giant end-to-end automation blob.
- The intended domain is deep-learning research, especially workflows that look like literature survey, baseline choice, idea selection, implementation, experiments, analysis, and paper writing.
- The system should automate everything that can be automated, but it must not pretend that all research judgment can be automated.
- Some decisions require human interaction, especially judging whether a proposed idea is meaningful, promising, or worth spending compute on.
- Human-readable survey output is required because it is the interface where humans inspect the evidence and make research-theme or idea judgments.
- Survey research must also create a durable evidence store, not just a written report. For each important paper, the system should record arXiv/link metadata, venue/lab/source context, code repository if available, and source/LaTeX/Markdown notes when accessible.
- Survey extraction should capture each paper's idea, method, and experiment-design pattern, but the human-readable survey does not need to include every low-level detail.
- Survey artifacts should be arranged so branch tasks can promote truly experiment-relevant papers into an experiment-specific archive or shortlist without losing the broader survey context.
- The system must support human-in-the-loop decisions, especially during research theme discovery and before committing GPU resources.
- "Context is all you need" is the central design principle: polluted context degrades agent reasoning and causes repeated failures.
- The bottom-line quality bar is strict: no fake information, every conclusion has a source, methods correspond to implemented code, results come from real runs, and a reader can reproduce the experiment from the paper description and code.
- Baseline selection and reproduction are not optional. They create the anchor needed to judge whether an idea actually works.
- For benchmark/pivot paper selection, open-source code is close to a hard requirement. A paper without usable code may still be useful survey context, but it is usually not a practical baseline for getting deep-learning research done.
- Idea generation and idea review should be isolated across models and sessions. A reviewer should not inherit the messy history of brainstormed or rejected ideas.
- Prior-paper experiment designs should inform later decisions, but our experiment design is a separate artifact created when we decide what experiment to run, how to modify the benchmark, and what evidence is needed.
- Results should feed back into new research, rather than being treated only as validation of the original idea.
- Implementation and experiment execution must be monitored for early failures such as process crashes, stalled downloads, low GPU usage, NaN loss, and clearly hopeless training signals.
- The automation-heavy pieces are mainly engineering: CPU/GPU utilization, NaN detection, process health, dataset/path verification, benchmark modification, run tracking, artifact capture, and other lessons learned through real "skin in the game."
- The implementation target is the agent harness itself: hooks, workflow, skills, and agent definitions should carry the research process rather than leaving it as an informal chat convention.
- The system needs evolution ability. It should not try to encode every future problem into the main workflow, but it should record real problems at session finish so later tasks can evolve the harness from evidence.
- MVP order is confirmed: first implement workflow/hooks for session state and evolution notes, then add the survey extraction skill.
- The survey system should be able to delegate survey/scout/extraction tasks to Gemini and Antigravity agents when those CLIs are available.
- Existing repo specs already include research safety constraints for host, GPU, venv, datasets, checkpoints, and large downloads.
- Existing archived harness work already uses gates with preconditions, commands, expected artifacts, success criteria, and failure diagnosis instructions.

## Assumptions (Temporary)

- The first useful deliverable is a design/spec for the research system, not production code yet.
- The research system should build on the existing Trellis task/spec/journal structure instead of inventing a totally separate workflow engine.
- The first MVP should focus on correctness, context hygiene, and reproducibility rather than full autonomy.
- Multi-model usage should be explicit by role: search/scout, idea generator, strict reviewer, architect/decider, implementer, experiment monitor, and claim auditor.

## Requirements (Evolving)

- The system must have hard phase boundaries: survey/idea, contract, implementation/experiment, analysis/paper.
- The system must distinguish automatable engineering work from human-judgment checkpoints.
- The survey artifact must be human-readable and evidence-grounded, not just an agent-private memory dump.
- The survey phase must maintain a file-backed paper/code/source registry so later agents can trace where claims, methods, and benchmark decisions came from.
- The paper registry must preserve detailed extraction fields for idea, method, experiment setup, datasets, metrics, ablations, and implementation availability, even when the human-readable survey only summarizes the decision-relevant parts.
- The system must treat the research contract as the primary handoff from idea to code.
- The research contract must preserve correspondence across the whole research chain: sources, prior claims, benchmark behavior, proposed method changes, experiment design, generated code, metrics, plots, result analysis, and final paper claims.
- The system must record evidence as files, not just chat: paper source summaries, idea cards, baseline records, experiment configs, logs, metrics, plots, arrays, and claim mappings.
- The system must classify papers by role: broad survey context, related-work evidence, possible pivot/baseline, experiment-critical reference, and rejected/archived candidate.
- The system must isolate noisy work from the main context: search sweeps, installs, downloads, reproduction attempts, long-running experiments, and model reviews should run in bounded sessions or subprocesses.
- The system must include a source policy for survey work: prefer paper source/LaTeX/Markdown when available; avoid trusting partial PDF skim as full-paper understanding.
- The system must strongly prefer benchmark papers with usable open-source code, reproducible configs, and realistic data/checkpoint access.
- The system must include an idea novelty review that distinguishes "strictly already studied" from "too close to be useful" from "incrementally viable for a top-conference-style contribution."
- The system must include implementation gates that verify baseline reproduction before idea implementation.
- The system must include experiment health monitoring and early-stop/escalation rules.
- The system must treat experiment results as inputs for the next research loop, including negative results and surprising intermediate findings.
- The system must include a claim audit before paper writing: every claim maps to a source or a produced experiment artifact.
- The implementation must map the research process onto hooks, workflow steps, reusable skills, and agent roles.
- Finish-work/session wrap-up must record operational problems and improvement opportunities without forcing every issue into the main system immediately.
- Survey delegation must support at least local Codex execution plus optional Gemini CLI and Antigravity CLI backends.

## Automation vs Human Judgment

The system should automate the parts where machines are clearly better or more reliable:

- Broad paper search and source retrieval
- LaTeX/Markdown extraction and section-level summarization
- Benchmark setup, run orchestration, and artifact capture
- CPU/GPU/process monitoring
- NaN, crash, stall, and low-utilization detection
- Config, commit, metric, plot, array, and log bookkeeping
- Reproducibility checks and claim-to-evidence tracing

The system should force human interaction where judgment is essential:

- Deciding whether a research theme is worth pursuing
- Judging whether a proposed idea is actually interesting
- Deciding whether novelty is sufficient despite related work
- Choosing whether a negative or ambiguous result opens a better research direction
- Approving expensive or risky compute/data/checkpoint actions

The survey is therefore not just an intermediate model context. It is a human-facing artifact designed to support judgment.

## Implementation Surfaces

The research system should be implemented through four harness surfaces:

- Hooks: inject current research state, detect active tasks/runs, remind agents about safety gates, and collect session-end observations.
- Workflow: define the phase order and gate transitions from survey to idea to contract to benchmark modification to experiment to analysis.
- Skills: encode repeatable procedures such as paper extraction, survey synthesis, idea review, research contract creation, benchmark selection, experiment design, experiment monitoring, and claim audit.
- Agents: provide isolated roles such as scout/searcher, survey extractor, idea generator, idea reviewer, architect/decider, implementer, experiment runner, monitor, and claim auditor.

The main thread should act as a scheduler and decision surface. Noisy or bounded work should be delegated to agents, subprocesses, or tmux/session runners with file-based handoff artifacts.

For survey work, Gemini and Antigravity should be treated as optional execution backends:

- Gemini: useful for broad search/scout and source discovery when available.
- Antigravity: useful as another autonomous CLI backend, especially if installed and able to run non-interactive `agy --print` prompts.
- Codex/local: fallback path when external agent CLIs fail or are not configured.

Delegation failures should not disappear into chat. They should be recorded in the evolution backlog with command shape, stderr/stdout summary, likely cause, and next diagnostic.

## Evolution Loop

The first version should stay lean. Instead of trying to predict every failure mode, each session finish should record problems that appeared during real work.

Examples:

- Gemini or another agent could not be called.
- Internet, proxy, paper download, dataset download, or code clone failed.
- A source could not be parsed from PDF/LaTeX/Markdown.
- A benchmark repository could not be installed or reproduced.
- GPU/CPU utilization, NaN loss, dead process, or stalled run created an operational issue.
- Agent handoff context was missing, noisy, stale, or misleading.

These observations should become an evolution backlog, not automatic main-workflow complexity. Later tasks can promote repeated or high-impact problems into new hooks, workflow gates, skills, agent prompts, or specs.

## Survey Evidence Store

The survey phase should produce two linked artifacts:

- A human-readable survey report that summarizes the research landscape, key ideas, method families, experiment patterns, open questions, and why a theme or idea may be worth pursuing.
- A machine-readable/file-backed evidence store that records the concrete sources behind the report.

The detailed extraction belongs in the evidence store. The human-readable survey should be selective: enough for a human to judge direction and idea quality, not a full reconstruction of every paper.

Proposed folder model:

```text
survey/
  papers/
    <paper-id>/
      metadata.yaml        # title, authors, venue, year, arXiv/OpenReview/DOI links
      source.md            # extracted LaTeX/Markdown notes or section map when available
      code.md              # repo link, commit/release info, license, install notes
      extraction.md         # idea, method, experiment design, dataset, metrics, ablations
      summary.md           # concise human-readable summary
      relevance.md         # why it matters for this project; role classification
  reports/
    survey.md              # human-readable synthesis for judgment
  shortlists/
    experiment-<name>.md   # papers promoted into a specific experiment branch
```

The broad survey should remain intact, while experiment branches can promote a smaller set of papers into a shortlist or archive of directly relevant references. This keeps exploration broad without polluting the implementation context.

## Experiment Design Boundary

The survey can record how other papers designed experiments, but it should not pretend to decide our experiment in advance. Our experiment design happens after a theme, idea, and benchmark candidate are selected.

The experiment design artifact should answer:

- What exact question are we testing?
- Which benchmark/codebase are we modifying?
- Which prior paper designs or ablations are we borrowing from?
- What is the minimal change from the baseline?
- Which metrics, datasets, splits, and compute settings are fixed?
- What result would support the idea?
- What result would falsify or weaken the idea?
- What artifacts must be produced so the result can become new research evidence?

## Benchmark Selection Rule

A paper can influence ideas without being runnable, but a benchmark/pivot paper should normally satisfy:

- Public code exists.
- Code is installable or at least auditable.
- Dataset/checkpoint requirements are known.
- Metrics and evaluation protocol are clear.
- The implementation can be modified without rewriting the whole system from scratch.

If no open-source code exists, the default status is "survey/reference only," not "baseline candidate."

## Proposed Core Architecture

The first architectural decision is to put a versioned research contract at the center:

```text
Human-readable survey + baseline context
        |
        v
Idea cards + independent reviews
        |
        v
Research contract v1
        |
        v
Benchmark modification + monitored experiments
        |
        v
Evidence ledger
        |
        v
Result analysis + next research loop + paper claims
```

The research contract should include:

- Hypothesis
- Baseline and exact baseline commit/config
- Method delta from baseline
- Source/reference/claim correspondence
- Benchmark modification plan
- Dataset, split, metric, and compute assumptions
- Required ablations
- Success signals
- Failure signals, written independently from success
- Allowed implementation degrees of freedom
- Disallowed changes without contract v2
- Required artifacts
- Claim mapping template

## Research References

- `research/local-context.md` - Local repo and pasted-note findings that shape the initial architecture.

## Open Questions

- Should the first concrete implementation target be the survey/paper-extraction skill, or the workflow/hook scaffolding that makes research sessions record state and evolution notes?

## Acceptance Criteria (Evolving)

- [x] We define the MVP scope of the research system.
- [x] We specify the survey/idea phase artifacts and handoff rules.
- [ ] We specify the research contract schema and versioning rules.
- [ ] We specify the implementation/experiment phase gates and monitoring rules.
- [ ] We specify how final paper claims are audited against sources and experiment artifacts.
- [x] We identify which parts should become Trellis specs, task templates, scripts, or agent prompts.
- [x] We specify which hooks, workflow steps, skills, and agents are needed for the MVP.
- [x] We specify how session-end problem records feed an evolution backlog.

## Implementation Notes

- Added `.trellis/spec/research-system.md` as the research-system contract.
- Added `.trellis/scripts/research_survey.py` for survey folder initialization, per-paper templates, Gemini/Antigravity/local survey delegation, and evolution problem recording.
- Added `trellis-research-survey` skill entries for shared Codex/Gemini-compatible skills and Antigravity skills.
- Added `trellis-survey` agent definitions for Codex and Gemini.
- Updated workflow, start, and finish-work entry points so survey work routes to the new skill and finish-work records evolution notes.
- Updated Codex/Gemini per-turn hooks to surface task-local survey/evolution artifacts only when they exist.
- Fixed the local Gemini delegate shell parse failure and corrected Gemini CLI adapter command shape to use headless `-p`.

## Definition of Done (Team Quality Bar)

- Tests added/updated if implementation begins.
- Lint/typecheck/CI green if code changes are made.
- Docs or specs updated if workflow behavior changes.
- Rollout/rollback considered if workflow automation becomes risky.

## Out of Scope (Explicit)

- Full autonomous paper generation.
- Running GPU experiments during this planning phase.
- Downloading datasets, checkpoints, or large paper corpora.
- Choosing a specific deep-learning research topic unless the user wants this task to include a concrete pilot.
- Fixing Gemini delegation unless we decide it is part of the research-system MVP.

## Technical Notes

- Active task: `.trellis/tasks/06-01-research-system-architecture`.
- Existing relevant specs: `.trellis/spec/research-safety.md`, `.trellis/spec/repo-structure.md`, `.trellis/spec/agent-collaboration.md`, `.trellis/spec/trellis_harness/meta/index.md`.
- Existing related artifact: `archive/provisional_research_harness/configs/task_arti6_linearvc.yaml`.
- Gemini worker delegation is currently blocked: `~/.gemini/extensions/superpowers/skills/delegate-to-gemini/delegate.sh` is missing, and `.trellis/scripts/delegate_to_gemini.sh` fails with a shell parse error.
- Local CLI check: `agy` exists at `/Users/bowen/.local/bin/agy`; `gemini` exists at `/opt/homebrew/bin/gemini`.
- Antigravity help confirms non-interactive print mode: `agy --print`, with optional `--conversation` and `--dangerously-skip-permissions`.
- Gemini help confirms non-interactive headless mode should use `gemini -p/--prompt`; the current `CLIAdapter("gemini").build_run_command(...)` returns a positional prompt, which may start interactive mode instead of headless mode.
