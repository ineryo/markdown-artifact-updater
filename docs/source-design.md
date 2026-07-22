# Source design and migration boundary

## Intended future behavior

The future updater is intended to reconcile explicit generated regions in Marp
Markdown. Its accepted design includes snippets, tables, figures, quotes,
equations, provenance, and optional Python calls. It will require a check or
dry-run phase before apply, no notebook execution, repository-root containment,
deterministic output, atomic writes, and Python calls disabled by default.

## T3 precondition

The detailed prior README/appendix implementation has not been imported into
this repository. Importing and reconciling that prior README/appendix design is
a T3 precondition. T2 neither copies nor implements its code or behavior.

Any later implementation must reconcile the imported source material with this
repository's independently reviewed governance and public-readiness boundary.
