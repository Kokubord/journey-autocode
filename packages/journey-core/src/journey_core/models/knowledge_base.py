"""Knowledge-base source model for the agent-conducted bootstrap pull (feature 016, ADR-0024).

The pull origin is **configurable** (default = current private repo). By construction it stores
**only the URL** — there is **no token field**: the secret never lives in config/repo/commit/log
(firm invariant). Access uses the **ambient git credential**; this code never handles the secret.
The end-user least-privilege mechanism is a **deferred, OPEN integration point** (backlog Ideia 5),
not hard-coded — and **no broad access** is encoded (exactly one configured URL is pulled).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class PullKind(StrEnum):
    """How the configured origin is pulled (Spec Kit style) — both use the URL only."""

    GIT_CLONE = "git_clone"  # git clone <url> — reproducible, ambient credential
    UVX = "uvx"  # uvx --from git+<url> — Spec Kit-style packaged base


class KnowledgeBaseSource(BaseModel):
    """A configurable pull origin — **only the URL**, never a secret (firm invariant)."""

    url: str
    private: bool = True
    kind: PullKind = PullKind.GIT_CLONE


class PullResult(BaseModel):
    """Outcome of a pull attempt — never carries the secret or raw stderr."""

    ok: bool
    message: str
