"""Pull the knowledge base from the configurable origin + hand off to journey-init (feature 016).

Pure command assembly + honest failure handling are **unit-tested**; the real remote pull / GitHub
auth is **manual-validated**. Firm invariants: the secret is **never** in the command, the base, a
commit, or a log; **only the URL** is used; the agent **never touches** the secret (the ambient git
credential does the auth). **No broad access** is encoded — exactly one configured origin is pulled,
and the handoff **reuses** ``journey-init`` (001), never re-implementing the install. Security by
construction: the pull/handoff refuse to write over an existing project/repo (``unsafe_dir_reason``)
and the handoff always passes an explicit ``--target`` (never the CWD).
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path

from journey_core.models.knowledge_base import KnowledgeBaseSource, PullKind, PullResult

Runner = Callable[[Sequence[str]], "subprocess.CompletedProcess[bytes]"]


def _default_runner(cmd: Sequence[str]) -> subprocess.CompletedProcess[bytes]:
    # Ambient git credential does the auth; we capture output but never surface it (no secret leak).
    return subprocess.run(cmd, capture_output=True, check=False)


def build_pull_command(source: KnowledgeBaseSource, dest: str) -> list[str]:
    """Assemble the pull command from the origin (URL only, no token; Spec Kit style)."""
    if source.kind is PullKind.UVX:
        return ["uvx", "--from", f"git+{source.url}", "journey-base", "--dest", dest]
    return ["git", "clone", "--depth", "1", source.url, dest]


def unsafe_dir_reason(path: str) -> str | None:
    """Honest refusal reason if ``path`` is unsafe for a fresh write, else ``None``.

    Unsafe = an existing **git repo** (a ``.git`` is present) or a **non-empty** directory — so the
    bootstrap never clones over, nor lets journey-init write into, an existing project. A
    non-existent path is safe (fresh). Reads only; leaks nothing.
    """
    p = Path(path)
    if not p.exists():
        return None
    if (p / ".git").exists():
        return f"Recuso: '{path}' já é um repositório git — não toco um projeto existente."
    if any(p.iterdir()):
        return f"Recuso: '{path}' não está vazia — não sobrescrevo conteúdo existente."
    return None


def auth_failure_message(source: KnowledgeBaseSource) -> str:
    """Honest detect→explain→instruct message — no mechanism prescribed, no secret leaked."""
    return (
        f"Sem acesso de leitura ao repositório da base ({source.url}). "
        "Configure o acesso de leitura a ESTE repositório e rode de novo. "
        "O Journey nunca manuseia nem armazena o seu segredo — a autenticação é a do seu git."
    )


def run_pull(
    source: KnowledgeBaseSource, dest: str, *, runner: Runner = _default_runner
) -> PullResult:
    """Run the configured pull (ambient credential). On failure → honest message; no stderr leak."""
    cmd = build_pull_command(source, dest)
    try:
        proc = runner(cmd)
    except FileNotFoundError:
        return PullResult(ok=False, message=auth_failure_message(source))
    if proc.returncode != 0:
        return PullResult(ok=False, message=auth_failure_message(source))
    return PullResult(ok=True, message="base de conhecimento puxada com sucesso")


def build_handoff_command(
    templates_dir: str, project_name: str, target_dir: str, *, remote_url: str | None = None
) -> list[str]:
    """Pull-and-invoke journey-init (001) — ALWAYS an explicit ``--target``; optional ``--remote``.

    With ``remote_url`` set, append ``--remote <url>`` so journey-init (001) does remote add +
    push — reuse, not re-implement. Journey NEVER creates the repo nor touches the account; the user
    creates it and provides the URL (the URL is not a secret).
    """
    cmd = [
        "journey-init",
        "--project-name",
        project_name,
        "--target",
        target_dir,
        "--templates",
        templates_dir,
    ]
    if remote_url:
        cmd += ["--remote", remote_url]
    return cmd


def build_conduct_plan(
    source: KnowledgeBaseSource,
    dest: str,
    project_dir: str,
    project_name: str,
    *,
    remote_url: str | None = None,
) -> list[list[str]]:
    """Ordered commands the conducting skill runs: pull → journey-init handoff (reuses builders).

    Composes :func:`build_pull_command` + :func:`build_handoff_command` — re-implements nothing. The
    skill validates each step and DELIVERS at Warmup, then STOPS; the "offer the next phase" step is
    ATRITO-70 (phase chaining), not here (no overlap).
    """
    return [
        build_pull_command(source, dest),
        build_handoff_command(
            f"{dest}/templates", project_name, project_dir, remote_url=remote_url
        ),
    ]
