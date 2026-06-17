# Local Context: Research System Architecture

## Sources Inspected

- `/Users/bowen/.codex/attachments/a0bcb556-5d82-4b07-bdc3-13118300f23f/pasted-text.txt`
- `.trellis/spec/research-safety.md`
- `.trellis/spec/repo-structure.md`
- `.trellis/spec/agent-collaboration.md`
- `.trellis/spec/trellis_harness/meta/index.md`
- `archive/research_notes/00_trellis_audit.md`
- `archive/research_notes/04_experiment_design.md`
- `archive/research_notes/06_risk_register.md`
- `archive/provisional_research_harness/configs/task_arti6_linearvc.yaml`
- `survey_report.md`

## Prior Work That Matters

- Trellis is already positioned as the repo's workflow and memory layer, but prior audits say it is not enough by itself for research execution. It needs research-specific gates, safety policies, and artifact conventions.
- Existing research safety rules already forbid assuming host, GPU, CUDA, datasets, checkpoints, or lab paths without verification.
- Existing experiment design work for ARTI-6/LinearVC uses gated execution, explicit ablations, required artifacts, saved arrays, diagnostics, and GO/PARTIAL GO/BLOCKED statuses.
- The provisional harness YAML already models research as gates with preconditions, commands, artifacts, success criteria, and failure diagnosis instructions.
- The pasted notes define the core philosophical constraints: context is the central resource; no fake information; every conclusion needs a source; ideas, methods, code, results, and claims must correspond exactly.

## Reusable Principles

- Context isolation is a first-class design goal. The main scheduler should not absorb noisy install logs, failed downloads, raw paper dumps, or long-running experiment output.
- Survey is not "read many PDFs." It is building a source-grounded expert context for later idea generation.
- Idea generation and idea review should be isolated. A reviewer should evaluate one idea against the baseline and evidence, not against the entire messy brainstorming history.
- Baseline reproduction is mandatory before idea implementation. It is the experimental anchor for all later claims.
- A research contract should sit between idea selection and implementation. It defines hypothesis, success signals, failure signals, metrics, data splits, ablations, and allowed deviations before results exist.
- Execution must be monitored. A process that started is not the same as a process that is healthy.
- Claims should be generated only from actual artifacts: code, configs, logs, metrics, plots, saved arrays, and source references.

## Tooling Risks Found

- The `AGENTS.md` Gemini delegation path does not exist on this machine.
- The project-local `.trellis/scripts/delegate_to_gemini.sh` currently fails with a shell parsing error before reaching Gemini.
- Existing safety rules are procedural rather than fully enforced. The future system should encode gates as machine-readable contracts where possible.

## Design Implication

The most important part of the system is the boundary object between thinking and execution: a versioned research contract plus evidence ledger. Without that, survey, idea generation, code, experiments, and paper writing will collapse into a narrative-producing loop that can rationalize anything after the fact.
