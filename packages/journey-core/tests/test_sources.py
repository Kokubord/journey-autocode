from pathlib import Path

from journey_core.parsers.sources import source_digest


def _repo() -> Path:
    return Path(__file__).resolve().parents[3]


def test_digest_lists_real_sources() -> None:
    d = source_digest(_repo())
    assert d.project == "journey"
    assert any(a.id == "ADR-0018" for a in d.adrs)  # ADRs listed
    assert any(s.id.startswith("008") for s in d.specs)  # specs listed
    assert any("journey_core" in m for m in d.modules)  # modules listed
    assert d.tests  # test files listed


def test_no_sentinel_tagged_tests_yields_empty() -> None:
    # the Journey repo tags no test as sentinel -> empty (skill section is empty/warned)
    assert source_digest(_repo()).sentinel_tests == []


def test_digest_on_empty_repo_is_safe(tmp_path: Path) -> None:
    d = source_digest(tmp_path)
    assert d.adrs == [] and d.specs == [] and d.modules == []
    assert d.current_phase is None  # parse_handover tolerates an absent HANDOVER
