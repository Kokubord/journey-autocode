"""Parser for Closing Handshake blocks in HANDOVER (pivot — ADR-0012)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, cast

import yaml
from pydantic import BaseModel

_YAML_BLOCK = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)


class ClosingBlock(BaseModel):
    """A parsed Closing Handshake block (methodology §12.1, ADR-0012)."""

    fase: str | None = None
    subfase: str | None = None
    sessao_id: str | None = None
    timestamp: str | None = None
    classe_sessao: str | None = None
    adrs_criados: list[str] = []


def _opt_str(value: Any) -> str | None:
    return None if value is None else str(value)


def parse_closing_blocks(path: str | Path) -> list[ClosingBlock]:
    """Extract Closing Handshake blocks from a HANDOVER.md file.

    Only fenced ``yaml`` blocks carrying the ``fase`` pivot key are returned;
    other yaml blocks are ignored. Field values are coerced by pydantic, so an
    unquoted yaml date in ``timestamp`` becomes a string. Degrades gracefully: an
    absent file yields an empty list (Edge Case — pre-ADR-0012 entries have no block).

    Args:
        path: Path to the HANDOVER.md file.

    Returns:
        The Closing blocks found, in document order.
    """
    file_path = Path(path)
    if not file_path.is_file():
        return []
    text = file_path.read_text(encoding="utf-8")
    blocks: list[ClosingBlock] = []
    for match in _YAML_BLOCK.finditer(text):
        loaded: Any = yaml.safe_load(match.group(1))
        if not isinstance(loaded, dict):
            continue
        data = cast(dict[str, Any], loaded)
        if "fase" not in data:
            continue
        blocks.append(
            ClosingBlock(
                fase=_opt_str(data.get("fase")),
                subfase=_opt_str(data.get("subfase")),
                sessao_id=_opt_str(data.get("sessao_id")),
                timestamp=_opt_str(data.get("timestamp")),
                classe_sessao=_opt_str(data.get("classe_sessao")),
                adrs_criados=data.get("adrs_criados") or [],
            )
        )
    return blocks
