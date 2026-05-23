Wrote exactly one file:

[`.trellis/tasks/05-19-add-gemini-agent-routing-to-harness/research/codex_exec_aux_code_probe.py`](/home/bowen/bowen_lab/projects/arti6_linearvc/.trellis/tasks/05-19-add-gemini-agent-routing-to-harness/research/codex_exec_aux_code_probe.py)

It contains `route_role(kind: str) -> str` mapping `search/research/docs` to `gemini`, `review/design/risky` to `codex`, and defaults to `auto`, plus a `__main__` smoke print.

Tool access worked: I verified the target directory and created the requested file with `apply_patch`.