# Repository Agent Guidance

## Scope

This repository is independently governed. Work only within the explicitly authorized task and tracked-path boundary. Do not add a remote, publish a registry release, select a different license, or make a structural product decision without explicit human authority.

## Current product boundary

The implemented command supports deterministic `check` and explicit `update --apply` for recognized generated regions in Markdown. Preserve its narrow authority: no implicit writes, repository-root containment, no notebook execution, and no responsibility for artifact generation or rendering. The normal materialization path invokes no shell; `python-call` is a separately explicit, exact-module allowlist capability whose module behavior remains out of scope.

Do not expand this project into a general build system, renderer, or unconstrained execution framework without separately authorized scope.

## Quality

Use uv with Python 3.12+. Run pytest, Black, Ruff, and local pre-commit hooks before review. Keep the worktree clean and surface blockers explicitly.
