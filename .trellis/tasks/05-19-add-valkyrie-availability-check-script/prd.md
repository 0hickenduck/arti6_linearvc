# Add Valkyrie availability check script

## Goal

Create a small read-only helper script that lets the user quickly see which Valkyrie hosts are available for daily work, including whether hosts are reachable, who is logged in, rough load, and accelerator/GPU information when available.

## What I already know

* The user now connects to `valkyrie02` and wants to run AI CLIs inside tmux for persistence.
* There are expected to be around eight Valkyrie hosts.
* The filesystem is shared between Athena and Valkyrie hosts, but shell PATH and process locality differ per host/session.
* The user wants a daily routine or script to decide which server to use.
* The script should help avoid using busy shared machines.

## Assumptions (temporary)

* "线卡" means GPU/显卡, likely from voice input.
* Hostnames are `valkyrie01` through `valkyrie08`.
* The check should be read-only and avoid killing or modifying processes.
* The script may use SSH to query peer Valkyrie nodes.

## Open Questions

* Should the MVP report GPU status only, or also network card/NIC model if "线卡" literally meant NIC?

## Requirements (evolving)

* Report each Valkyrie host in a compact table.
* Include reachability, uptime/load, logged-in users, tmux/session hints, and GPU model/usage when accessible.
* Be safe to run daily from a VS Code terminal or tmux.
* Avoid requiring root permissions.

## Acceptance Criteria (evolving)

* [ ] A single command can show status across Valkyrie hosts.
* [ ] Unreachable hosts fail quickly and clearly.
* [ ] Output helps the user choose an idle machine.
* [ ] The Codex bubblewrap warning is explained to the user.

## Definition of Done (team quality bar)

* Script runs without writing to system locations.
* No destructive commands are used.
* Documentation or final instructions explain daily usage.

## Out of Scope (explicit)

* Automatically migrating running VS Code/Codex/Gemini sessions.
* Killing other users' processes.
* Installing system packages such as bubblewrap without admin approval.

## Technical Notes

* Start with shell-based SSH probing because it is portable and transparent for the user to learn from.
