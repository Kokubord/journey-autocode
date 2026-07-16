"""Unit tests for the centralized roadmap status enum + PT labels (single source, B5)."""

from journey_core.models.roadmap_status import STATUS_LABELS_PT, Status, label_pt


def test_ten_states() -> None:
    assert len({s for s in Status}) == 10


def test_superseded_state_and_label() -> None:
    assert Status.SUPERSEDED.value == "superseded"
    assert label_pt(Status.SUPERSEDED) == "Substituída"


def test_every_state_has_a_pt_label() -> None:
    assert set(STATUS_LABELS_PT) == set(Status)
    assert label_pt(Status.IN_EXECUTION) == "Em execução"
    assert label_pt(Status.STANDBY) == "Em standby / Pausado"
