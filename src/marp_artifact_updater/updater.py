"""Deterministic rendering, planning, and explicit atomic application."""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

from marp_artifact_updater.handlers import render_region
from marp_artifact_updater.model import IncludeBlockError, SynchronizationResult
from marp_artifact_updater.parser import iter_regions, replace_regions
from marp_artifact_updater.paths import resolve_under_root


def _fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _atomic_write(path: Path, content: str) -> None:
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=".marp-artifact-updater-",
        delete=False,
    ) as temporary:
        temporary.write(content)
        temporary.flush()
        os.fsync(temporary.fileno())
        temporary_path = Path(temporary.name)
    try:
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def synchronize_markdown(
    repo_root: Path | str,
    markdown_path: Path | str,
    *,
    apply: bool = False,
    allowed_modules: set[str] | frozenset[str] | None = None,
) -> SynchronizationResult:
    """Synchronize supported explicit regions, writing only with ``apply=True``."""
    root = Path(repo_root).resolve(strict=True)
    markdown = resolve_under_root(root, markdown_path)
    if not markdown.is_file():
        raise IncludeBlockError(f"Markdown file not found: {markdown_path}")
    original = markdown.read_text(encoding="utf-8")
    if not iter_regions(original):
        raise IncludeBlockError("No recognized generated regions found")
    warnings: list[str] = []
    counts: dict[str, int] = {}
    allowed = frozenset(allowed_modules or ())

    generated = replace_regions(
        original,
        lambda region: render_region(region, root, markdown, warnings, allowed, counts),
    )
    changed = generated != original
    if apply and changed:
        _atomic_write(markdown, generated)
    return SynchronizationResult(
        markdown_path=str(markdown.relative_to(root)),
        changed=changed,
        counts=dict(sorted(counts.items())),
        warnings=tuple(warnings),
        original_fingerprint=_fingerprint(original),
        generated_fingerprint=_fingerprint(generated),
        generated_text=generated,
        applied=apply and changed,
    )
