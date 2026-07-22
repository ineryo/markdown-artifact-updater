"""CLI behavior for deterministic check and explicit apply modes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _run(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "marp_artifact_updater", *arguments],
        check=False,
        capture_output=True,
        cwd=root,
        text=True,
    )


def test_check_json_is_deterministic_and_does_not_write(tmp_path: Path) -> None:
    _write(tmp_path / "source.py", "# snippet:start x\nx = 1\n# snippet:end x\n")
    deck = _write(
        tmp_path / "deck.md",
        "<!-- snippet-include: source.py#x -->\n```python\nold\n```\n<!-- snippet-include-end -->\n",
    )
    original = deck.read_text(encoding="utf-8")

    result = _run(tmp_path, "check", "deck.md", "--repo-root", ".", "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["changed"] is True
    assert payload["counts"] == {"snippet": 1}
    assert deck.read_text(encoding="utf-8") == original


def test_update_requires_apply_before_writing(tmp_path: Path) -> None:
    _write(tmp_path / "source.py", "# snippet:start x\nx = 1\n# snippet:end x\n")
    deck = _write(
        tmp_path / "deck.md",
        "<!-- snippet-include: source.py#x -->\n```python\nold\n```\n<!-- snippet-include-end -->\n",
    )

    dry_run = _run(tmp_path, "update", "deck.md", "--repo-root", ".")
    applied = _run(tmp_path, "update", "deck.md", "--repo-root", ".", "--apply")

    assert dry_run.returncode == 1
    assert "Dry run" in dry_run.stdout
    assert applied.returncode == 0
    assert "x = 1" in deck.read_text(encoding="utf-8")
