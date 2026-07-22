# Python calls

Python-call regions are an opt-in execution boundary. They are disabled by
default, even for a module located under the repository root.

```markdown
<!-- python-call-include: module=safe_examples&function=answer -->
<!-- python-call-include-end -->
```

To render this region, pass the exact module name on the command line:

```console
marp-artifact-updater update deck.md --repo-root . --apply \
  --allow-python-module safe_examples
```

The allowlist is exact: allowing `safe_examples` does not authorize a different
module. Calls receive JSON `args` (an array) and `kwargs` (an object) when those
options are present. The selected function runs in the current Python process,
so allow only reviewed, deterministic modules. Do not use this feature for
untrusted decks or repositories.

Notebook snippets are not Python calls. They read saved code-cell source only
and never execute a kernel.
