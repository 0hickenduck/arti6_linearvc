# [UNFINISHED] Add Gemini agent routing to harness

## Status Note
This task is being archived as **UNFINISHED** per user request on 2026-05-23. The logic for Gemini agent routing has not been fully implemented in the harness.

## Goal

Add a pragmatic first Gemini integration pass to the Trellis harness: make Gemini an actually usable CLI-agent backend where the harness already knows how to launch it, give Gemini's Trellis agents sensible role-specific model routing, and keep the source templates plus this repo's generated harness aligned.

## What I already know

* The implementation target is `external/trellis/`, especially `packages/cli/`, plus this repo's generated Trellis files that mirror those templates locally.
* Codex and Gemini are both already marked `agentCapable: true`; both ship `trellis-implement`, `trellis-check`, and `trellis-research` definitions.
* `CLIAdapter.build_run_command()` already has a Gemini launch branch, but `supports_cli_agents` still excludes Gemini.
* Gemini CLI supports per-agent model routing; research can use a cheaper/faster model while implementation/check use a stronger model.
* Codex and Gemini already share a pull-based sub-agent context strategy through `applyPullBasedPrelude*()` in `packages/cli/src/configurators/shared.ts`.
* I could not find `/tmp/trellis` on disk yet, so the extra notes the user mentioned are not available in the current workspace.
* The local Gemini delegation blocker on 2026-05-20 was a corrupted `~/.gemini/gemini-credentials.json`; moving it aside restored OAuth-backed headless Gemini delegation.
* Gemini delegation should be treated as a general-purpose autonomous helper agent backend, not as a special-purpose read-only search tool.

## Assumptions

* The right first cut is the smallest honest integration that closes the existing seam, not a speculative registry redesign.
* Gemini should be treated as a real delegated backend wherever the current harness already has the plumbing to support it.
* A deeper agent-registry abstraction may still be valuable later, but it is intentionally out of this MVP unless the implementation reveals a sharp need for it.

## Requirements (evolving)

* Treat Gemini as CLI-agent capable in the shared adapter surface.
* Configure Gemini role routing so research uses a faster/cheaper model and implementation/check use a stronger model.
* Preserve backend-specific behavior where the platforms genuinely differ.
* Keep packaged templates and this repo's generated harness in sync.
* Add regression coverage for the new Gemini behavior.
* Reconcile the user's extra notes from `/tmp/trellis` later if that material becomes available.
* Add a local delegate preflight so corrupted Gemini credential files fail with a clear, actionable message before Gemini CLI emits a stack trace.
* Make the delegate wrapper usage and injected prompt describe a normal autonomous agent handoff: the caller supplies complete task instructions and scope, and Gemini can edit/run commands under the selected approval mode.
* Default local delegation should be useful for real work (`yolo` approval mode), with `--approval-mode plan` available for read-only/review tasks.

## Acceptance Criteria (evolving)

* [ ] `CLIAdapter.supports_cli_agents` reports Gemini as supported.
* [ ] Gemini settings pin `trellis-research` to a Flash-class model and `trellis-implement` / `trellis-check` to a Pro-class model.
* [ ] Gemini agent descriptions make the routing intent legible.
* [ ] Packaged templates and local generated harness files stay aligned.
* [ ] Regression coverage proves the new behavior.
* [x] Local Gemini delegate command succeeds from this project after repairing corrupted credentials.
* [x] Local delegate wrapper catches invalid credential JSON with a clear diagnostic.
* [x] Delegate wrapper help text and worker prelude frame Gemini as a general autonomous helper agent.
* [x] Delegate wrapper defaults to `yolo`, matching the expected posture for useful delegated implementation work.
* [x] Gemini write probe succeeds under default delegation mode and cleans up its temporary file.

## Definition of Done (team quality bar)

* Tests added/updated (unit/integration where appropriate)
* Lint / typecheck / CI green
* Docs/notes updated if behavior changes
* Rollout/rollback considered if risky

## Out of Scope (explicit)

* Reworking every Trellis platform in one pass.
* Building a generalized multi-backend agent registry in this pass.
* Removing legitimate backend differences just to force symmetry.

## Technical Notes

* Inspected: `packages/cli/src/types/ai-tools.ts`, `src/configurators/{index,codex,gemini,shared}.ts`, Codex/Gemini agent templates, and existing tests under `packages/cli/test/`.
* Existing useful seam: `applyPullBasedPreludeMarkdown()` / `applyPullBasedPreludeToml()` already normalize a cross-backend concern for Codex/Gemini.
* Existing tests suggest likely extension points: `test/configurators/platforms.test.ts`, `test/registry-invariants.test.ts`, and sections of `test/regression.test.ts`.
* 2026-05-20 local repair:
  * Moved corrupted credentials to `/home/bowen/.gemini/gemini-credentials.json.corrupt-20260520-003557`.
  * Verified delegate health with `~/.gemini/extensions/superpowers/skills/delegate-to-gemini/delegate.sh --model auto --prompt "Health check only. Reply with exactly: GEMINI_DELEGATION_FINAL_OK" --timeout 120`.
  * Added credential JSON preflight to `.trellis/scripts/delegate_to_gemini.sh`.
  * Clarified `.trellis/scripts/delegate_to_gemini.sh` usage: Gemini can handle general agent tasks, including editing and validation.
  * Set default delegation approval mode to `yolo`; callers can still pass `--approval-mode plan` for read-only/review tasks.
  * Verified write-capable worker behavior with a temporary `.trellis/tmp_gemini_write_probe.txt` create/verify/delete task; Gemini returned `GEMINI_YOLO_AGENT_OK` and the probe file was absent afterward.
  * `rg` is still missing on this host; Gemini falls back to grep, which is slower but not blocking.
