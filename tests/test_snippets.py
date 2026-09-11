from __future__ import annotations

import json
from pathlib import Path

import pytest

from marp_artifact_updater.model import IncludeBlockError
from marp_artifact_updater.snippets import extract_snippet, resolve_fence_language


def test_marker_families_and_unknown_suffix_are_language_light(tmp_path: Path) -> None:
    cases = {
        "py": "#",
        "c": "//",
        "js": "//",
        "rs": "//",
        "go": "//",
        "sql": "--",
        "m": "%",
        "lisp": ";",
        "html": "<!--",
    }
    for suffix, prefix in cases.items():
        path = tmp_path / f"source.{suffix}"
        end = " -->" if prefix == "<!--" else ""
        path.write_text(
            f"{prefix} snippet:start sample{end}\nbody\n{prefix} snippet:end sample{end}\n"
        )
        assert extract_snippet(path, "sample").text == "body"


def test_crossing_intervals_are_named_not_stacked(tmp_path: Path) -> None:
    path = tmp_path / "crossing.cpp"
    path.write_text(
        "// snippet:start hehe\n// snippet:start tchau\ntemplate <typename T>\n// snippet:start oi\n1+1\n// snippet:end tchau\nvoid selection_sort(T& values) {}\n// snippet:end oi\n// snippet:end hehe\n"
    )
    assert (
        extract_snippet(path, "hehe").text
        == "template <typename T>\n1+1\nvoid selection_sort(T& values) {}"
    )
    assert extract_snippet(path, "tchau").text == "template <typename T>\n1+1"
    assert extract_snippet(path, "oi").text == "1+1\nvoid selection_sort(T& values) {}"


@pytest.mark.parametrize(
    "source, message",
    [
        (
            "# snippet:start x\n# snippet:start x\n# snippet:end x\n",
            "more than one start",
        ),
        ("# snippet:start x\n", "no matching end"),
        ("# snippet:end x\n# snippet:start x\n", "end precedes start"),
    ],
)
def test_malformed_markers_are_diagnostic(
    tmp_path: Path, source: str, message: str
) -> None:
    path = tmp_path / "bad.unknown"
    path.write_text(source)
    with pytest.raises(IncludeBlockError, match=message):
        extract_snippet(path, "x")


def test_marker_like_content_is_not_a_control_line(tmp_path: Path) -> None:
    path = tmp_path / "source.py"
    path.write_text('message = "# snippet:start x"\n# ordinary snippet:start x\n')
    with pytest.raises(IncludeBlockError, match="marker not found"):
        extract_snippet(path, "x")


def test_notebook_is_read_without_execution(tmp_path: Path) -> None:
    path = tmp_path / "n.ipynb"
    path.write_text(
        json.dumps(
            {
                "cells": [
                    {
                        "cell_type": "code",
                        "source": [
                            "# snippet:start x\n",
                            "x = 1\n",
                            "# snippet:end x\n",
                        ],
                    },
                    {"cell_type": "markdown", "source": ["ignored"]},
                ]
            }
        )
    )
    assert extract_snippet(path, "x").text == "x = 1"


def test_fence_resolution_is_conservative() -> None:
    assert resolve_fence_language(Path("a.py"), "cpp") == "cpp"
    assert resolve_fence_language(Path("a.hpp"), "") == "cpp"
    assert resolve_fence_language(Path("a.h"), "") == "c"
    assert resolve_fence_language(Path("a.unknown"), "") == "unknown"
    assert resolve_fence_language(Path("README"), "") == "text"
