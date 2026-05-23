#!/usr/bin/env bash
# Delegate an isolated task from Codex/Trellis to Gemini CLI.
# This intentionally disables Gemini extensions by default so third-party hooks
# do not hijack headless prompts or force incompatible skill/tool flows.

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: .trellis/scripts/delegate_to_gemini.sh --model <auto|flash|pro|MODEL_ID> --prompt "..." [--approval-mode <plan|default|auto_edit|yolo>] [--timeout <seconds>]

Delegate a general agent task to Gemini CLI from the current Trellis project.
Use it the same way you would spawn a smaller helper agent: pass the complete
task instructions in --prompt, including scope, expected output, and edit policy.

Model aliases:
  auto   omit --model and let Gemini CLI choose its configured default
  flash  ${GEMINI_FLASH_MODEL:-gemini-3-flash-preview}
  pro    ${GEMINI_PRO_MODEL:-gemini-3.1-pro-preview}

Defaults:
  --model auto
  --approval-mode yolo   # same default posture as an autonomous coding agent in this repo
  --timeout 1800

Examples:
  # General reasoning / review / planning helper
  .trellis/scripts/delegate_to_gemini.sh --model auto --approval-mode plan --prompt "Review this approach and return risks."

  # Read-only codebase exploration
  .trellis/scripts/delegate_to_gemini.sh --model flash --approval-mode plan --prompt "Inspect X and summarize relevant files."

  # Bounded implementation helper with normal edit/run permissions
  .trellis/scripts/delegate_to_gemini.sh --model pro --prompt "Edit only file Y to add Z; run syntax check."
USAGE
}

MODEL_ALIAS="auto"
PROMPT=""
APPROVAL_MODE="${GEMINI_DELEGATE_APPROVAL_MODE:-yolo}"
TIMEOUT_SECONDS="${GEMINI_DELEGATE_TIMEOUT_SECONDS:-1800}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      [[ $# -ge 2 ]] || { echo "Missing value for --model" >&2; usage >&2; exit 2; }
      MODEL_ALIAS="$2"; shift 2 ;;
    --prompt)
      [[ $# -ge 2 ]] || { echo "Missing value for --prompt" >&2; usage >&2; exit 2; }
      PROMPT="$2"; shift 2 ;;
    --approval-mode)
      [[ $# -ge 2 ]] || { echo "Missing value for --approval-mode" >&2; usage >&2; exit 2; }
      APPROVAL_MODE="$2"; shift 2 ;;
    --timeout)
      [[ $# -ge 2 ]] || { echo "Missing value for --timeout" >&2; usage >&2; exit 2; }
      TIMEOUT_SECONDS="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$PROMPT" ]] || { echo "--prompt is required" >&2; usage >&2; exit 2; }

case "$APPROVAL_MODE" in
  plan|default|auto_edit|yolo) ;;
  *) echo "Invalid --approval-mode: $APPROVAL_MODE" >&2; exit 2 ;;
esac

case "$MODEL_ALIAS" in
  auto) MODEL_ID="" ;;
  flash) MODEL_ID="${GEMINI_FLASH_MODEL:-gemini-3-flash-preview}" ;;
  pro) MODEL_ID="${GEMINI_PRO_MODEL:-gemini-3.1-pro-preview}" ;;
  *) MODEL_ID="$MODEL_ALIAS" ;;
esac

if ! command -v gemini >/dev/null 2>&1; then
  echo "Gemini CLI not found on PATH" >&2
  exit 127
fi

GEMINI_CREDENTIALS_FILE="${GEMINI_CREDENTIALS_FILE:-$HOME/.gemini/gemini-credentials.json}"
if [[ -f "$GEMINI_CREDENTIALS_FILE" ]]; then
  if ! python3 - "$GEMINI_CREDENTIALS_FILE" >/dev/null 2>&1 <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as f:
    json.load(f)
PY
  then
    cat >&2 <<EOF
Gemini CLI credentials file is not valid JSON:
  $GEMINI_CREDENTIALS_FILE

Gemini CLI refuses to start when this file is corrupted. Move it aside and
let Gemini fall back to OAuth/API-key auth, for example:

  mv "$GEMINI_CREDENTIALS_FILE" "$GEMINI_CREDENTIALS_FILE.corrupt-\$(date +%Y%m%d-%H%M%S)"

EOF
    exit 78
  fi
fi

PROJECT_ROOT="$(pwd)"
TASK_CONTEXT="none"
if [[ -x .trellis/scripts/task.py || -f .trellis/scripts/task.py ]]; then
  CURRENT_TASK_OUTPUT="$(python3 ./.trellis/scripts/task.py current --source 2>/dev/null || true)"
  if [[ "$CURRENT_TASK_OUTPUT" == Current\ task:\ * ]]; then
    TASK_CONTEXT="$(printf '%s\n' "$CURRENT_TASK_OUTPUT" | sed -n 's/^Current task: //p' | head -n 1)"
  fi
elif [[ -f .trellis/current_task ]]; then
  TASK_CONTEXT="$(cat .trellis/current_task 2>/dev/null || true)"
elif [[ -d .trellis/tasks ]]; then
  TASK_CONTEXT="Trellis task directory exists; no .trellis/current_task file found"
fi

FULL_PROMPT=$(cat <<PROMPT_EOF
Active task: ${TASK_CONTEXT}

You are a delegated Gemini worker called by Codex inside the Trellis harness.
Treat this as a normal autonomous agent handoff. You have the same project
responsibilities as any coding agent in this repository: read the harness
context, follow the requested task scope, do the work, verify it, and report back.

Context:
- Project root: ${PROJECT_ROOT}
- Active task: ${TASK_CONTEXT}
- You may inspect repository files from this working directory.
- Follow AGENTS.md if present.
- Respect the caller's prompt as the task scope.
- Do not perform destructive operations unless the prompt explicitly asks for them.
- Return a concise report of what you did, what you found, and any files changed.

Delegated task:
${PROMPT}
PROMPT_EOF
)

CMD=(gemini --skip-trust --extensions "" --approval-mode "$APPROVAL_MODE" --output-format text)
if [[ -n "$MODEL_ID" ]]; then
  CMD+=(-m "$MODEL_ID")
fi
CMD+=(-p "$FULL_PROMPT")

echo "[delegate_to_gemini] cwd=${PROJECT_ROOT}" >&2
echo "[delegate_to_gemini] model=${MODEL_ID:-auto} approval_mode=${APPROVAL_MODE} timeout=${TIMEOUT_SECONDS}s" >&2

if command -v timeout >/dev/null 2>&1; then
  timeout "$TIMEOUT_SECONDS" "${CMD[@]}"
else
  "${CMD[@]}"
fi
