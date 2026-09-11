"""Language-light source reading, marker indexing, and fence hints."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from marp_artifact_updater.model import IncludeBlockError

_MARKER = re.compile(
    r"^\s*(?:(?P<line>#|//|--|%|;)\s*snippet:(?P<kind>start|end)\s+(?P<name>[^\s]+)\s*|<!--\s*snippet:(?P<html_kind>start|end)\s+(?P<html_name>[^\s]+)\s*-->)\s*$"
)
_FENCES = {
    ".py": "python",
    ".pyi": "python",
    ".c": "c",
    ".h": "c",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".cxx": "cpp",
    ".hh": "cpp",
    ".hpp": "cpp",
    ".hxx": "cpp",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".cs": "csharp",
    ".sh": "bash",
    ".bash": "bash",
    ".sql": "sql",
    ".r": "r",
    ".lua": "lua",
    ".ipynb": "python",
}


@dataclass(frozen=True)
class ExtractedSnippet:
    text: str
    suggested_fence_language: str


def _read_lines(path: Path) -> list[str]:
    if path.suffix.lower() != ".ipynb":
        return path.read_text(encoding="utf-8").splitlines()
    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise IncludeBlockError(f"Malformed notebook source: {path}") from error
    lines: list[str] = []
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") == "code":
            source = cell.get("source", [])
            lines.extend(
                "".join(source).splitlines()
                if isinstance(source, list)
                else str(source).splitlines()
            )
    return lines


def _markers(
    lines: list[str], path: Path
) -> tuple[dict[str, tuple[int, int]], set[int]]:
    starts: dict[str, int] = {}
    ends: dict[str, int] = {}
    controls: set[int] = set()
    for index, line in enumerate(lines):
        match = _MARKER.fullmatch(line)
        if not match:
            continue
        controls.add(index)
        kind = match.group("kind") or match.group("html_kind")
        name = match.group("name") or match.group("html_name")
        target = starts if kind == "start" else ends
        if name in target:
            label = "start" if kind == "start" else "end"
            raise IncludeBlockError(
                f"Invalid snippet markers in {path}: snippet '{name}' has more than one {label} marker"
            )
        target[name] = index
    if not starts and not ends:
        raise IncludeBlockError("snippet marker not found")
    for name, start in starts.items():
        if name not in ends:
            raise IncludeBlockError(
                f"Invalid snippet markers in {path}: snippet '{name}' has no matching end marker"
            )
        if ends[name] < start:
            raise IncludeBlockError(
                f"Invalid snippet markers in {path}: snippet '{name}' end precedes start"
            )
    for name in ends:
        if name not in starts:
            raise IncludeBlockError(
                f"Invalid snippet markers in {path}: snippet '{name}' has no matching start marker"
            )
    return {name: (start, ends[name]) for name, start in starts.items()}, controls


def resolve_fence_language(path: Path, explicit: str) -> str:
    if explicit.strip():
        return explicit.strip()
    suffix = path.suffix.lower()
    return _FENCES.get(suffix, suffix[1:] if suffix else "text")


def extract_snippet(path: Path, name: str) -> ExtractedSnippet:
    lines = _read_lines(path)
    intervals, controls = _markers(lines, path)
    if name not in intervals:
        raise IncludeBlockError(f"snippet marker not found: {name}")
    start, end = intervals[name]
    return ExtractedSnippet(
        "\n".join(
            line
            for i, line in enumerate(lines[start + 1 : end], start + 1)
            if i not in controls
        ),
        resolve_fence_language(path, ""),
    )
