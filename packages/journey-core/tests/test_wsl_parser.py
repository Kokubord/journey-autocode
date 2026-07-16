"""Tests for the ``wsl -l -v`` parser (feature 015, FATIA 1)."""

from journey_core.parsers.wsl import parse_wsl_list_verbose

_SAMPLE = "  NAME      STATE      VERSION\n* Ubuntu    Running    2\n  Debian    Stopped    1\n"


def test_parses_distros_and_default() -> None:
    listing = parse_wsl_list_verbose(_SAMPLE)
    assert listing.default_distro == "Ubuntu"
    assert [d.name for d in listing.distros] == ["Ubuntu", "Debian"]
    assert listing.has_wsl2_default is True


def test_tolerates_utf16_null_bytes() -> None:
    raw = "\x00".join(_SAMPLE)  # mimic UTF-16 null padding between chars
    listing = parse_wsl_list_verbose(raw)
    assert listing.default_distro == "Ubuntu"
    assert listing.distros[0].version == 2


def test_default_marker_assigns_default() -> None:
    listing = parse_wsl_list_verbose("* Debian Running 2\n  Ubuntu Stopped 2\n")
    assert listing.default_distro == "Debian"


def test_v1_default_is_not_wsl2() -> None:
    listing = parse_wsl_list_verbose("* Ubuntu Running 1\n")
    assert listing.has_wsl2_default is False


def test_empty_input_yields_empty_listing() -> None:
    listing = parse_wsl_list_verbose("")
    assert listing.distros == []
    assert listing.default_distro is None


def test_no_installed_distributions_message_is_ignored() -> None:
    listing = parse_wsl_list_verbose(
        "Windows Subsystem for Linux has no installed distributions.\n"
    )
    assert listing.distros == []
    assert listing.default_distro is None


def test_blank_and_short_lines_are_skipped() -> None:
    listing = parse_wsl_list_verbose("\n  \n* Ubuntu Running 2\nshort line\n")
    assert [d.name for d in listing.distros] == ["Ubuntu"]
