from journey_core.handshake import OpeningHandshake, build_opening_handshake


def test_build_opening_handshake() -> None:
    handshake = build_opening_handshake(
        handover_read=True,
        highest_adr="ADR-0015",
        constitution_version="v1.3",
        git_synced=True,
        summary="Build em curso",
    )
    assert isinstance(handshake, OpeningHandshake)
    assert handshake.highest_adr == "ADR-0015"
    assert handshake.git_synced is True
