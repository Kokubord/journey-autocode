from journey_core.models import PHASE_CHECKLISTS, Phase, PhaseState, checklist_for


def test_six_canonical_phases() -> None:
    assert [p.value for p in Phase] == [
        "warmup",
        "foundation",
        "discovery",
        "build",
        "release",
        "run",
    ]


def test_label_is_capitalized() -> None:
    assert Phase.BUILD.label == "Build"
    assert Phase.DISCOVERY.label == "Discovery"


def test_marker_includes_phase_and_slug() -> None:
    state = PhaseState(phase=Phase.BUILD, slug="dashboard")
    assert state.marker == "Build — sub-fase **dashboard** (ativa)"
    assert state.active is True
    assert state.previous is None


def test_previous_preserved() -> None:
    state = PhaseState(phase=Phase.BUILD, slug="x", previous="Discovery — workshop (ativa)")
    assert state.previous == "Discovery — workshop (ativa)"


def test_checklists_cover_all_phases_and_nonempty() -> None:
    assert set(PHASE_CHECKLISTS) == set(Phase)
    for phase in Phase:
        items = checklist_for(phase)
        assert items and all(line.strip() for line in items)
