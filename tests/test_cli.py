"""Bootstrap behavior for the public command surface."""

from __future__ import annotations

import subprocess
import sys


def _run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "marp_artifact_updater", *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def test_package_exposes_bootstrap_version() -> None:
    from marp_artifact_updater import __version__

    assert __version__ == "0.0.0.dev0"


def test_module_help_describes_synchronization_surface() -> None:
    result = _run("--help")

    assert result.returncode == 0
    assert "marp-artifact-updater" in result.stdout
    assert "synchronize" in result.stdout.lower()
    assert "check" in result.stdout
    assert "update" in result.stdout


def test_module_version_reports_package_version() -> None:
    result = _run("--version")

    assert result.returncode == 0
    assert result.stdout.strip() == "0.0.0.dev0"
