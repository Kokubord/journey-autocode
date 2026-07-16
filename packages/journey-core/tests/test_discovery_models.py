from pathlib import Path

from journey_core.models import WORKSHOP_QUESTIONS, Gap, SpecDraft, Vision, WorkshopTopic
from journey_core.parsers import parse_vision


def test_workshop_questions_cover_all_topics() -> None:
    assert set(WORKSHOP_QUESTIONS) == set(WorkshopTopic)
    assert all(q.strip() for q in WORKSHOP_QUESTIONS.values())


def test_vision_default_target_is_firm() -> None:
    v = Vision(content="visão")
    assert v.path == "docs/JOURNEY-VISION.md"
    assert v.sources == [] and v.gaps == []


def test_vision_holds_gaps_and_sources() -> None:
    v = Vision(
        content="x",
        sources=["docs/JOURNEY-VISION-v1_7.md", "HANDOVER.md"],
        gaps=[Gap(topic="diferencial", description="ainda não claro")],
    )
    assert v.gaps[0].topic == "diferencial"
    assert "HANDOVER.md" in v.sources


def test_spec_draft_path_under_drafts() -> None:
    d = SpecDraft(feature_slug="journey-foo", title="Foo", content="# draft")
    assert d.path == "specs/drafts/journey-foo.spec.md"


def test_parse_vision_missing_and_present(tmp_path: Path) -> None:
    assert parse_vision(tmp_path / "missing.md").exists is False
    doc = tmp_path / "JOURNEY-VISION.md"
    doc.write_text("# Visão\nconteúdo", encoding="utf-8")
    parsed = parse_vision(doc)
    assert parsed.exists is True
    assert parsed.content is not None and "conteúdo" in parsed.content
