"""End-to-end generated-region synchronization behavior."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from markdown_artifact_updater import updater
from markdown_artifact_updater.model import PathSafetyError, PythonCallDeniedError
from markdown_artifact_updater.updater import synchronize_markdown


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))
    return path


def test_dry_run_replaces_only_explicit_snippet_region_and_is_idempotent(
    tmp_path: Path,
) -> None:
    source = _write(
        tmp_path / "src" / "demo.py",
        "# snippet:start greeting\nprint('hello')\n# snippet:end greeting\n",
    )
    deck = _write(
        tmp_path / "slides" / "deck.md",
        "before\n<!-- snippet-include: src/demo.py#greeting -->\n```python\nold\n```\n<!-- snippet-include-end -->\nafter\n",
    )
    original = deck.read_text(encoding="utf-8")

    result = synchronize_markdown(tmp_path, deck, apply=False)

    assert result.changed is True
    assert deck.read_text(encoding="utf-8") == original
    assert "print('hello')" in result.generated_text
    assert result.counts == {"snippet": 1}
    assert result.original_fingerprint != result.generated_fingerprint
    applied = synchronize_markdown(tmp_path, deck, apply=True)
    repeated = synchronize_markdown(tmp_path, deck, apply=False)
    assert applied.changed is True
    assert repeated.changed is False
    assert source.exists()


def test_cpp_snippet_uses_valid_cpp_line_comment_markers(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "selection_sort.cpp",
        "// snippet:start selection-sort\n"
        "template <typename T>\n"
        "void selection_sort(T& values) {}\n"
        "// snippet:end selection-sort\n",
    )
    deck = _write(
        tmp_path / "slides" / "deck.md",
        "<!-- snippet-include: src/selection_sort.cpp#selection-sort -->\n"
        "```cpp\nold\n```\n"
        "<!-- snippet-include-end -->\n",
    )

    result = synchronize_markdown(tmp_path, deck)

    assert "void selection_sort(T& values) {}" in result.generated_text
    assert "snippet:start" not in result.generated_text
    assert "```cpp" in result.generated_text


def test_cpp_snippet_accepts_a_recognized_language_light_marker(tmp_path: Path) -> None:
    _write(
        tmp_path / "selection_sort.cpp",
        "# snippet:start selection-sort\n"
        "void selection_sort() {}\n"
        "# snippet:end selection-sort\n",
    )
    deck = _write(
        tmp_path / "deck.md",
        "<!-- snippet-include: selection_sort.cpp#selection-sort -->\n"
        "old\n"
        "<!-- snippet-include-end -->\n",
    )

    result = synchronize_markdown(tmp_path, deck)

    assert "void selection_sort() {}" in result.generated_text


def test_saved_notebook_cells_are_read_without_execution(tmp_path: Path) -> None:
    _write(
        tmp_path / "analysis.ipynb",
        json.dumps(
            {
                "cells": [
                    {
                        "cell_type": "code",
                        "source": [
                            "# snippet:start cell\n",
                            "x = 1\n",
                            "# snippet:end cell\n",
                        ],
                    },
                    {"cell_type": "markdown", "source": ["ignored"]},
                ]
            }
        ),
    )
    deck = _write(
        tmp_path / "deck.md",
        "<!-- snippet-include: analysis.ipynb#cell -->\n```python\nold\n```\n<!-- snippet-include-end -->\n",
    )

    result = synchronize_markdown(tmp_path, deck)

    assert "x = 1" in result.generated_text
    assert "ignored" not in result.generated_text


def test_quote_equation_figure_and_csv_regions_are_rendered(tmp_path: Path) -> None:
    _write(
        tmp_path / "references.md",
        "<!-- quote:start source -->\n> Quoted text\n<!-- quote:end source -->\n"
        "<!-- equation:start energy -->\nE = mc^2\n<!-- equation:end energy -->\n",
    )
    _write(tmp_path / "assets" / "image.png", "not parsed")
    _write(tmp_path / "assets" / "table.csv", "name,score\na,2\nb,1\n")
    deck = _write(
        tmp_path / "slides" / "deck.md",
        "<!-- quote-include: references.md#source -->\nold\n<!-- quote-include-end -->\n"
        "<!-- equation-include: references.md#energy -->\nold\n<!-- equation-include-end -->\n"
        "<!-- figure-include: assets/image.png?width=50px&caption=Chart -->\nold\n<!-- figure-include-end -->\n"
        "<!-- dataframe-include: assets/table.csv?sort_by=score&ascending=false&caption=Scores -->\nold\n<!-- dataframe-include-end -->\n",
    )

    result = synchronize_markdown(tmp_path, deck)

    assert "> Quoted text" in result.generated_text
    assert "\\[\nE = mc^2\n\\]" in result.generated_text
    assert "![width:50px](../assets/image.png)" in result.generated_text
    assert "**Chart**" in result.generated_text
    assert "| name | score |" in result.generated_text
    assert result.counts == {"dataframe": 1, "equation": 1, "figure": 1, "quote": 1}


def test_stale_artifact_is_reported_deterministically(tmp_path: Path) -> None:
    dependency = _write(tmp_path / "analysis.py", "source")
    artifact = _write(tmp_path / "table.csv", "value\n1\n")
    now = time.time()
    os.utime(artifact, (now - 20, now - 20))
    os.utime(dependency, (now, now))
    deck = _write(
        tmp_path / "deck.md",
        "<!-- dataframe-include: table.csv?depends_on=analysis.py -->\nold\n<!-- dataframe-include-end -->\n",
    )

    result = synchronize_markdown(tmp_path, deck)

    assert result.warnings == (
        "DataFrame artifact may be stale: table.csv is older than analysis.py",
    )


def test_stale_figure_is_reported_deterministically(tmp_path: Path) -> None:
    dependency = _write(tmp_path / "analysis.py", "source")
    artifact = _write(tmp_path / "chart.png", "image")
    now = time.time()
    os.utime(artifact, (now - 20, now - 20))
    os.utime(dependency, (now, now))
    deck = _write(
        tmp_path / "deck.md",
        "<!-- figure-include: chart.png?depends_on=analysis.py -->\nold\n<!-- figure-include-end -->\n",
    )

    result = synchronize_markdown(tmp_path, deck)

    assert result.warnings == (
        "Figure artifact may be stale: chart.png is older than analysis.py",
    )


def test_python_calls_are_denied_by_default_and_explicitly_allowlisted(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "safe_module.py", "def answer():\n    return 42\n")
    deck = _write(
        tmp_path / "deck.md",
        "<!-- python-call-include: module=safe_module&function=answer -->\nold\n<!-- python-call-include-end -->\n",
    )

    with pytest.raises(PythonCallDeniedError, match="disabled by default"):
        synchronize_markdown(tmp_path, deck)

    result = synchronize_markdown(tmp_path, deck, allowed_modules={"safe_module"})

    assert "42" in result.generated_text
    assert result.counts == {"python_call": 1}


def test_atomic_apply_leaves_no_temporary_file(tmp_path: Path) -> None:
    _write(tmp_path / "source.py", "# snippet:start x\nx = 1\n# snippet:end x\n")
    deck = _write(
        tmp_path / "deck.md",
        "<!-- snippet-include: source.py#x -->\n```python\nold\n```\n<!-- snippet-include-end -->\n",
    )

    synchronize_markdown(tmp_path, deck, apply=True)

    assert "x = 1" in deck.read_text(encoding="utf-8")
    assert list(tmp_path.glob(".markdown-artifact-updater-*")) == []


def test_atomic_apply_failure_preserves_original_and_removes_temporary_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write(tmp_path / "source.py", "# snippet:start x\nx = 1\n# snippet:end x\n")
    deck = _write(
        tmp_path / "deck.md",
        "<!-- snippet-include: source.py#x -->\nold\n<!-- snippet-include-end -->\n",
    )
    original = deck.read_bytes()

    def fail_replace(source: Path, destination: Path) -> None:
        raise OSError("simulated replacement failure")

    monkeypatch.setattr(updater.os, "replace", fail_replace)

    with pytest.raises(OSError, match="simulated replacement failure"):
        synchronize_markdown(tmp_path, deck, apply=True)

    assert deck.read_bytes() == original
    assert list(tmp_path.glob(".markdown-artifact-updater-*")) == []


def test_symlinked_snippet_source_is_refused_without_writing_deck(
    tmp_path: Path,
) -> None:
    outside = _write(
        tmp_path.parent / "outside.py",
        "# snippet:start private\nsecret = 'no'\n# snippet:end private\n",
    )
    link = tmp_path / "linked.py"
    try:
        os.symlink(outside, link)
    except OSError as error:
        pytest.skip(f"symlinks unavailable: {error}")
    deck = _write(
        tmp_path / "deck.md",
        "<!-- snippet-include: linked.py#private -->\nold\n<!-- snippet-include-end -->\n",
    )
    original = deck.read_bytes()

    with pytest.raises(PathSafetyError, match="escapes repository root"):
        synchronize_markdown(tmp_path, deck, apply=True)

    assert deck.read_bytes() == original


def test_notebook_snippets_do_not_execute_saved_cell_code(tmp_path: Path) -> None:
    marker = tmp_path / "notebook-executed.txt"
    _write(
        tmp_path / "analysis.ipynb",
        json.dumps(
            {
                "cells": [
                    {
                        "cell_type": "code",
                        "source": [
                            "# snippet:start cell\n",
                            f"Path({str(marker)!r}).write_text('executed')\n",
                            "# snippet:end cell\n",
                        ],
                    }
                ]
            }
        ),
    )
    deck = _write(
        tmp_path / "deck.md",
        "<!-- snippet-include: analysis.ipynb#cell -->\nold\n<!-- snippet-include-end -->\n",
    )

    result = synchronize_markdown(tmp_path, deck)

    assert "notebook-executed.txt" in result.generated_text
    assert not marker.exists()


def test_apply_preserves_crlf_outside_generated_region(tmp_path: Path) -> None:
    _write(
        tmp_path / "source.py",
        "# snippet:start x\r\nx = 1\r\n# snippet:end x\r\n",
    )
    deck = tmp_path / "deck.md"
    deck.write_bytes(
        b"before\r\n<!-- snippet-include: source.py#x -->\r\n```python\r\nold\r\n```\r\n"
        b"<!-- snippet-include-end -->\r\nafter\r\n"
    )

    synchronize_markdown(tmp_path, deck, apply=True)

    applied = deck.read_bytes()
    assert applied.startswith(b"before\r\n")
    assert applied.endswith(b"<!-- snippet-include-end -->\r\nafter\r\n")
    assert b"\n" not in applied.replace(b"\r\n", b"")


def test_provenance_reports_prior_generated_regions_and_stale_warnings(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "source.py", "# snippet:start x\nx = 1\n# snippet:end x\n")
    dependency = _write(tmp_path / "analysis.py", "source")
    artifact = _write(tmp_path / "table.csv", "value\n1\n")
    now = time.time()
    os.utime(artifact, (now - 20, now - 20))
    os.utime(dependency, (now, now))
    deck = _write(
        tmp_path / "deck.md",
        "<!-- snippet-include: source.py#x -->\n```python\nold\n```\n<!-- snippet-include-end -->\n"
        "<!-- dataframe-include: table.csv?depends_on=analysis.py -->\nold\n<!-- dataframe-include-end -->\n"
        "<!-- provenance-include -->\nold\n<!-- provenance-include-end -->\n",
    )

    result = synchronize_markdown(tmp_path, deck)

    assert "- Generated regions: `dataframe=1, snippet=1`" in result.generated_text
    assert "DataFrame artifact may be stale" in result.generated_text
    assert result.counts["provenance"] == 1
