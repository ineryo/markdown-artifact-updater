"""Safe command-line boundary for deterministic Marp synchronization."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from markdown_artifact_updater import __version__
from markdown_artifact_updater.model import MarpArtifactUpdaterError
from markdown_artifact_updater.updater import synchronize_markdown


def build_parser() -> argparse.ArgumentParser:
    """Build command parsing with dry-run behavior as the default."""
    parser = argparse.ArgumentParser(
        prog="markdown-artifact-updater",
        description="Synchronize explicit generated regions in a Markdown file.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "update"):
        command = commands.add_parser(name)
        command.add_argument("markdown_file")
        command.add_argument("--repo-root", default=".")
        command.add_argument("--apply", action="store_true")
        command.add_argument("--json", action="store_true", dest="as_json")
        command.add_argument(
            "--allow-python-module", action="append", default=[], metavar="MODULE"
        )
    return parser


def main() -> int:
    """Run a check or an explicitly applied update without hidden writes."""
    arguments = build_parser().parse_args()
    try:
        result = synchronize_markdown(
            Path(arguments.repo_root),
            arguments.markdown_file,
            apply=arguments.command == "update" and arguments.apply,
            allowed_modules=set(arguments.allow_python_module),
        )
    except MarpArtifactUpdaterError as error:
        if arguments.as_json:
            print(json.dumps({"error": str(error)}, sort_keys=True))
        else:
            print(f"error: {error}")
        return 2
    if arguments.as_json:
        print(json.dumps(result.to_dict(), sort_keys=True))
    elif result.changed and not result.applied:
        print(f"Dry run: {result.markdown_path} would change.")
    else:
        print(f"No changes required: {result.markdown_path}.")
    return 1 if result.changed and not result.applied else 0
