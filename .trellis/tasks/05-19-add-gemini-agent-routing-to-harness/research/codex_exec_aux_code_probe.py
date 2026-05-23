def route_role(kind: str) -> str:
    if kind in {"search", "research", "docs"}:
        return "gemini"
    if kind in {"review", "design", "risky"}:
        return "codex"
    return "auto"


if __name__ == "__main__":
    print(route_role("search"))
