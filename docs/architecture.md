# Architecture

## Responsibility boundary

Markdown Artifact Updater is the **materialization** step between already-produced artifacts and a hand-authored Markdown document:

```text
artifact generation → explicit-region materialization → rendering
```

It reads declared repository artifacts, refreshes only explicit generated regions, and does not own the upstream analysis/build pipeline or a downstream renderer.

## Runtime layers

- `markdown_artifact_updater.cli` owns command parsing, human-readable/JSON output, and exit status.
- `parser` recognizes explicit include regions.
- `snippets` reads named source intervals and stored notebook code cells without executing notebooks.
- `paths` confines document and artifact paths to `--repo-root`.
- `updater` resolves regions, reports staleness, and atomically replaces a target only for explicit `update --apply`.
- `handlers` render the bounded supported artifact kinds.

The normal materialization path invokes no shell and does not execute notebooks. `python-call` is a separate explicit capability requiring an exact command-line module allowlist; the allowlisted module remains responsible for its own behavior.

## Ownership model

Human-authored prose and all text outside recognized regions remain outside the updater's authority. A generated region projects its declared source; a stale warning does not authorize the updater to regenerate an artifact.

See [safety](safety.md) and [include blocks](include-blocks.md) for the public contract.
