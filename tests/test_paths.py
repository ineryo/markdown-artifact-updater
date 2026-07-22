"""Filesystem-containment behavior."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from marp_artifact_updater.paths import PathSafetyError, resolve_under_root


def test_resolve_under_root_accepts_existing_regular_file(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    source = root / "assets" / "example.txt"
    source.parent.mkdir()
    source.write_text("content", encoding="utf-8")

    assert resolve_under_root(root, "assets/example.txt") == source.resolve()


def test_resolve_under_root_refuses_parent_escape(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()

    with pytest.raises(PathSafetyError, match="escapes repository root"):
        resolve_under_root(root, "../outside.txt")


def test_resolve_under_root_refuses_symlink_escape(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("private", encoding="utf-8")
    link = root / "assets-link"
    try:
        os.symlink(outside, link)
    except OSError as error:
        pytest.skip(f"symlinks unavailable: {error}")

    with pytest.raises(PathSafetyError, match="escapes repository root"):
        resolve_under_root(root, "assets-link")
