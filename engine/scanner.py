from __future__ import annotations

import re
from pathlib import Path

SKIP_DIRS = {
    ".git", ".gradle", ".gradle-user", ".idea", "build", "out", "target",
    "logs", "node_modules", "__pycache__", "dist", "vendor", ".dart_tool",
}
TEXT_EXTENSIONS = {
    ".java", ".kt", ".groovy", ".gradle", ".properties", ".yml", ".yaml",
    ".json", ".xml", ".sql", ".md", ".html", ".js", ".cjs", ".py", ".sh",
    ".bat", ".cmd", ".go", ".mod", ".env", ".conf", ".toml", "",
}
JAVA_EXTS = {".java", ".kt", ".groovy", ".gradle", ".properties", ".yml", ".yaml", ".xml"}
GO_EXTS = {".go", ".mod"}


def files_to_scan(root: Path) -> list[Path]:
    result: list[Path] = []
    for path in root.rglob("*", recurse_symlinks=False):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        result.append(path)
    return sorted(result)


def rulesets_for(path: Path) -> tuple[str, ...]:
    ext = path.suffix.lower()
    if ext in GO_EXTS:
        return ("common", "go")
    if ext in JAVA_EXTS:
        return ("common", "java_spring")
    return ("common",)


DOC_EXTS = {".md", ".html"}


def masked(line: str) -> str:
    line = line.strip()
    if len(line) > 180:
        line = line[:177] + "..."
    return re.sub(
        r"(?i)(password|secret|token|api[_-]?key)(\s*[:=]\s*)(\"[^\"]*\"|'[^']*'|[^\s,;}]+)",
        r"\1\2***",
        line,
    )
