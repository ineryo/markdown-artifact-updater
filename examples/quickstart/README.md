# Quick start

`source.py` owns the marked source interval. `report.md` owns its prose; only the explicit include body is managed.

```console
uv run markdown-artifact-updater check report.md --repo-root examples/quickstart
```

Change the string in `source.py`, then run `check`, `update --apply`, and `check` as shown in the root README. The first check is read-only; the explicit apply changes only the bounded snippet body.
