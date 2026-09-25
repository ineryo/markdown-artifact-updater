# Markdown Artifact Updater

**Safely materialize already-produced technical artifacts into hand-authored Markdown.**

Markdown Artifact Updater refreshes only small, explicit generated regions for artifacts such as code snippets, CSV tables, figures, quotations, equations, and provenance. It separates three responsibilities:

```text
analysis / notebook / benchmark / source code
                    ↓
        saved artifacts: CSV, SVG, image, snippets
                    ↓
          Markdown Artifact Updater
                    ↓
             hand-authored Markdown
                    ↓
          renderer, site, or Marp CLI
```

It does not run your analysis pipeline or render the document. It materializes selected projections of files your project already produced.

## First success

A clean, ready-to-check example lives in [`examples/quickstart/`](examples/quickstart/). From a checkout:

```console
uv sync --group dev
uv run markdown-artifact-updater check report.md --repo-root examples/quickstart
```

The check is read-only and exits `0`. To see a bounded update, change the marked string in `examples/quickstart/source.py`, then run:

```console
uv run markdown-artifact-updater check report.md --repo-root examples/quickstart
uv run markdown-artifact-updater update report.md --repo-root examples/quickstart --apply
uv run markdown-artifact-updater check report.md --repo-root examples/quickstart
```

The first command reports the pending change without writing. `--apply` changes only the explicitly bounded region; surrounding report prose remains yours.

## What the updater guarantees

Its deliberately limited authority is a user benefit:

- only recognized, explicit generated regions are updater-owned;
- `check` is always read-only; writes require `update --apply`;
- text outside owned regions is byte-preserved, including existing CRLF line endings;
- paths are confined under `--repo-root`; parent traversal and escaped symlinks are refused;
- the normal no-exec materialization path invokes no shell and never executes notebooks; the separate `python-call` exception is explicitly allowlisted;
- writes are atomic and repeated successful updates are idempotent;
- `dataframe` and `figure` regions can warn that an artifact is older than a declared dependency, without regenerating it.

See [the safety model](docs/safety.md) and [generated-region reference](docs/include-blocks.md).

## When to use it

Use it when computation is already managed elsewhere and a readable, committed Markdown document needs selected saved results kept current. It is especially useful for technical reports, research repositories, CI gates, and agent-assisted workflows where an updater should have narrow, auditable mutation and execution authority.

## When not to use it

- Use Quarto, Codebraid, or notebook publishing when the document should own computation and rendering.
- Use a broad Markdown transformation/template system when arbitrary document transforms are the goal.
- Use a snippet-specific tool when tested source excerpts are the only problem.
- Use a broader Markdown workspace/lint/build system when that is the desired scope.

This project deliberately stays narrower: read an already-produced artifact, validate and materialize it into an owned region, then stop.

## Supported artifacts

- **Snippets**, including saved notebook code cells without executing notebooks.
- **Dataframes** from CSV; other table formats are deliberately unsupported.
- **Figures**, including PNG, JPEG, GIF, SVG, WebP, AVIF, HTML, and HTM.
- **Quotes**, **equations**, and **provenance** blocks.
- **Python calls** only as an opt-in exception: an exact module must be allowlisted with `--allow-python-module`. Read [Python calls](docs/python-calls.md) first.

## Marp is a flagship use case

For a Marp deck, the flow is: saved research artifacts → this updater → Marp Markdown → Marp CLI. [Marp Artifact Updater](https://github.com/ineryo/marp-artifact-updater) is the separately packaged Marp-facing sibling. The repositories currently expose closely aligned behavior, but the tracked portfolio does not formally designate either as the other's canonical implementation or promise consolidation.

## Installation and commands

This pre-alpha project is currently installed from a checkout; no registry release is claimed here.

```console
uv sync --group dev
uv run markdown-artifact-updater --help
# or install a checked-out copy as a command
uv tool install .
```

```console
markdown-artifact-updater check document.md --repo-root .
markdown-artifact-updater update document.md --repo-root .
markdown-artifact-updater update document.md --repo-root . --apply
markdown-artifact-updater check document.md --repo-root . --json
```

A pending dry-run update exits `1`; malformed or unsafe input exits `2`. `--json` provides stable machine-readable result information including region counts, warnings, paths, and SHA-256 fingerprints. Python 3.12+ and [uv](https://docs.astral.sh/uv/) are required.

## More information

- [`examples/quickstart/`](examples/quickstart/) — clean onboarding example.
- [`examples/snippet-demo/`](examples/snippet-demo/) — fuller executable Marp example.
- [`examples/basic/`](examples/basic/) — intentionally stale update fixture, not the primary onboarding path.
- [Architecture](docs/architecture.md), [contributing](CONTRIBUTING.md), [license](LICENSE), and [security reporting](SECURITY.md).

`file` regions materialize one complete repository-relative UTF-8 text file without transforming or executing it; see the [generated-region reference](docs/include-blocks.md).
