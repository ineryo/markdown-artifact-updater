# Contributing

Thank you for considering a contribution.

## Current boundary

This repository is at its T2 bootstrap milestone. Contributions must not add
Marp parsing, reconciliation commands, file rewriting, notebook execution,
Python-call execution, rendering, or export before separately authorized T3
work.

## Local checks

Use Python 3.12+ and uv:

```console
uv sync --group dev
uv run pytest
uv run black --check .
uv run ruff check .
uv run pre-commit run --all-files
```

Keep changes focused, add behavior tests before implementation, and ensure the
repository is clean before requesting review.

## Licensing and publication

By contributing to this repository, you agree that your contributions will be licensed under the repository's [MIT License](LICENSE).