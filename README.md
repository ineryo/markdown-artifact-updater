# Marp Artifact Updater

Marp Artifact Updater deterministically refreshes explicitly delimited generated
regions in a Marp Markdown deck. It changes only region bodies, defaults to
read-only operation, and requires an explicit `--apply` before writing.

## Install and quick start

For local development or a repository checkout, install the declared development
tools and run the package in place:

```console
uv sync --group dev
uv run marp-artifact-updater --help
```

To install the current checkout as a user-facing command, use:

```console
uv tool install .
```

The complete executable presentation example is
[`examples/snippet-demo/`](examples/snippet-demo/). From the repository root:

```console
uv run marp-artifact-updater update presentation.md --repo-root examples/snippet-demo --apply
uv run marp-artifact-updater check presentation.md --repo-root examples/snippet-demo
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

`update` is a dry run unless `--apply` is supplied. The updater never changes
content outside a recognized include region.

## Supported generated regions

`snippet`, `dataframe` (CSV), `figure`, `quote`, `equation`, `provenance`, and
opt-in `python-call` regions are supported. Region syntax, source markers, and
format-specific options are documented in [include blocks](docs/include-blocks.md).

See [safety](docs/safety.md) for containment, atomic-write, notebook, and
line-ending guarantees. See [Python calls](docs/python-calls.md) before opting
in to executing a reviewed module.

## Snippet semantics

Snippets are explicit named source intervals, not parsed language constructs.
Standalone `snippet:start NAME` and `snippet:end NAME` markers are recognized
with `#`, `//`, `--`, `%`, `;`, or HTML-comment syntax. Intervals may be
disjoint, nested, or crossing; source extensions select only a conservative
Markdown fence hint. Notebooks are read as stored code cells and never run.

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

This project is licensed under the [MIT License](LICENSE). See
[licensing details](docs/licensing.md).

## Security

Please follow `SECURITY.md` for private vulnerability reporting guidance.
