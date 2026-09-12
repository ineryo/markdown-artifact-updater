---
marp: true
theme: default
paginate: true
---

# Markdown Artifact Updater

Synchronize explicit generated regions in an existing Marp presentation.

Source snippets stay current without rewriting the rest of the deck.

---

# 1. Define a named source interval

This Python source uses standalone `#` control markers.

<!-- snippet-include: source.py#normalize-name -->
```python
def normalize_name(value: str) -> str:
    """Create a presentation-safe display value."""
    return " ".join(value.split()).title()


```
<!-- snippet-include-end -->

---

# 2. Include it in the presentation

```markdown
<!-- snippet-include: source.py#normalize-name -->
```python
def normalize_name(value: str) -> str:
    """Create a presentation-safe display value."""
    return " ".join(value.split()).title()


```
<!-- snippet-include-end -->
```

The updater replaces only the bounded region body.

---

# 3. Generalized marker support

Marker extraction is language-light: a valid `--` marker works even with an
unknown source extension. The extension supplies only the fence hint.

<!-- snippet-include: query.unknown#recent-results -->
```text
SELECT name, score
FROM results
ORDER BY score DESC;
```
<!-- snippet-include-end -->

---

# 4. Run it yourself

```console
uv sync --group dev
uv run markdown-artifact-updater update presentation.md --repo-root examples/snippet-demo --apply
uv run markdown-artifact-updater check presentation.md --repo-root examples/snippet-demo
```

Run the update again: it produces no diff.
