# Explicit generated regions

`markdown-artifact-updater` only changes content between a recognized opening and
closing HTML comment. All text outside those regions is preserved byte-for-byte.
Paths are repository-relative and must resolve under `--repo-root`; parent-path
and symlink escapes are refused.

## Commands

```text
markdown-artifact-updater check slides/deck.md --repo-root .
markdown-artifact-updater update slides/deck.md --repo-root .       # dry run
markdown-artifact-updater update slides/deck.md --repo-root . --apply
markdown-artifact-updater check slides/deck.md --repo-root . --json
```

`check` and `update` without `--apply` never write. A needed update returns exit
status 1; malformed or unsafe input returns 2. `--json` emits stable structured
result fields and SHA-256 fingerprints.

## Supported regions

```markdown
<!-- snippet-include: src/example.py#greeting -->
```python
# generated
```
<!-- snippet-include-end -->

<!-- dataframe-include: assets/results.csv?sort_by=score&ascending=false -->
<!-- dataframe-include-end -->

<!-- figure-include: assets/chart.png?width=800px&caption=Results -->
<!-- figure-include-end -->

<!-- quote-include: references.md#source -->
<!-- quote-include-end -->

<!-- equation-include: equations.md#energy?wrap=true -->
<!-- equation-include-end -->

<!-- provenance-include -->
<!-- provenance-include-end -->
```

Snippet extraction is language-light: recognized standalone control lines use
`#`, `//`, `--`, `%`, `;`, or HTML comments, regardless of the file suffix.
Extensions affect only the suggested Markdown fence. Each name has exactly one
start and end marker; intervals may be independent, nested, or crossing. All
recognized marker control lines are omitted from rendered source.

| Source file | Markers |
| --- | --- |
| Python (`.py`) and saved notebooks (`.ipynb`) | `# snippet:start NAME` / `# snippet:end NAME` |
| C++ (`.cpp`, `.cc`, `.cxx`, `.hpp`, `.h`) | `// snippet:start NAME` / `// snippet:end NAME` |
| SQL, MATLAB, Lisp, HTML | `--`, `%`, `;`, or `<!-- snippet:start NAME -->` |

Unknown extensions may use any recognized marker family. Explicit existing
target fences are preserved; otherwise a small suffix map is used (`.h` falls
back to `c`) and then the suffix itself or `text`. Quote and equation
sources use `<!-- quote:start NAME -->` / corresponding end markers, and
equivalent `equation` markers. Saved `.ipynb` snippets read only stored
code-cell text; notebooks are never run.

CSV tables require no optional dependency. Other table formats fail with an
explicit message explaining that pandas and the corresponding reader engine are
required; this package intentionally does not install them implicitly.

Figures accept PNG, JPEG, GIF, SVG, WebP, AVIF, HTML, and HTM. HTML defaults to
an iframe and supports `mode=link`.

## Python calls

Python calls are rejected by default. They execute only when a module is named
in the deck and explicitly allowlisted on the command line:

```text
markdown-artifact-updater update deck.md --apply --allow-python-module safe_examples
```

```markdown
<!-- python-call-include: module=safe_examples&function=answer -->
<!-- python-call-include-end -->
```

Allowlisting is deliberate: never pass an unreviewed module name. There is no
shell execution and no notebook execution.

## Staleness

Use `depends_on` on CSV or figure blocks to report a deterministic warning when
the generated artifact is older than a declared source:

```markdown
<!-- dataframe-include: assets/results.csv?depends_on=analysis.py -->
<!-- dataframe-include-end -->
```

Application is atomic: content is written to a temporary file in the target
directory and replaced only after its complete write succeeds.
