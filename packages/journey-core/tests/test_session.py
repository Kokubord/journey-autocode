"""Tests for the Claude Code session-id capture (ATRITO-43 fix-real)."""

from __future__ import annotations

import pytest
from journey_core.session import UNRESOLVED, capture_session_id


def test_capture_returns_session_id_when_present() -> None:
    assert capture_session_id({"CLAUDE_CODE_SESSION_ID": "7cea6ef0-abc"}) == "7cea6ef0-abc"


def test_capture_unresolved_when_absent() -> None:
    # ATRITO-43: var ausente -> 'unresolved' EXPLÍCITO, nunca vazio silencioso.
    assert capture_session_id({}) == UNRESOLVED


def test_capture_unresolved_when_blank() -> None:
    assert capture_session_id({"CLAUDE_CODE_SESSION_ID": "   "}) == UNRESOLVED


def test_capture_reads_os_environ_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    assert capture_session_id() == UNRESOLVED
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "live-id")
    assert capture_session_id() == "live-id"
