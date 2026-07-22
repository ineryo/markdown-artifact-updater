# Examples

`basic/` is a minimal Marp deck with an explicit generated snippet region. Run
from the repository root:

```console
uv run marp-artifact-updater check deck.md --repo-root examples/basic
uv run marp-artifact-updater update deck.md --repo-root examples/basic --apply
uv run marp-artifact-updater check deck.md --repo-root examples/basic
```

The first command reports a pending update with exit status 1. The second
updates only the delimited region. The final check returns 0, demonstrating
idempotence.
