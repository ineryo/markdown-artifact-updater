"""Bootstrap command-line interface; updater operations are intentionally absent."""

from __future__ import annotations

import argparse

from marp_artifact_updater import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build the intentionally small T2 command parser."""
    return argparse.ArgumentParser(
        prog="marp-artifact-updater",
        description=(
            "Bootstrap scaffold only; Marp parsing and update operations are not "
            "implemented."
        ),
    )


def main() -> int:
    """Run the bootstrap command surface."""
    parser = build_parser()
    parser.add_argument("--version", action="version", version=__version__)
    parser.parse_args()
    return 0
