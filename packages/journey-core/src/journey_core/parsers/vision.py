"""Parser for a pre-existing vision document (input to consolidation, FR-005/011)."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class VisionDoc(BaseModel):
    """A pre-existing vision document discovered on disk."""

    exists: bool
    path: str | None = None
    content: str | None = None


def parse_vision(path: str | Path) -> VisionDoc:
    """Read a pre-existing vision document, if present.

    Args:
        path: Path to the vision document (e.g. ``docs/JOURNEY-VISION.md``).

    Returns:
        A :class:`VisionDoc`; ``exists`` is ``False`` when the file is absent.
    """
    file_path = Path(path)
    if not file_path.is_file():
        return VisionDoc(exists=False)
    return VisionDoc(
        exists=True, path=str(file_path), content=file_path.read_text(encoding="utf-8")
    )
