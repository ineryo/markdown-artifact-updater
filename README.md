# Marp Artifact Updater

Marp Artifact Updater deterministically refreshes explicitly delimited generated
regions in a Marp Markdown deck. It changes only region bodies, defaults to
read-only operation, and requires an explicit `--apply` before writing.

## Quick start

The included example is executable from the repository root:

```console
uv run marp-artifact-updater check deck.md --repo-root examples/basic
uv run marp-artifact-updater update deck.md --repo-root examples/basic --apply
uv run marp-artifact-updater check deck.md --repo-root examples/basic
```

The first `check` exits 1 because the region is stale. After `update --apply`,
the final `check` exits 0. Repeating the update makes no further change.

`python -m marp_artifact_updater` provides the same command surface.

## Commands

```console
marp-artifact-updater check slides/deck.md --repo-root .
marp-artifact-updater update slides/deck.md --repo-root .       # dry run
marp-artifact-updater update slides/deck.md --repo-root . --apply
marp-artifact-updater check slides/deck.md --repo-root . --json
```

An update needed in dry-run mode exits 1. Invalid or unsafe input exits 2.
`--json` produces a stable result object containing change state, per-region
counts, warnings, paths, and SHA-256 fingerprints.

## Supported generated regions

`snippet`, `dataframe` (CSV), `figure`, `quote`, `equation`, `provenance`, and
opt-in `python-call` regions are supported. Region syntax, source markers, and
format-specific options are documented in [include blocks](docs/include-blocks.md).

See [safety](docs/safety.md) for containment, atomic-write, notebook, and
line-ending guarantees. See [Python calls](docs/python-calls.md) before opting
in to executing a reviewed module.

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
