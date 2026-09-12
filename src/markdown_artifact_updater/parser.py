"""Parsing for explicit, bounded generated regions in Markdown."""

from __future__ import annotations

import re
from dataclasses import dataclass

from markdown_artifact_updater.model import IncludeBlockError

SUPPORTED_KINDS = (
    "snippet",
    "dataframe",
    "figure",
    "quote",
    "equation",
    "python-call",
    "provenance",
)

_REGION_RE = re.compile(
    r"(?P<start><!--\s*(?P<kind>snippet|dataframe|figure|quote|equation|python-call|provenance)-include(?:\s*:\s*(?P<spec>.*?))?\s*-->)"
    r"(?P<body>.*?)"
    r"(?P<end><!--\s*(?P=kind)-include-end\s*-->)",
    re.DOTALL,
)


@dataclass(frozen=True)
class IncludeRegion:
    """One recognized explicit generated region."""

    kind: str
    spec: str
    start: str
    body: str
    end: str


def iter_regions(markdown: str) -> tuple[IncludeRegion, ...]:
    """Return recognized regions in document order."""
    return tuple(
        IncludeRegion(
            kind=match.group("kind"),
            spec=(match.group("spec") or "").strip(),
            start=match.group("start"),
            body=match.group("body"),
            end=match.group("end"),
        )
        for match in _REGION_RE.finditer(markdown)
    )


def replace_regions(markdown: str, renderer) -> str:
    """Replace only region bodies, preserving all surrounding document bytes."""

    def replacement(match: re.Match[str]) -> str:
        region = IncludeRegion(
            kind=match.group("kind"),
            spec=(match.group("spec") or "").strip(),
            start=match.group("start"),
            body=match.group("body"),
            end=match.group("end"),
        )
        rendered = renderer(region)
        line_ending = "\r\n" if "\r\n" in region.body else "\n"
        normalized = rendered.replace("\r\n", "\n").replace("\r", "\n")
        return line_ending.join(
            (region.start, normalized.replace("\n", line_ending), region.end)
        )

    return _REGION_RE.sub(replacement, markdown)


def parse_spec(spec: str) -> tuple[str, dict[str, str]]:
    """Parse a path plus a compact URL-query option set."""
    from urllib.parse import parse_qsl

    path, separator, query = spec.partition("?")
    options = dict(parse_qsl(query, keep_blank_values=True)) if separator else {}
    return path.strip(), options


def require_spec(kind: str, spec: str) -> str:
    """Reject a header with required but missing source data."""
    if not spec:
        raise IncludeBlockError(f"{kind}-include requires a source specification")
    return spec
