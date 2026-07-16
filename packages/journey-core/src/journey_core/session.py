"""Capture the Claude Code session id for the Closing pivot (ATRITO-43 fix-real).

The token pipeline (005 FR-016) binds per-session token usage to a phase via the
``sessao_id`` of the Closing block (ADR-0012). That id is the Claude Code session
id, exposed at runtime as ``CLAUDE_CODE_SESSION_ID`` (spike 2026-06-22) — a
DETERMINISTIC capture that kills ATRITO-43 (no fragile "most recent .jsonl" join).

Fail-safe (no silent empty): when the variable is absent/blank, capture returns the
EXPLICIT :data:`UNRESOLVED` sentinel — never an empty/None that looks bound. The
binding must not be able to regress to ATRITO-43 disguised as a silent blank field.

Claude-Code-only by design (ADR-0031): the var is proprietary to Claude Code (as are
the ``.jsonl`` transcripts — ADR-0010); other agents (001 FR-018, deferred) need
another capture path.
"""

from __future__ import annotations

import os
from collections.abc import Mapping

#: Explicit marker written to ``sessao_id`` when the session id cannot be captured.
UNRESOLVED = "unresolved"

_ENV_VAR = "CLAUDE_CODE_SESSION_ID"


def capture_session_id(env: Mapping[str, str] | None = None) -> str:
    """Return the current Claude Code session id, or :data:`UNRESOLVED` if absent.

    Args:
        env: Environment mapping to read (defaults to ``os.environ``). The skill must
            plumb ``CLAUDE_CODE_SESSION_ID`` through to its exec context — e.g.
            ``WSLENV=CLAUDE_CODE_SESSION_ID/u`` or an explicit assignment on the
            ``wsl`` invocation (ADR-0031).

    Returns:
        The session id from ``CLAUDE_CODE_SESSION_ID``, or ``"unresolved"`` when the
        variable is missing/blank — an EXPLICIT marker, never a silent empty string
        (ATRITO-43 must not return disguised as an empty field).
    """
    source = os.environ if env is None else env
    return (source.get(_ENV_VAR) or "").strip() or UNRESOLVED
