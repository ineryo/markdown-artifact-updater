# Repository Agent Guidance

## Scope

This repository is independently governed. Work only within the explicitly
authorized milestone and tracked-path boundary. Do not add a remote, push,
publish, select a final license, or implement a later milestone without human
authority.

## T2 boundary

T2 supports only package importability, help, version reporting, and equivalent
`python -m marp_artifact_updater` behavior. Marp parsing, check/update behavior,
file rewriting, notebooks, Python calls, rendering, and export are prohibited.

## Quality

Use uv with Python 3.12+. Run pytest, Black, Ruff, and local pre-commit hooks
before review. Keep the worktree clean and surface blockers explicitly.
