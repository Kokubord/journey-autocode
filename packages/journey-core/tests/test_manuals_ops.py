from pathlib import Path

import pytest
from journey_core.exceptions import WriteRoutingError
from journey_core.manuals_ops import write_manual
from journey_core.models.manual import Manual, ManualType


def test_writes_manual_to_flat_docs_manuals(tmp_path: Path) -> None:
    p = write_manual(tmp_path, Manual(type=ManualType.USER, content="# Manual\nVer ADR-0001."))
    assert p == tmp_path / "docs" / "manuals" / "user.md"
    assert p.read_text(encoding="utf-8") == "# Manual\nVer ADR-0001."


def test_writes_all_four_with_english_filenames(tmp_path: Path) -> None:
    for t in ManualType:
        write_manual(tmp_path, Manual(type=t, content="x"))
    names = sorted(p.name for p in (tmp_path / "docs" / "manuals").iterdir())
    assert names == ["admin.md", "technical.md", "troubleshooting.md", "user.md"]


def test_unc_path_is_vetoed() -> None:
    with pytest.raises(WriteRoutingError):
        write_manual("//wsl.localhost/Ubuntu/x", Manual(type=ManualType.USER, content="x"))
