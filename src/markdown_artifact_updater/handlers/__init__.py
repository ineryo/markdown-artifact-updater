"""Rendering handlers for supported explicit generated regions."""

from __future__ import annotations

import csv
import importlib
import json
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from markdown_artifact_updater.model import IncludeBlockError, PythonCallDeniedError
from markdown_artifact_updater.parser import IncludeRegion, parse_spec, require_spec
from markdown_artifact_updater.paths import markdown_relative_path, resolve_under_root
from markdown_artifact_updater.snippets import extract_snippet, resolve_fence_language

_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif"}
_HTML_SUFFIXES = {".html", ".htm"}
_CPP_SUFFIXES = {".cpp", ".cc", ".cxx", ".hpp", ".h"}


def _split_items(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _boolean(value: str, option: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise IncludeBlockError(f"{option} must be true or false")


def _read_text(root: Path, path_text: str) -> str:
    path = resolve_under_root(root, path_text)
    if not path.is_file():
        raise IncludeBlockError(f"Source file not found: {path_text}")
    return path.read_text(encoding="utf-8")


def _marked_content(text: str, kind: str, name: str, marker_prefix: str) -> str:
    if marker_prefix == "html":
        pattern = re.compile(
            rf"<!--\s*{re.escape(kind)}:start\s+{re.escape(name)}\s*-->\s*"
            rf"(?P<body>.*?)\s*<!--\s*{re.escape(kind)}:end\s+{re.escape(name)}\s*-->",
            re.DOTALL,
        )
    else:
        escaped_prefix = re.escape(marker_prefix)
        pattern = re.compile(
            rf"^\s*{escaped_prefix}\s*{re.escape(kind)}:start\s+{re.escape(name)}\s*$\n?"
            rf"(?P<body>.*?)^\s*{escaped_prefix}\s*{re.escape(kind)}:end\s+{re.escape(name)}\s*$",
            re.MULTILINE | re.DOTALL,
        )
    match = pattern.search(text)
    if match is None:
        raise IncludeBlockError(f"{kind} marker not found: {name}")
    return match.group("body").strip("\n")


def _snippet_marker_prefix(source_path: Path) -> str:
    """Return the valid line-comment prefix for a snippet source file."""
    return "//" if source_path.suffix.lower() in _CPP_SUFFIXES else "#"


def _render_snippet(region: IncludeRegion, root: Path) -> str:
    path_text, name = require_spec("snippet", region.spec).rsplit("#", 1)
    source_path = resolve_under_root(root, path_text)
    code = extract_snippet(source_path, name).text
    fence = re.search(r"^\s*(`{3,}|~{3,})([^\n]*)", region.body)
    marker, language = fence.groups() if fence else ("```", "")
    language = resolve_fence_language(source_path, language)
    return f"{marker}{language.rstrip()}\n{code}\n{marker}"


def _render_file(region: IncludeRegion, root: Path) -> str:
    """Include an entire UTF-8 text file without interpreting its contents."""
    path_text, options = parse_spec(require_spec("file", region.spec))
    if options:
        raise IncludeBlockError("file-include does not accept options")
    return _read_text(root, path_text).rstrip("\n")


def _markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    def cell(value: object) -> str:
        return str(value).replace("|", "\\|").replace("\n", "<br>")

    header = "| " + " | ".join(cell(column) for column in columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    body = [
        "| " + " | ".join(cell(row.get(column, "")) for column in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, divider, *body])


def _warn_if_stale(
    source: Path,
    path_text: str,
    options: dict[str, str],
    root: Path,
    label: str,
    warnings: list[str],
) -> None:
    for dependency_text in _split_items(options.get("depends_on", "")):
        dependency = resolve_under_root(root, dependency_text)
        if not dependency.exists():
            warnings.append(f"{label} dependency not found: {dependency_text}")
        elif source.stat().st_mtime < dependency.stat().st_mtime:
            warnings.append(
                f"{label} artifact may be stale: {path_text} is older than {dependency_text}"
            )


def _render_dataframe(region: IncludeRegion, root: Path, warnings: list[str]) -> str:
    path_text, options = parse_spec(require_spec("dataframe", region.spec))
    source = resolve_under_root(root, path_text)
    if source.suffix.lower() != ".csv":
        raise IncludeBlockError(
            "dataframe-include supports CSV without optional dependencies; install pandas and a suitable engine for other formats"
        )
    try:
        with source.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    except FileNotFoundError as error:
        raise IncludeBlockError(f"DataFrame file not found: {path_text}") from error
    columns = list(rows[0]) if rows else []
    if "columns" in options:
        columns = _split_items(options["columns"])
        missing = [column for column in columns if rows and column not in rows[0]]
        if missing:
            raise IncludeBlockError(f"DataFrame missing requested columns: {missing}")
    if "drop_columns" in options:
        dropped = set(_split_items(options["drop_columns"]))
        columns = [column for column in columns if column not in dropped]
    if "sort_by" in options:
        sort_key = options["sort_by"]
        if sort_key not in columns:
            raise IncludeBlockError(
                f"sort_by column not found in DataFrame: {sort_key}"
            )
        reverse = not _boolean(options.get("ascending", "true"), "ascending")
        rows.sort(key=lambda row: row.get(sort_key, ""), reverse=reverse)
    if "max_rows" in options:
        rows = rows[: int(options["max_rows"])]
    if "max_cols" in options:
        columns = columns[: int(options["max_cols"])]
    if "rename" in options:
        rename = dict(item.split(":", 1) for item in _split_items(options["rename"]))
        display_columns = [rename.get(column, column) for column in columns]
        rows = [
            {rename.get(key, key): value for key, value in row.items()} for row in rows
        ]
        columns = display_columns
    _warn_if_stale(source, path_text, options, root, "DataFrame", warnings)
    caption = options.get("caption", "").strip()
    prefix = f"**{caption}**\n\n" if caption else ""
    return prefix + _markdown_table(rows, columns)


def _render_figure(
    region: IncludeRegion, root: Path, markdown_path: Path, warnings: list[str]
) -> str:
    path_text, options = parse_spec(require_spec("figure", region.spec))
    source = resolve_under_root(root, path_text)
    if not source.is_file():
        raise IncludeBlockError(f"Figure file not found: {path_text}")
    _warn_if_stale(source, path_text, options, root, "Figure", warnings)
    relative = markdown_relative_path(markdown_path, source)
    if source.suffix.lower() in _IMAGE_SUFFIXES:
        attributes = " ".join(
            f"{key}:{options[key]}" for key in ("width", "height") if key in options
        )
        generated = f"![{attributes}]({relative})"
    elif source.suffix.lower() in _HTML_SUFFIXES:
        if options.get("mode", "iframe") == "link":
            generated = (
                f"[{options.get('label', 'Open interactive HTML plot')}]({relative})"
            )
        else:
            generated = f'<iframe src="{relative}" width="{options.get("width", "100%")}" height="{options.get("height", "520")}" title="{options.get("title", "interactive plot")}" frameborder="0"></iframe>'
    else:
        raise IncludeBlockError(f"Unsupported figure file type: {source.suffix}")
    caption = options.get("caption", "").strip()
    return generated + (f"\n\n**{caption}**" if caption else "")


def _render_quote_or_equation(region: IncludeRegion, root: Path) -> str:
    spec = require_spec(region.kind, region.spec)
    path_text, name_and_query = spec.rsplit("#", 1)
    name, options = parse_spec(name_and_query)
    source = _read_text(root, path_text)
    content = _marked_content(source, region.kind, name, "html")
    if region.kind == "equation" and _boolean(options.get("wrap", "true"), "wrap"):
        return f"\\[\n{content}\n\\]"
    return content


def _parse_call_options(spec: str) -> dict[str, str]:
    return dict(
        item.split("=", 1) for item in spec.replace("\n", "&").split("&") if "=" in item
    )


def _render_python_call(
    region: IncludeRegion, root: Path, allowed_modules: frozenset[str]
) -> str:
    options = _parse_call_options(require_spec("python-call", region.spec))
    module_name = options.get("module", "")
    function_name = options.get("function", "")
    if not module_name or not function_name:
        raise IncludeBlockError("python-call-include requires module and function")
    if module_name not in allowed_modules:
        raise PythonCallDeniedError(
            f"python-call-include is disabled by default; explicitly allow module: {module_name}"
        )
    root_text = str(root)
    sys.path.insert(0, root_text)
    try:
        module = importlib.import_module(module_name)
        function: Callable[..., Any] = getattr(module, function_name)
        args = json.loads(options.get("args", "[]"))
        kwargs = json.loads(options.get("kwargs", "{}"))
        result = function(*args, **kwargs)
    finally:
        sys.path.remove(root_text)
    if options.get("format", "io") == "output":
        return f"```python\n{result!r}\n```"
    return f"**Input**\n\n```python\n{function_name}(...)\n```\n\n**Output**\n\n```python\n{result!r}\n```"


def render_region(
    region: IncludeRegion,
    root: Path,
    markdown_path: Path,
    warnings: list[str],
    allowed_modules: frozenset[str],
    counts: dict[str, int],
) -> str:
    """Render a single region and update only deterministic local bookkeeping."""
    if region.kind == "snippet":
        rendered = _render_snippet(region, root)
    elif region.kind == "file":
        rendered = _render_file(region, root)
    elif region.kind == "dataframe":
        rendered = _render_dataframe(region, root, warnings)
    elif region.kind == "figure":
        rendered = _render_figure(region, root, markdown_path, warnings)
    elif region.kind in {"quote", "equation"}:
        rendered = _render_quote_or_equation(region, root)
    elif region.kind == "python-call":
        rendered = _render_python_call(region, root, allowed_modules)
    else:
        lines = ["**Provenance**", "", "- Generated by: `markdown-artifact-updater`"]
        if counts:
            rendered_counts = ", ".join(
                f"{kind}={count}" for kind, count in sorted(counts.items())
            )
            lines.append(f"- Generated regions: `{rendered_counts}`")
        if warnings:
            lines.append("- Warnings:")
            lines.extend(f"  - {warning}" for warning in warnings)
        rendered = "\n".join(lines)
    count_name = "python_call" if region.kind == "python-call" else region.kind
    counts[count_name] = counts.get(count_name, 0) + 1
    return rendered
