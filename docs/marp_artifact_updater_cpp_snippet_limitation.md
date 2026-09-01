# Limitação: snippets em comentários C++

## Contexto

O `marp-artifact-updater` foi usado para sincronizar os snippets da apresentação
Marp da atividade `assignments/01-sorting`.

Os fontes Python usam os delimitadores suportados:

```python
# snippet:start selection-sort

def selection_sort(...):
    ...

# snippet:end selection-sort
```

Para os fontes C++, o formato documentado para comentários foi usado:

```cpp
// snippet:start selection-sort

template <typename ProbeType>
void selection_sort_impl(...) {
    ...
}

// snippet:end selection-sort
```

## Problema observado

Ao atualizar ou verificar `assignments/01-sorting/slides/lista.md`, o updater
não reconhece o marcador C++:

```text
error: snippet marker not found: selection-sort
```

Comando de reprodução:

```powershell
uv run marp-artifact-updater update `
    assignments/01-sorting/slides/lista.md `
    --repo-root . `
    --apply
```

## Causa

Na versão instalada, a extração de snippets usa uma expressão regular que aceita
somente linhas iniciadas por `#`:

```python
rf"^\s*#\s*{re.escape(kind)}:start\s+{re.escape(name)}\s*$\n?"
...
rf"^\s*#\s*{re.escape(kind)}:end\s+{re.escape(name)}\s*$"
```

Assim, o updater está efetivamente limitado a marcadores no estilo Python. O
formato `// snippet:start ...`, necessário para preservar a validade sintática
dos arquivos C++, não é reconhecido.

Usar `# snippet:start ...` em um arquivo `.cpp` não é uma alternativa válida:
isso cria uma diretiva de pré-processador desconhecida e torna o código C++
inválido para compilação.

## Atualização proposta

Estender a leitura de snippets de arquivos de texto para reconhecer, além de
`#`, comentários de linha `//`. A expressão regular pode aceitar ambos os
prefixos:

```python
comment_prefix = r"(?:#|//)"

pattern = re.compile(
    rf"^\s*{comment_prefix}\s*{re.escape(kind)}:start\s+{re.escape(name)}\s*$\n?"
    rf"(?P<body>.*?)"
    rf"^\s*{comment_prefix}\s*{re.escape(kind)}:end\s+{re.escape(name)}\s*$",
    re.MULTILINE | re.DOTALL,
)
```

Idealmente, os prefixos aceitos devem depender da extensão do arquivo, para
evitar que uma diretiva de linguagem seja confundida com um comentário. Uma
primeira cobertura suficiente seria:

| Extensão | Marcador aceito |
| --- | --- |
| `.py` | `# snippet:start/end ...` |
| `.cpp`, `.cc`, `.cxx`, `.hpp`, `.h` | `// snippet:start/end ...` |

## Testes de regressão sugeridos

1. Um arquivo Python com marcadores `#` continua sendo extraído corretamente.
2. Um arquivo C++ com marcadores `//` é extraído corretamente.
3. O conteúdo retornado não inclui as linhas de marcador.
4. Um marcador ausente continua retornando `snippet marker not found: <nome>`.
5. Um arquivo C++ com `# snippet:start/end` não precisa ser suportado, pois não
   representa um comentário C++ válido.

## Impacto neste repositório

Os marcadores C++ foram mantidos como comentários válidos `//`, e os marcadores
Python usam `#`. A apresentação [lista.md](../assignments/01-sorting/slides/lista.md)
já referencia os cinco pares de snippets, mas a sincronização dos blocos C++
depende dessa atualização do updater.
