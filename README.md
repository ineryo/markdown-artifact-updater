# Marp Artifact Updater

Marp Artifact Updater is a public-ready Python repository scaffold for a future
tool that will reconcile explicit generated regions in Marp Markdown.

## Bootstrap status

This T2 repository establishes package identity, governance, and development
quality controls only. It does not parse Marp, inspect or rewrite files, run
notebooks or Python calls, render output, or export artifacts.

The supported bootstrap command surface is intentionally limited to:

```console
marp-artifact-updater --help
marp-artifact-updater --version
python -m marp_artifact_updater --help
python -m marp_artifact_updater --version
```

Future operational commands and their behavior are not implemented in this
milestone. See `docs/source-design.md` for the intended design and its T3
precondition.

## Development

Python 3.12+ and [uv](https://docs.astral.sh/uv/) are required.

```console
uv sync --group dev
uv run pytest
uv run black --check .
uv run ruff check .
uv run pre-commit run --all-files
```

## Licensing

No public license is currently granted. Do not redistribute or publish this
repository until the human H1 license decision is recorded. See `LICENSE` and
`docs/licensing.md`.

## Security

Please follow `SECURITY.md` for private vulnerability reporting guidance.
