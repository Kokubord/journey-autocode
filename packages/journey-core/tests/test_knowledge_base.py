"""Tests for the knowledge-base source model (feature 016, FATIA pull)."""

from journey_core.models.knowledge_base import KnowledgeBaseSource, PullKind, PullResult


def test_source_stores_url_and_defaults() -> None:
    s = KnowledgeBaseSource(url="https://example.com/journey.git")
    assert s.url == "https://example.com/journey.git"
    assert s.private is True
    assert s.kind is PullKind.GIT_CLONE


def test_source_has_no_token_field() -> None:
    # Firm invariant: the origin stores ONLY the URL — there is no token/secret field.
    fields = set(KnowledgeBaseSource.model_fields)
    assert "token" not in fields
    assert "secret" not in fields
    assert fields == {"url", "private", "kind"}


def test_pull_result_shape() -> None:
    r = PullResult(ok=True, message="ok")
    assert r.ok is True
    assert r.message == "ok"
