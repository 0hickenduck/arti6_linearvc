# Install Antigravity CLI

## Goal

Install the Antigravity CLI (the successor to Gemini CLI) on the server to enable advanced agent features and better remote TUI support.

## What I already know

* The user explicitly requested to install the "antigravity CLI (Google's new CLI)".
* Research indicates the installation command for Linux is `curl -fsSL https://antigravity.google/cli/install.sh | bash`.
* The binary name is `agy`.
* `agy` is not currently installed on the server.

## Requirements

* Install Antigravity CLI using the official installation script.
* Ensure the `agy` binary is accessible in the PATH.

## Acceptance Criteria

* [x] `agy --version` returns a version number.
* [x] The command `agy` is available in the shell.

## Definition of Done

* Antigravity CLI is installed and verified.
* No regressions or environment breakages.

## Out of Scope

* Configuration and login (this will be handled by the user as it may require interactive steps or personal credentials).
* Migration from Gemini CLI (unless requested).

## Technical Notes

* Installation script: `https://antigravity.google/cli/install.sh`
* Binary: `agy`
