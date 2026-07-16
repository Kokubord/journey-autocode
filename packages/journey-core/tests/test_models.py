from journey_core.models import (
    AdoptionDecision,
    ArtifactType,
    ExecutionPlan,
    ProjectState,
    Runtime,
    SubPhase,
    Tier,
)


def test_project_state_defaults() -> None:
    state = ProjectState(runtime=Runtime.WSL_TUNNEL, os="Linux")
    assert state.tier is Tier.STANDARD
    assert state.language == "pt-BR"
    assert state.folder_confirmed is False


def test_execution_plan_default_subphases() -> None:
    plan = ExecutionPlan()
    assert plan.sub_phases == [SubPhase.PRE_IDE, SubPhase.NA_IDE, SubPhase.VALIDACAO]


def test_adoption_decision_message_is_english_without_trailer() -> None:
    decision = AdoptionDecision()
    assert decision.commit_message.startswith("DECISION(meta): adopt Journey methodology")
    assert "Co-Authored-By" not in decision.commit_message


def test_artifact_type_includes_roadmap_seed() -> None:
    assert ArtifactType.ROADMAP_SEED.value == "roadmap_seed"
