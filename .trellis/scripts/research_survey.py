#!/usr/bin/env python3
"""Task-local research survey and evolution helpers.

This script keeps research artifacts deterministic and file-backed while still
allowing optional delegation to external agent CLIs such as Gemini and
Antigravity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    while cur != cur.parent:
        if (cur / ".trellis").is_dir():
            return cur
        cur = cur.parent
    raise SystemExit("Error: could not find .trellis/ from current directory")


def slugify(value: str, fallback: str = "item") -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or fallback


def delegated_report_name(topic: str, timestamp: str) -> str:
    slug = slugify(topic, "survey")
    digest = hashlib.sha256(topic.encode("utf-8")).hexdigest()[:10]
    return f"delegated-{slug[:80].rstrip('-')}-{digest}-{timestamp}.md"


def display_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def yaml_scalar(value: str | None) -> str:
    return json.dumps(value or "")


def normalize_task_ref(repo_root: Path, task_ref: str | None) -> Path:
    if task_ref:
        raw = task_ref.strip()
    else:
        cmd = [sys.executable, "./.trellis/scripts/task.py", "current", "--source"]
        result = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        if result.returncode != 0 or "Current task:" not in result.stdout:
            raise SystemExit("Error: no active task found; pass --task <task-dir>")
        raw = ""
        for line in result.stdout.splitlines():
            if line.startswith("Current task:"):
                raw = line.split(":", 1)[1].strip()
                break
        if not raw:
            raise SystemExit("Error: could not parse active task path")

    path = Path(raw)
    if path.is_absolute():
        task_dir = path
    else:
        while raw.startswith("./"):
            raw = raw[2:]
        if raw.startswith(".trellis/"):
            task_dir = repo_root / raw
        elif raw.startswith("tasks/"):
            task_dir = repo_root / ".trellis" / raw
        else:
            task_dir = repo_root / ".trellis" / "tasks" / raw

    if not task_dir.is_dir():
        raise SystemExit(f"Error: task directory not found: {task_dir}")
    return task_dir


def ensure_survey_dirs(task_dir: Path) -> Path:
    survey = task_dir / "survey"
    for child in (
        survey / "papers",
        survey / "reports",
        survey / "shortlists",
        task_dir / "research",
    ):
        child.mkdir(parents=True, exist_ok=True)
    return survey


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def append(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)


def read_developer(repo_root: Path) -> str | None:
    developer_file = repo_root / ".trellis" / ".developer"
    if not developer_file.is_file():
        return None
    raw = developer_file.read_text(encoding="utf-8").strip()
    for line in raw.splitlines():
        if line.startswith("name="):
            value = line.split("=", 1)[1].strip()
            return value or None
    return raw or None


def record_problem(
    repo_root: Path,
    task_dir: Path,
    title: str,
    context: str,
    command: str,
    evidence: str,
    next_step: str,
) -> None:
    entry = f"""## {today()} - {title}

- Context: {context or "-"}
- Command: `{command or "-"}`
- Evidence: {evidence or "-"}
- Next diagnostic: {next_step or "-"}

"""
    append(task_dir / "evolution.md", entry)

    developer = read_developer(repo_root)
    if developer:
        append(
            repo_root / ".trellis" / "workspace" / developer / "evolution-backlog.md",
            entry,
        )


def build_survey_prompt(topic: str, instructions: str) -> str:
    extra = f"\n\nAdditional instructions:\n{instructions.strip()}" if instructions.strip() else ""
    return f"""You are a read-only deep-learning survey scout.

Task:
Research this topic and return concise markdown for a task-local survey evidence store:

{topic}

Required output:
- Candidate papers with title, year, venue if known, arXiv/OpenReview/DOI links when available.
- Code repository links and whether the code appears usable.
- For each important paper: idea, method, experiment-design pattern, datasets, metrics, ablations.
- Classify each paper as broad survey context, related-work evidence, possible pivot/baseline, experiment-critical reference, or rejected/archived candidate.
- Highlight benchmark candidates with public code.
- Mark uncertain facts explicitly. Do not fabricate citations, venues, code links, metrics, or results.

Do not modify repository files. Return markdown only.{extra}
"""


def backend_command(backend: str, prompt: str, timeout_seconds: int) -> list[str]:
    if backend == "gemini":
        return [
            "gemini",
            "--skip-trust",
            "--extensions",
            "",
            "--approval-mode",
            "plan",
            "--output-format",
            "text",
            "-p",
            prompt,
        ]
    if backend == "antigravity":
        return [
            "agy",
            "--print",
            "--print-timeout",
            f"{timeout_seconds}s",
            "--dangerously-skip-permissions",
            prompt,
        ]
    raise ValueError(f"Unsupported backend: {backend}")


def choose_backends(requested: str) -> list[str]:
    if requested == "auto":
        result = []
        if shutil.which("gemini"):
            result.append("gemini")
        if shutil.which("agy"):
            result.append("antigravity")
        return result
    if requested == "gemini":
        return ["gemini"] if shutil.which("gemini") else []
    if requested == "antigravity":
        return ["antigravity"] if shutil.which("agy") else []
    if requested == "local":
        return []
    raise ValueError(f"Unsupported backend: {requested}")


def cmd_init(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    task_dir = normalize_task_ref(repo_root, args.task)
    survey = ensure_survey_dirs(task_dir)
    report = survey / "reports" / "survey.md"
    if not report.exists():
        report.write_text(
            f"""# Survey

- Date: {today()}
- Task: {task_dir.name}

## Human-Readable Synthesis

Write the decision-relevant survey here. Keep detailed per-paper extraction in
`survey/papers/<paper-id>/`.

## Open Questions

-
""",
            encoding="utf-8",
        )
    print(survey.relative_to(repo_root))
    return 0


def cmd_paper(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    task_dir = normalize_task_ref(repo_root, args.task)
    survey = ensure_survey_dirs(task_dir)
    paper_id = args.paper_id or slugify(args.title or args.arxiv or "paper")
    paper_dir = survey / "papers" / paper_id
    paper_dir.mkdir(parents=True, exist_ok=True)

    metadata = paper_dir / "metadata.yaml"
    if not metadata.exists():
        metadata.write_text(
            f"""id: {yaml_scalar(paper_id)}
title: {yaml_scalar(args.title)}
authors: []
venue: {yaml_scalar(args.venue)}
year: {yaml_scalar(args.year)}
links:
  arxiv: {yaml_scalar(args.arxiv)}
  openreview: {yaml_scalar(args.openreview)}
  doi: {yaml_scalar(args.doi)}
role: "broad-survey-context"
status: "candidate"
""",
            encoding="utf-8",
        )

    templates = {
        "source.md": "# Source Notes\n\n- Source availability:\n- Sections extracted:\n",
        "code.md": f"# Code Notes\n\n- Repository: {args.code or ''}\n- Usable as benchmark: unknown\n- Install notes:\n- License:\n",
        "extraction.md": "# Extraction\n\n## Idea\n\n## Method\n\n## Experiment Design Pattern\n\n## Datasets\n\n## Metrics\n\n## Ablations\n\n## Implementation Availability\n\n",
        "summary.md": "# Summary\n\n## Decision-Relevant Takeaway\n\n## Caveats\n\n",
        "relevance.md": "# Relevance\n\n- Role: broad-survey-context\n- Why it matters:\n- Promote to experiment shortlist: no\n",
    }
    for filename, content in templates.items():
        path = paper_dir / filename
        if not path.exists():
            path.write_text(content, encoding="utf-8")

    print(paper_dir.relative_to(repo_root))
    return 0


def cmd_delegate(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    task_dir = normalize_task_ref(repo_root, args.task)
    survey = ensure_survey_dirs(task_dir)
    prompt = build_survey_prompt(args.topic, args.instructions or "")
    backends = choose_backends(args.backend)

    if args.backend != "local" and not backends:
        record_problem(
            repo_root,
            task_dir,
            "Survey delegation backend unavailable",
            f"Requested backend: {args.backend}",
            "research_survey.py delegate",
            "No matching CLI found on PATH",
            "Run `command -v gemini agy` and verify CLI installation",
        )
        return 2

    if args.backend == "local":
        print(prompt)
        return 0

    last_error = ""
    for backend in backends:
        cmd = backend_command(backend, prompt, args.timeout)
        try:
            result = subprocess.run(
                cmd,
                cwd=repo_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=args.timeout,
            )
        except subprocess.TimeoutExpired:
            last_error = f"{backend} timed out after {args.timeout}s"
            record_problem(
                repo_root,
                task_dir,
                "Survey delegation timed out",
                f"Topic: {args.topic}",
                " ".join(cmd[:4]) + " ...",
                last_error,
                f"Retry with --backend {backend} --timeout <larger seconds> or use --backend local",
            )
            continue

        if result.returncode == 0 and result.stdout.strip():
            output = args.output or (
                survey
                / "reports"
                / delegated_report_name(
                    args.topic,
                    datetime.now().strftime("%Y%m%d-%H%M%S"),
                )
            )
            output = Path(output)
            if not output.is_absolute():
                output = repo_root / output
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(result.stdout.strip() + "\n", encoding="utf-8")
            print(display_path(output, repo_root))
            return 0

        last_error = (result.stderr or result.stdout or "empty output").strip()
        record_problem(
            repo_root,
            task_dir,
            "Survey delegation failed",
            f"Backend: {backend}; topic: {args.topic}",
            " ".join(cmd[:4]) + " ...",
            last_error[:2000],
            f"Inspect CLI auth/config for {backend}, then retry or use --backend local",
        )

    print(last_error, file=sys.stderr)
    return 1


def cmd_record_problem(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    task_dir = normalize_task_ref(repo_root, args.task)
    record_problem(
        repo_root,
        task_dir,
        args.title,
        args.context or "",
        args.command or "",
        args.evidence or "",
        args.next or "",
    )
    print(task_dir / "evolution.md")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create task-local survey directories")
    p_init.add_argument("--task", help="Task directory/name; defaults to active task")
    p_init.set_defaults(func=cmd_init)

    p_paper = sub.add_parser("paper", help="Create a per-paper evidence template")
    p_paper.add_argument("--task", help="Task directory/name; defaults to active task")
    p_paper.add_argument("--paper-id")
    p_paper.add_argument("--title")
    p_paper.add_argument("--venue")
    p_paper.add_argument("--year")
    p_paper.add_argument("--arxiv")
    p_paper.add_argument("--openreview")
    p_paper.add_argument("--doi")
    p_paper.add_argument("--code")
    p_paper.set_defaults(func=cmd_paper)

    p_delegate = sub.add_parser("delegate", help="Delegate survey scouting/extraction")
    p_delegate.add_argument("--task", help="Task directory/name; defaults to active task")
    p_delegate.add_argument(
        "--backend",
        choices=("auto", "gemini", "antigravity", "local"),
        default="auto",
    )
    p_delegate.add_argument("--topic", required=True)
    p_delegate.add_argument("--instructions", default="")
    p_delegate.add_argument("--output", type=Path)
    p_delegate.add_argument("--timeout", type=int, default=600)
    p_delegate.set_defaults(func=cmd_delegate)

    p_problem = sub.add_parser("record-problem", help="Record an evolution backlog item")
    p_problem.add_argument("--task", help="Task directory/name; defaults to active task")
    p_problem.add_argument("--title", required=True)
    p_problem.add_argument("--context", default="")
    p_problem.add_argument("--command", default="")
    p_problem.add_argument("--evidence", default="")
    p_problem.add_argument("--next", default="")
    p_problem.set_defaults(func=cmd_record_problem)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
