"""Domain models and explicit error types for Marp synchronization."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


class MarpArtifactUpdaterError(Exception):
    """Base class for expected updater failures."""


class PathSafetyError(MarpArtifactUpdaterError):
    """Raised when a requested path is outside the repository root."""


class IncludeBlockError(MarpArtifactUpdaterError):
    """Raised when an explicit generated region cannot be rendered safely."""


class PythonCallDeniedError(MarpArtifactUpdaterError):
    """Raised when a Python call block lacks explicit authorization."""


@dataclass(frozen=True)
class SynchronizationResult:
    """Deterministic result of rendering one Markdown document."""

    markdown_path: str
    changed: bool
    counts: Mapping[str, int]
    warnings: tuple[str, ...]
    original_fingerprint: str
    generated_fingerprint: str
    generated_text: str
    applied: bool

    def to_dict(self) -> dict[str, object]:
        """Return stable JSON-ready data without embedding the full document."""
        return {
            "applied": self.applied,
            "changed": self.changed,
            "counts": dict(sorted(self.counts.items())),
            "generated_fingerprint": self.generated_fingerprint,
            "markdown_path": self.markdown_path,
            "original_fingerprint": self.original_fingerprint,
            "warnings": list(self.warnings),
        }
