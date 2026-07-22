"""Repository-root path containment helpers."""

from __future__ import annotations

import os
from pathlib import Path

from marp_artifact_updater.model import PathSafetyError


def normalize_repository_path(path_text: str) -> Path:
    """Normalize Markdown path separators without making a path absolute."""
    return Path(path_text.strip().replace("\\", "/"))


def resolve_under_root(root: Path, path_text: str | Path) -> Path:
    """Resolve a path only when its resolved location remains under ``root``.

    Resolving existing components intentionally detects symlink escapes. Absolute
    paths are rejected unless they identify a location below the supplied root.
    """
    resolved_root = root.resolve(strict=True)
    candidate = Path(path_text)
    if isinstance(path_text, str):
        candidate = normalize_repository_path(path_text)
    resolved_candidate = (resolved_root / candidate).resolve(strict=False)
    try:
        resolved_candidate.relative_to(resolved_root)
    except ValueError as error:
        raise PathSafetyError(f"Path escapes repository root: {path_text!s}") from error
    return resolved_candidate


def markdown_relative_path(markdown_path: Path, target_path: Path) -> str:
    """Return a portable path suitable for a Markdown link."""
    return os.path.relpath(target_path, start=markdown_path.parent).replace("\\", "/")
