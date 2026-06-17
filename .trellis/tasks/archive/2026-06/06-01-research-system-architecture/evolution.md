## 2026-06-01 - Gemini delegation path unavailable

- Context: Tried to use AGENTS.md worker-bee delegation path during research-system planning
- Command: `~/.gemini/extensions/superpowers/skills/delegate-to-gemini/delegate.sh`
- Evidence: Path did not exist on this machine
- Next diagnostic: Use project-local survey delegation helper or verify desired Gemini delegate installation path

## 2026-06-01 - Project Gemini delegate shell parse failure

- Context: Tried to use .trellis/scripts/delegate_to_gemini.sh as fallback during planning
- Command: `.trellis/scripts/delegate_to_gemini.sh --model flash --approval-mode plan ...`
- Evidence: bash -n reports unexpected EOF while looking for matching single quote near line 133
- Next diagnostic: Repair delegate_to_gemini.sh or route survey delegation through research_survey.py
- Status: Resolved in this task by removing the apostrophe from the unquoted here-doc body; `bash -n` now passes.
## 2026-06-02 - Survey delegate output filename too long

- Context: Delegating broad singing-skill/disentangled-codec literature scouting from current research-system task
- Command: `python3 ./.trellis/scripts/research_survey.py delegate --backend gemini --topic <long topic>`
- Evidence: OSError Errno 63 File name too long when writing survey/reports/delegated-<full-topic>-20260602-011316.md
- Next diagnostic: Slug delegated report filenames to a short hash or truncate topic-derived basename before write_text
- Status: Resolved by limiting the readable slug to 80 characters and appending a stable SHA-256 prefix.
