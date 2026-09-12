# Executable snippet demo

- `presentation.md` is a five-slide Marp deck.
- `source.py` supplies the `#`-marked Python interval.
- `query.unknown` supplies a `--`-marked interval from an unknown extension.

From the repository root:

```console
uv sync --group dev
uv run marp-artifact-updater update presentation.md --repo-root examples/snippet-demo --apply
uv run marp-artifact-updater check presentation.md --repo-root examples/snippet-demo
```

The update replaces only the two generated include bodies. Run the update a
second time and `git diff -- examples/snippet-demo/presentation.md` is empty.
