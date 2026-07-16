from journey_core.models.manual import (
    CANONICAL_MANUALS,
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    Manual,
    ManualType,
)


def test_four_canonical_manuals() -> None:
    assert [m.value for m in CANONICAL_MANUALS] == [
        "user",
        "admin",
        "troubleshooting",
        "technical",
    ]


def test_filename_is_english_and_path_is_flat() -> None:
    m = Manual(type=ManualType.TECHNICAL, content="x", language="pt-BR")
    assert m.filename == "technical.md"  # EN filename (FR-006)
    assert m.path == "docs/manuals/technical.md"  # flat docs/manuals/ (Vision §10.3)


def test_default_language_is_pt() -> None:
    assert Manual(type=ManualType.USER, content="x").language == "pt-BR"


def test_filename_is_english_regardless_of_content_language() -> None:
    m = Manual(type=ManualType.USER, content="x", language="en-US")
    assert m.filename == "user.md"  # FR-006: filename EN independent of content language


def test_default_and_supported_languages() -> None:
    assert DEFAULT_LANGUAGE == "pt-BR"  # FR-005 / Constituição §8.5
    assert "pt-BR" in SUPPORTED_LANGUAGES and "en-US" in SUPPORTED_LANGUAGES
    assert Manual(type=ManualType.USER, content="x").language == DEFAULT_LANGUAGE
