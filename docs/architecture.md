# Architecture

## Bootstrap architecture

The T2 package has one intentionally small command boundary:

- `markdown_artifact_updater.__version__` is the package version.
- `markdown_artifact_updater.cli.main` owns argument parsing and terminal output.
- `markdown_artifact_updater.__main__` delegates module execution to `cli.main`.

No domain model, parser, filesystem adapter, notebook support, execution
runtime, renderer, or exporter exists in this milestone.

## Future layering

A later, separately authorized implementation is intended to keep command
parsing, deterministic planning, generated-region parsing, repository-root
containment, filesystem mutation, and optional execution controls explicit and
separate. The detailed source design remains a T3 precondition.
