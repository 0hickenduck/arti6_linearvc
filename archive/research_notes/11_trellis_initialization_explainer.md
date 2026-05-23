# Trellis Initialization Explainer

Status: GO

Scope: local source audit of `external/trellis/`. No `trellis init` was run. No dependencies, models, checkpoints, or datasets were installed or downloaded.

## Evidence Sources

| Source | What it verified |
|---|---|
| `external/trellis/README.md` | Trellis purpose, prerequisites, quick-start install/init commands, multi-platform claim, `.trellis/spec`, `.trellis/tasks`, `.trellis/workspace`. |
| `external/trellis/.trellis/workflow.md` | Runtime task/spec/workspace model, developer identity, task lifecycle scripts, workflow state, sub-agent protocol, Codex and Gemini listed in workflow routing. |
| `external/trellis/packages/cli/package.json` | npm package name `@mindfoldhq/trellis`, binary names `trellis` and `tl`, Node engine `>=18.17.0`, package dependencies. |
| `external/trellis/packages/cli/src/cli/index.ts` | `trellis init` command flags, including `--codex` and `--gemini`. |
| `external/trellis/packages/cli/src/commands/init.ts` | What init does: Python check, project detection, workflow creation, platform configuration, root `AGENTS.md`, template hashes, developer identity, bootstrap/joiner task creation, optional template network fetch. |
| `external/trellis/packages/cli/src/configurators/workflow.ts` | `.trellis/` core files/directories created by init. |
| `external/trellis/packages/cli/src/configurators/codex.ts` | Codex adapter files: `.agents/skills`, `.codex/skills`, `.codex/agents`, `.codex/hooks`, `.codex/hooks.json`, `.codex/config.toml`. |
| `external/trellis/packages/cli/src/configurators/gemini.ts` | Gemini adapter files: `.gemini/commands/trellis`, `.agents/skills`, `.gemini/agents`, `.gemini/hooks`, `.gemini/settings.json`. |
| `external/trellis/packages/cli/src/types/ai-tools.ts` | Supported AI tools and per-agent metadata; Gemini CLI is directly supported. |
| `external/trellis/packages/cli/src/templates/shared-hooks/index.ts` | Which hook scripts each platform receives. |
| `external/trellis/packages/cli/src/utils/file-writer.ts` | Conflict behavior: ask, force, skip, append; non-TTY defaults to skip on conflicts. |

## 1. What Does "Initialize Trellis" Mean?

Trellis initialization means running the already-installed Trellis CLI in a project root so it writes Trellis workflow files and selected agent adapter files into that project.

It is distinct from installing the CLI. The README quick start has two separate steps:

```bash
npm install -g @mindfoldhq/trellis@latest
trellis init -u your-name
```

### What Initialization Does

| Question | Answer | Evidence |
|---|---|---|
| Installs global CLI tools? | No. Global CLI installation is the preceding `npm install -g @mindfoldhq/trellis@latest` step. | README quick start separates install from init; package metadata exposes `trellis` and `tl` binaries. |
| Creates project-local files? | Yes. Init writes `.trellis/`, selected agent directories, and root `AGENTS.md` if not already present or if overwrite/append is chosen. | `commands/init.ts`, `configurators/workflow.ts`, platform configurators. |
| Creates `.trellis/`? | Yes. It creates workflow scripts, config, workflow guide, workspace index, tasks dir, spec templates, `.version`, `.template-hashes.json`, and optionally bootstrap/joiner task files. | `createWorkflowStructure()` in `configurators/workflow.ts`; `commands/init.ts`. |
| Creates `.agents/`? | Yes for platforms that support shared Agent Skills, including Codex and Gemini. | `configureCodex()` and `configureGemini()` both write `.agents/skills/`. |
| Creates `.codex/`? | Yes if `--codex` is selected. | `configureCodex()` writes `.codex/skills`, `.codex/agents`, `.codex/hooks`, `.codex/hooks.json`, `.codex/config.toml`. |
| Creates other agent-specific files? | Yes, depending on selected flags. Gemini creates `.gemini/`; Claude creates `.claude/`; Cursor creates `.cursor/`; etc. | `cli/index.ts` flags and `types/ai-tools.ts` registry. |
| Modifies existing files? | It can. Existing file conflicts are handled by prompt, `--force`, `--skip-existing`, `--append`, or non-TTY skip behavior. Root `AGENTS.md` is a known possible conflict. | `file-writer.ts`; `createRootFiles()` in `commands/init.ts`. |
| Starts a background service? | No evidence found. Init writes files and runs short scripts/commands; no daemon/service startup was found in inspected source. | `commands/init.ts`; workflow/configurator source. |
| Downloads dependencies? | Not in the normal project init path. The CLI must already be installed. However, interactive init may fetch a remote spec-template index, and `--template`/`--registry` can download spec templates. | `commands/init.ts` template selection/download logic. |
| Downloads models or datasets? | No evidence. Trellis is a coding-agent workflow scaffold, not an ML runner. | README and init/configurator source. |

## 2. What Files/Directories Would Trellis Init Create?

Exact files depend on selected flags, write mode, project type, and whether existing files conflict. The likely layout for this project is below.

### A. Agent-Neutral Trellis Core

| File/directory | Purpose |
|---|---|
| `.trellis/` | Project-local Trellis workflow root. |
| `.trellis/workflow.md` | Canonical workflow guide, phase rules, state breadcrumbs, task routing. |
| `.trellis/config.yaml` | Project settings: journal rotation, task lifecycle hooks, monorepo packages, Codex dispatch mode. |
| `.trellis/scripts/` | Local Python scripts such as `task.py`, `get_context.py`, `init_developer.py`, `add_session.py`. |
| `.trellis/spec/` | Project rules and reusable specs injected into tasks/agents. |
| `.trellis/spec/guides/` | General Trellis thinking guides. |
| `.trellis/tasks/` | Trellis task storage. Each task uses `prd.md`, `task.json`, `implement.jsonl`, `check.jsonl`, optional `research/`. |
| `.trellis/tasks/00-bootstrap-guidelines/` | First-init task created when init has a developer name and tasks are empty. It asks the AI to populate real project specs. |
| `.trellis/workspace/index.md` | Workspace index. |
| `.trellis/.gitignore` | Ignores local runtime/developer state inside `.trellis/`. |
| `.trellis/.version` | Trellis project template version for update checks. |
| `.trellis/.template-hashes.json` | Tracks Trellis-owned generated files for updates. |
| `AGENTS.md` | Root agent instructions from Trellis template if written. Existing `AGENTS.md` may be skipped, appended, or overwritten depending on mode. |

### B. Codex-Specific Adapter Files

Created only when `--codex` is selected.

| File/directory | Purpose |
|---|---|
| `.agents/skills/` | Shared Agent Skills. Codex writes Trellis workflow skills here; Gemini CLI 0.40+ also reads this workspace alias according to source comments. |
| `.agents/skills/trellis-start/SKILL.md` | Codex-specific start skill used as fallback because Codex SessionStart behavior differs. |
| `.codex/skills/` | Codex-specific Trellis skills. |
| `.codex/agents/trellis-implement.toml` | Codex implement sub-agent definition. |
| `.codex/agents/trellis-check.toml` | Codex check sub-agent definition. |
| `.codex/agents/trellis-research.toml` | Codex research sub-agent definition. |
| `.codex/hooks/session-start.py` | Codex-specific session-start hook template. |
| `.codex/hooks/inject-workflow-state.py` | Shared workflow-state hook distributed for Codex. |
| `.codex/hooks.json` | Codex hook registration for `UserPromptSubmit`. |
| `.codex/config.toml` | Project-scoped Codex defaults, including `project_doc_fallback_filenames = ["AGENTS.md"]` and `features.multi_agent_v2`. |

Important Codex caveat: `configureCodex()` says Codex hooks also require user-level `~/.codex/config.toml` feature flags and a one-time `/hooks` review on Codex 0.129+.

### C. Other Agent-Specific Adapter Files

Created only for selected platforms.

| Platform | Likely files/directories | Notes |
|---|---|---|
| Gemini CLI | `.gemini/commands/trellis/*.toml`, `.gemini/agents/*.md`, `.gemini/hooks/*.py`, `.gemini/settings.json`, shared `.agents/skills/` | Directly supported by `--gemini`. |
| Claude Code | `.claude/commands/trellis/*.md`, `.claude/skills/`, `.claude/agents/*.md`, `.claude/hooks/`, `.claude/settings.json` | Default-checked in interactive init. |
| Cursor | `.cursor/commands/`, `.cursor/skills/`, `.cursor/agents/`, `.cursor/hooks/`, `.cursor/hooks.json` | Default-checked in interactive init. |
| OpenCode | `.opencode/` plugin/agent files | Supported by `--opencode`. |
| Other supported tools | `.kilocode/`, `.kiro/`, `.agent/`, `.windsurf/`, `.qoder/`, `.codebuddy/`, `.github/copilot/`, `.factory/`, `.pi/` | Listed in `types/ai-tools.ts` and `cli/index.ts`. |

### D. User/Project State Files

| File/directory | Purpose |
|---|---|
| `.trellis/.developer` | Local developer identity. Workflow doc says it is gitignored. |
| `.trellis/workspace/<developer>/` | Per-developer workspace journal. |
| `.trellis/workspace/<developer>/journal-N.md` | Session log files, rotated around 2000 lines by default. |
| `.trellis/workspace/<developer>/index.md` | Per-developer journal index. |
| `.trellis/.runtime/sessions/` | Runtime active-task pointers. Workflow doc says active task state is stored here. |
| `.trellis/tasks/<task>/task.json` | Task metadata and status. |
| `.trellis/tasks/<task>/prd.md` | Task requirement/source-of-truth document. |
| `.trellis/tasks/<task>/implement.jsonl` | Context manifest for implementation agents. |
| `.trellis/tasks/<task>/check.jsonl` | Context manifest for checking agents. |

### E. Hooks/Scripts/Checks

| File/directory | Purpose |
|---|---|
| `.trellis/scripts/task.py` | Task lifecycle: create/start/current/finish/archive/list/context management. |
| `.trellis/scripts/get_context.py` | Loads session context, package/spec context, and phase guidance. |
| `.trellis/scripts/init_developer.py` | Creates developer identity/workspace. |
| `.trellis/scripts/add_session.py` | Records session summaries into journals. |
| `.codex/hooks/*.py` | Codex hook scripts if Codex adapter is enabled. |
| `.gemini/hooks/*.py` | Gemini hook scripts if Gemini adapter is enabled. |
| `.trellis/config.yaml` lifecycle hooks | Optional user-configured shell hooks after task create/start/finish/archive. Template comments say hook failures warn but do not block. |

## 3. Is Initialization CLI-Specific?

Initialization has two layers:

1. Shared Trellis core: `.trellis/`, task/spec/workspace state, scripts, project rules.
2. Per-agent adapters: `.codex/`, `.gemini/`, `.claude/`, `.cursor/`, etc.

If you run Trellis init for Codex only, the shared `.trellis/` core benefits the project, and `.agents/skills/` may be partially useful to Gemini CLI 0.40+ because Codex writes shared Agent Skills there. But Codex-only init does not create Gemini slash commands, Gemini agents, Gemini hooks, or `.gemini/settings.json`.

If you also want Gemini CLI, use the Gemini flag later or in the same init:

```bash
trellis init --gemini -u bowen
```

or:

```bash
trellis init --codex --gemini -u bowen
```

Trellis does support Gemini CLI directly. Evidence:

- `cli/index.ts` defines `.option("--gemini", "Include Gemini CLI commands")`.
- `types/ai-tools.ts` has a `gemini` registry entry with `name: "Gemini CLI"`, `configDir: ".gemini"`, `supportsAgentSkills: true`, `hasPythonHooks: true`, and `agentCapable: true`.
- `configurators/gemini.ts` writes `.gemini/commands/trellis`, `.agents/skills`, `.gemini/agents`, `.gemini/hooks`, and `.gemini/settings.json`.

Minimal manual Gemini-compatible files are only needed if we choose not to run official `--gemini`. The minimum would be:

- `GEMINI.md` or equivalent root instruction file pointing Gemini to `.trellis/workflow.md`, `.trellis/tasks/`, `.trellis/spec/`, `AGENTS.md`, and the safety policy.
- `.gemini/commands/trellis/*.toml` for start/continue/finish if Gemini slash commands are desired.
- `.gemini/settings.json` and `.gemini/hooks/*.py` only if we explicitly want hook-based context injection.
- `.agents/skills/` if using Gemini CLI versions that read workspace Agent Skills.

## 4. Can One Trellis Initialization Support All CLI Agents?

Yes, architecturally. Trellis is designed as:

- one shared, agent-neutral core in `.trellis/`
- thin per-agent adapters for each CLI/IDE
- shared `.agents/skills/` where supported
- one task/spec/workspace source of truth
- per-platform hooks/settings/commands only for integration glue

The best architecture for this project is:

| Layer | Source of truth | Notes |
|---|---|---|
| Project rules | `.trellis/spec/` plus root `AGENTS.md` safety summary | Avoid contradictory rules across adapters. |
| Task state | `.trellis/tasks/<task>/task.json` and `prd.md` | Do not duplicate task truth in both Trellis and custom YAML long term. |
| Research notes | `.trellis/tasks/<task>/research/` for task-local notes; optionally keep `research_notes/` as archival source material | Current markdown notes can seed task research. |
| Developer journals | `.trellis/workspace/<developer>/` | Portable and per-developer. |
| Codex adapter | `.codex/` and `.agents/skills/` | Codex-specific config/hook/agent files. |
| Gemini adapter | `.gemini/` and `.agents/skills/` | Gemini-specific commands/hooks/agents. |

The key rule is no duplicated research task state. Codex and Gemini should both read/write the same `.trellis/tasks/` and `.trellis/spec/` artifacts.

## 5. Minimal Safe Initialization For This Use Case

Your constraints:

- local disposable workspace, not the lab server
- no model/dataset downloads
- no ARTI-6 run
- portable, mostly agent-neutral harness
- likely use Codex and Gemini CLI
- GO / PARTIAL GO / BLOCKED status
- human approval before large downloads
- no unnecessary runtime magic

Recommended minimum:

1. Use the shared Trellis core as the source of truth.
2. Enable Codex and Gemini adapters together, but use skip-existing mode to protect current `AGENTS.md`.
3. Immediately add research-specific Trellis specs for:
   - no large downloads without human approval
   - no model/checkpoint downloads without human approval
   - no dataset downloads without human approval
   - no lab-server assumptions
   - GO / PARTIAL GO / BLOCKED status format
   - exact failure reporting format
4. Keep `.trellis/config.yaml` conservative:
   - do not add lifecycle shell hooks yet
   - consider setting `session_auto_commit: false` after init if auto-committing journals/tasks is unwanted
   - keep Codex dispatch mode inline unless sub-agent behavior is explicitly desired
5. Migrate current notes into one Trellis planning task before further implementation.

This gives shared rules, task/spec tracking, journals, Codex compatibility, Gemini compatibility, and minimal heavy runtime behavior. It does not download ML artifacts.

## 6. Exact Commands Needed Later

Do not execute these yet.

### Option A: Trellis Official Full Init

Command:

```bash
npm install -g @mindfoldhq/trellis@latest
trellis init -u bowen
```

What it creates:

- `.trellis/` shared core
- default selected platform adapters in interactive mode or with `-y`; source shows default-checked tools are Claude Code and Cursor, not Codex/Gemini
- root `AGENTS.md` if allowed
- developer identity and bootstrap task

Pros:

- Most official path.
- Lets Trellis choose defaults interactively.
- Good for teams already using default-supported platforms.

Cons:

- Installs global npm CLI.
- Interactive init may fetch remote template index.
- Default platform choices may create unwanted `.claude/` and `.cursor/`.
- Does not necessarily configure Codex/Gemini unless selected.

Codex support: only if selected interactively or `--codex` is added.

Gemini support: only if selected interactively or `--gemini` is added.

Recommended for this project: No. Too broad for a clean research workspace.

### Option B: Trellis Minimal Codex Init

Command:

```bash
npm install -g @mindfoldhq/trellis@latest
trellis init --codex --skip-existing -u bowen
```

What it creates:

- `.trellis/` shared core
- `.agents/skills/`
- `.codex/`
- developer identity and bootstrap task
- skips existing conflicting files such as current `AGENTS.md`

Pros:

- Clean Codex setup.
- Avoids default Claude/Cursor adapters.
- Protects existing safety files with `--skip-existing`.
- Creates the Trellis task/spec/workspace core.

Cons:

- Gemini does not get `.gemini/` commands/hooks/agents.
- Codex hook behavior requires user-level Codex hook enablement and one-time `/hooks` review.
- Still installs global npm CLI first.

Codex support: Yes.

Gemini support: Partial only through shared `.agents/skills/`; not full Gemini CLI integration.

Recommended for this project: Acceptable if we will only use Codex first, but not ideal if Gemini CLI is expected soon.

### Option C: Trellis Multi-Agent Init If Supported

Command:

```bash
npm install -g @mindfoldhq/trellis@latest
trellis init --codex --gemini --skip-existing -u bowen
```

What it creates:

- `.trellis/` shared core
- `.agents/skills/` shared skills
- `.codex/` adapter
- `.gemini/` adapter
- developer identity and bootstrap task
- skips existing conflicting files such as current `AGENTS.md`

Pros:

- Best match to Codex + Gemini use.
- One shared Trellis task/spec/workspace core.
- No duplicated research task state.
- Avoids default Claude/Cursor clutter.
- Gemini CLI is directly supported by local source.

Cons:

- Installs global npm CLI first.
- Creates both `.codex/` and `.gemini/` adapter directories.
- Hooks may do more context injection than desired unless reviewed.
- We still need to add research-specific safety specs.

Codex support: Yes.

Gemini support: Yes.

Recommended for this project: Yes, when ready to run official Trellis init.

### Option D: Manual Minimal Trellis-Compatible Structure Without Running Init

Command:

```bash
mkdir -p .trellis/spec/research .trellis/tasks .trellis/workspace .trellis/scripts
mkdir -p .agents/skills
```

Then manually create:

```text
.trellis/workflow.md
.trellis/config.yaml
.trellis/spec/research/safety.md
.trellis/spec/research/status.md
.trellis/tasks/<task>/prd.md
.trellis/tasks/<task>/task.json
.trellis/tasks/<task>/research/
GEMINI.md
```

What it creates:

- A Trellis-inspired file layout, but not an official initialized Trellis project.
- No generated hooks, adapters, scripts, template hashes, version file, or official task script support unless copied manually.

Pros:

- No global install.
- No remote template checks.
- Maximum control and least magic.
- Easy to keep small and research-specific.

Cons:

- Not actually official Trellis initialization.
- Easy to drift from Trellis schema.
- No official update path.
- Would recreate parts of a custom harness, which we are trying to avoid.

Codex support: Manual only through `AGENTS.md`/`.agents/skills` if added.

Gemini support: Manual only through `GEMINI.md`/`.gemini` if added.

Recommended for this project: No, unless we decide not to trust official init behavior.

## 7. Risks

| Risk | Why it matters | Mitigation |
|---|---|---|
| Repo clutter from agent-specific files | Multi-agent init creates `.codex/`, `.gemini/`, `.agents/skills/`, and possibly more if broad flags are used. | Use explicit `--codex --gemini`; avoid default interactive selections. |
| Codex-only config does not fully help Gemini | Codex init creates `.codex/`; Gemini still needs `.gemini/commands`, `.gemini/hooks`, `.gemini/agents`, `.gemini/settings.json` for full support. | Use `--codex --gemini` together or add `--gemini` later. |
| Hooks doing more than expected | Hook configs inject workflow state/session context. Codex needs separate user-level hook enablement and review. Gemini settings also register hooks. | Inspect generated hook files before enabling/approving hooks; keep lifecycle hooks empty in `.trellis/config.yaml`. |
| Dependency installation | Official CLI install uses npm and installs package dependencies such as `commander`, `inquirer`, `figlet`, `giget`, `undici`. | Install only after approval; pin or record version; do not install GPU/ML packages. |
| Template network fetch | Interactive init may fetch a template index and selected templates can download spec templates. | Use explicit platform flags plus `--skip-existing`; avoid `--template` and `--registry`; consider `-y` only if defaults are understood, but do not use no-flags `-y` because it defaults to Claude/Cursor. |
| Conflicting instructions | Root `AGENTS.md`, future `GEMINI.md`, `.codex/config.toml`, `.agents/skills`, and `.trellis/spec` can disagree. | Make `.trellis/spec/research/` the detailed source and keep root agent files as short pointers plus hard safety rules. |
| Losing portability to lab server | Agent-specific files may assume local paths or local Python command. | Keep all paths relative; avoid lab paths until verified; record Python command and Trellis version; do not encode local cache paths except under project-relative directories. |
| Auto-commit behavior | `.trellis/config.yaml` template says session/task archive scripts may auto-stage/auto-commit by default unless configured false. | Review and possibly set `session_auto_commit: false` immediately after init. |
| Existing `AGENTS.md` conflict | Trellis may try to write root `AGENTS.md`. | Use `--skip-existing`; manually reconcile later. |

## 8. Recommendation

Recommendation: A. Run official Trellis init now.

Use the official init path, but do not use broad interactive defaults. For this project, "official init" should mean the narrow multi-agent command from Option C:

```bash
trellis init --codex --gemini --skip-existing -u bowen
```

Reasoning:

- Trellis source confirms direct Gemini CLI support. A manual Gemini adapter is unnecessary unless official `--gemini` fails.
- Explicit `--codex --gemini` creates one shared `.trellis/` core with thin Codex and Gemini adapters.
- `--skip-existing` protects the current `AGENTS.md` and other safety files.
- This avoids default interactive selections that may create unwanted Claude/Cursor files.
- It keeps task/spec/workspace state unified instead of creating a parallel custom harness.

If you decide Gemini CLI is not needed yet, use Option B instead. But based on the stated possibility of using both Codex and Gemini, Option C is the best concrete command under the final recommendation "A. Run official Trellis init now."

## Exact Next Prompt If You Accept

Use this prompt:

```text
Initialize Trellis officially with only Codex and Gemini adapters.

Do not download models or datasets.
Do not run ARTI-6.
Do not install heavyweight packages.
Do not use sudo.
Use the installed/available Trellis CLI only if present; if it is not installed, stop and report the exact missing-command error instead of installing it.

Run:
trellis init --codex --gemini --skip-existing -u bowen

Then inspect the generated files before enabling any hooks.
Update PROJECT_STATE.json and create a short report:
research_notes/12_trellis_init_result.md

Final status must be GO / PARTIAL GO / BLOCKED.
```

## Final Status

GO: initialization plan is clear
