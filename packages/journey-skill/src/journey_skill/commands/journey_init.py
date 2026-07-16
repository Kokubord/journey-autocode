# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false
"""journey-init — install the Journey methodology into a project (001: US1-US4 + Polish).

Three conducted sub-phases (FR-005, methodology §3.1):
- **Pré-IDE (US2):** environment diagnosis + folder gate (1st gate) + cloud-sync alert +
  stop-and-self-heal; writes are routed through the repository runtime and UNC paths are
  vetoed (ADR-0004, journey_core.writer).
- **Na-IDE (US1/US4):** git init, Spec Kit, materialize the 12 canonical artifacts
  (FR-008) — **non-destructive**: existing files are preserved, ``CLAUDE.md`` is merged via
  a managed block (ATRITO-16), re-run is idempotent (FR-014). First ``DECISION`` commit.
- **Validação (US3):** verify the artifacts that enable the Opening Handshake (FR-015).

Templates render with a stdlib substitution (no jinja2 dependency — §3.5).
"""

from __future__ import annotations

import platform
import re
import shutil
import subprocess
from datetime import date as date_cls
from pathlib import Path
from typing import Annotated, Any

import typer
from git import Repo
from journey_core.exceptions import JourneyError
from journey_core.models.execution_plan import Checkpoint, ExecutionPlan, Step, SubPhase
from journey_core.models.project_state import ProjectState, Runtime
from journey_core.parsers import parse_handover
from journey_core.writer import detect_runtime, guard_write_target

_VAR_RE = re.compile(r"{{\s*(\w+)\s*}}")
_COMMIT_MESSAGE = "DECISION(meta): adopt Journey methodology [ADR-0001]"
_CLAUDE_BEGIN = "<!-- BEGIN JOURNEY (managed — não editar à mão) -->"
_CLAUDE_END = "<!-- END JOURNEY (managed) -->"
_CLOUD_MARKERS = ("onedrive", "dropbox", "icloud", "google drive", "googledrive")
_CONSTITUTION_DEST = ".specify/memory/constitution.md"
_SPECKIT_PLACEHOLDER_MARKERS = ("[PROJECT_NAME]", "[PRINCIPLE_1_NAME]")
#: Conductor skills NOT embarked into a target (no re-bootstrap from within — ADR-0050).
_CONDUCTOR_EXCLUDE = frozenset({"journey-bootstrap"})

# (template filename, target path relative to the project root) — FR-008
_ARTIFACTS: list[tuple[str, str]] = [
    ("handover.md.jinja", "HANDOVER.md"),
    ("agents.md.jinja", "AGENTS.md"),
    ("claude.md.jinja", "CLAUDE.md"),
    ("gitignore.jinja", ".gitignore"),
    ("readme.md.jinja", "README.md"),
    ("contributing.md.jinja", "CONTRIBUTING.md"),
    # Render local de roadmap DESABILITADO (feature 023 / ATRITO-78 / ADR-0032): o roadmap
    # renderizado vive no Site, não localmente. Os templates seguem em templates/ (reversível):
    #   ("roadmap.md.jinja", "docs/ROADMAP.md"),
    #   ("roadmap.seed.yaml.jinja", "roadmap.yaml"),
    ("adr-0001.md.jinja", "docs/adr/0001-adopcao-journey.md"),
    ("constitution.placeholder.md.jinja", ".specify/memory/constitution.md"),
    ("ci.yml.jinja", ".github/workflows/ci.yml"),
    ("roadmap-format-contract.md.jinja", "docs/ROADMAP-FORMAT-CONTRACT.md"),
]

#: Public alias of the canonical artifact set — reused by feature 002 (journey-upgrade).
ARTIFACTS: list[tuple[str, str]] = _ARTIFACTS


def _bundled_dir() -> Path | None:
    """Package-bundled data (templates + skills) — present only in a built/installed wheel (024)."""
    bundled = Path(__file__).resolve().parent.parent / "_bundled"
    return bundled if bundled.is_dir() else None


def default_templates_dir() -> Path:
    """Locate templates/: bundled package-data (installed wheel) or the repo root (dev/dogfooding).

    Bundling makes a global journey-init/journey-upgrade self-contained (no base clone needed —
    feature 024). Falls back to the repo layout when running from a source checkout.
    """
    bundled = _bundled_dir()
    if bundled is not None and (bundled / "templates").is_dir():
        return bundled / "templates"
    return Path(__file__).resolve().parents[5] / "templates"


def render(text: str, context: dict[str, str]) -> str:
    """Substitute ``{{ var }}`` placeholders from ``context`` (stdlib, no jinja2)."""
    return _VAR_RE.sub(lambda m: context.get(m.group(1), m.group(0)), text)


def build_plan() -> ExecutionPlan:
    """Declare the conducted plan over the three sub-phases (FR-005)."""
    return ExecutionPlan(
        sub_phases=[SubPhase.PRE_IDE, SubPhase.NA_IDE, SubPhase.VALIDACAO],
        steps=[
            Step(description="diagnose environment + confirm folder", sub_phase=SubPhase.PRE_IDE),
            Step(
                description="git init + Spec Kit + materialize artifacts", sub_phase=SubPhase.NA_IDE
            ),
            Step(description="first DECISION commit + push", sub_phase=SubPhase.NA_IDE),
            Step(description="operational validation", sub_phase=SubPhase.VALIDACAO),
        ],
        checkpoints=[
            Checkpoint(label="1º gate: confirmar pasta/projeto correto"),
            Checkpoint(label="revisar artefatos antes do commit"),
        ],
    )


# --- US2: Pré-IDE — diagnosis + gates ---------------------------------------


def _preexisting_artifacts(target: Path) -> list[str]:
    return [dest for _, dest in _ARTIFACTS if (target / dest).exists()]


def diagnose_environment(target: Path, *, language: str = "pt-BR") -> ProjectState:
    """Diagnose the environment before any write (FR-001/US2 + state detection US4)."""
    ssh_dir = Path.home() / ".ssh"
    ssh_ok = ssh_dir.is_dir() and any(ssh_dir.glob("id_*"))
    return ProjectState(
        runtime=detect_runtime(),
        os=f"{platform.system()} {platform.release()}",
        git_present=shutil.which("git") is not None,
        spec_kit_present=shutil.which("specify") is not None or (target / ".specify").is_dir(),
        language=language,
        ssh_ok=ssh_ok,
        preexisting_artifacts=_preexisting_artifacts(target),
        folder_confirmed=False,
    )


def is_cloud_sync(path: Path) -> bool:
    """Return whether ``path`` sits under a cloud-sync folder (FR-003)."""
    lowered = str(path).lower()
    return any(marker in lowered for marker in _CLOUD_MARKERS)


def environment_problems(state: ProjectState) -> list[str]:
    """Return hard environment problems that block the install (stop-and-self-heal, FR-002)."""
    problems: list[str] = []
    if not state.git_present:
        problems.append("git não encontrado no PATH")
    if state.runtime == Runtime.WINDOWS:
        problems.append("runtime Windows: escreva pelo runtime onde o repositório vive (ADR-0004)")
    return problems


# --- US4: non-destructive materialization + CLAUDE.md merge -----------------


def merge_claude(existing: str | None, journey: str) -> str:
    """Merge the Journey block into a CLAUDE.md, preserving user content (ATRITO-16).

    Mechanical and idempotent: the Journey portion lives between managed markers; a
    re-run replaces only that block; user content outside the markers is never touched.
    """
    block = f"{_CLAUDE_BEGIN}\n{journey.strip()}\n{_CLAUDE_END}"
    if existing is None:
        return block + "\n"
    if _CLAUDE_BEGIN in existing and _CLAUDE_END in existing:
        pre = existing.split(_CLAUDE_BEGIN)[0]
        post = existing.split(_CLAUDE_END, 1)[1]
        return f"{pre}{block}{post}"
    return f"{existing.rstrip()}\n\n{block}\n"


def materialize_artifacts(
    templates_dir: Path, target: Path, context: dict[str, str], *, overwrite: bool = False
) -> dict[str, list[str]]:
    """Render and write the canonical artifacts (FR-008), non-destructively (FR-014).

    Existing files are preserved (never overwritten blindly); ``CLAUDE.md`` is merged via
    the managed block. Returns which artifacts were created / preserved / merged.
    """
    created: list[str] = []
    preserved: list[str] = []
    merged: list[str] = []
    for template_name, dest in _ARTIFACTS:
        source = templates_dir / template_name
        if not source.is_file():
            raise JourneyError(f"Missing template: {source}")
        rendered = render(source.read_text(encoding="utf-8"), context)
        out = guard_write_target(target / dest)
        out.parent.mkdir(parents=True, exist_ok=True)
        if dest == "CLAUDE.md":
            existing = out.read_text(encoding="utf-8") if out.exists() and not overwrite else None
            new_text = merge_claude(existing, rendered)
            if out.exists() and out.read_text(encoding="utf-8") == new_text:
                preserved.append(dest)
            else:
                out.write_text(new_text, encoding="utf-8")
                (merged if existing is not None else created).append(dest)
        elif (
            dest == _CONSTITUTION_DEST
            and out.exists()
            and not overwrite
            and _is_speckit_placeholder(out.read_text(encoding="utf-8"))
        ):
            # Journey's placeholder wins over Spec Kit's generic (ATRITO-93): specify init
            # writes a generic constitution first, so a plain preserve would drop Journey's.
            if out.read_text(encoding="utf-8") == rendered:
                preserved.append(dest)
            else:
                out.write_text(rendered, encoding="utf-8")
                merged.append(dest)
        elif out.exists() and not overwrite:
            preserved.append(dest)
        else:
            out.write_text(rendered, encoding="utf-8")
            created.append(dest)
    archive = guard_write_target(target / "docs/handover-archive")
    archive.mkdir(parents=True, exist_ok=True)
    keep = archive / ".gitkeep"
    if keep.exists():
        preserved.append("docs/handover-archive/.gitkeep")
    else:
        keep.write_text("", encoding="utf-8")
        created.append("docs/handover-archive/.gitkeep")
    return {"created": created, "preserved": preserved, "merged": merged}


def _is_speckit_placeholder(text: str) -> bool:
    """Whether a constitution file is still Spec Kit's untouched generic template (ATRITO-93)."""
    return any(marker in text for marker in _SPECKIT_PLACEHOLDER_MARKERS)


# --- Conductors: embark the journey-* skills into the target (ADR-0050) ------


def conductor_skills_source(templates_dir: Path) -> Path:
    """Locate the conducting skills — bundled sibling, or the base/dev .claude/skills layout."""
    bundled_sibling = templates_dir.parent / "skills"
    if bundled_sibling.is_dir():
        return bundled_sibling
    return templates_dir.parent / ".claude" / "skills"


def materialize_conductors(templates_dir: Path, target: Path) -> dict[str, list[str]]:
    """Copy the ``journey-*`` conducting skills into ``target/.claude/skills`` (ADR-0050).

    Journey owns the ``journey-*`` namespace: those dirs are refreshed so ``journey-upgrade``
    propagates updates; ``journey-bootstrap`` is excluded (no re-bootstrap from within an
    installed project); the user's own (non ``journey-*``) skills are never touched. Missing
    source (no base alongside the templates) degrades honestly to a no-op.
    """
    source = conductor_skills_source(templates_dir)
    copied: list[str] = []
    if not source.is_dir():
        return {"copied": copied}
    dest_root = guard_write_target(target / ".claude" / "skills")
    dest_root.mkdir(parents=True, exist_ok=True)
    for skill_dir in sorted(p for p in source.iterdir() if p.is_dir()):
        name = skill_dir.name
        if not name.startswith("journey-") or name in _CONDUCTOR_EXCLUDE:
            continue
        shutil.copytree(skill_dir, dest_root / name, dirs_exist_ok=True)
        copied.append(name)
    return {"copied": copied}


def conductor_cli_present() -> bool:
    """Whether the ``journey-*`` CLIs the conductors call are on PATH (ADR-0050)."""
    return shutil.which("journey-roadmap") is not None


def conductor_install_hint(base_dir: Path | None) -> str:
    """Consent-based hint: install the journey-* CLIs from WHEELS, self-contained (ADR-0050).

    Installing from the workspace source makes journey-core EDITABLE, locking the CLIs to the base
    clone (FR-006). Wheels copy journey-core in, so the base is disposable.
    """
    if base_dir is None:
        return (
            "condutores: skills journey-* copiadas, mas os CLIs journey-* NÃO estão no PATH. "
            "Instale-os como ferramenta global (com o seu consentimento) a partir dos WHEELS "
            "(`uv build --wheel` → `uv tool install --find-links <dist>`), nunca do source "
            "editable (prende os CLIs à base). Sem isso, os comandos que as skills chamam falham."
        )
    pkgs = base_dir / "packages"
    dist = base_dir / "dist"
    return (
        "condutores: skills journey-* copiadas, mas os CLIs journey-* NÃO estão no PATH. "
        "Ative-os como ferramenta global SELF-CONTAINED (com o seu consentimento) via WHEELS — "
        "instalar do source editable prende journey-core à base e quebra ao apagá-la (FR-006):\n"
        f"    uv build --wheel {pkgs}/journey-core --out-dir {dist}\n"
        f"    uv build --wheel {pkgs}/journey-skill --out-dir {dist}\n"
        f"    uv build --wheel {pkgs}/journey-roadmap --out-dir {dist}\n"
        f"    uv tool install --find-links {dist} journey-skill\n"
        f"    uv tool install --find-links {dist} journey-roadmap\n"
        "aí journey-core é COPIADO (sem .pth editable) e a base pode ser descartada."
    )


# --- US3: operational validation --------------------------------------------


def validate_installation(target: Path) -> tuple[bool, list[str]]:
    """Verify the artifacts that enable the Opening Handshake (FR-015/US3)."""
    problems: list[str] = []
    claude = target / "CLAUDE.md"
    if not claude.is_file() or "Opening Handshake" not in claude.read_text(encoding="utf-8"):
        problems.append("CLAUDE.md sem a seção Opening Handshake")
    handover = parse_handover(target / "HANDOVER.md")
    if not handover.exists:
        problems.append("HANDOVER.md ausente")
    elif handover.current_phase is None:
        problems.append("HANDOVER.md sem campo 'Fase atual' parseável")
    return (not problems, problems)


# --- git plumbing -----------------------------------------------------------


def _git_init(target: Path, remote: str, username: str, email: str) -> Repo:
    repo = Repo.init(target, initial_branch="main")
    with repo.config_writer() as cfg:
        if username:
            cfg.set_value("user", "name", username)
        if email:
            cfg.set_value("user", "email", email)
    if remote and "origin" not in [r.name for r in repo.remotes]:
        repo.create_remote("origin", remote)
    return repo


def _install_spec_kit(target: Path) -> bool:
    try:
        subprocess.run(
            ["specify", "init", "--here", "--ai", "claude", "--force", "--script", "sh"],
            cwd=target,
            check=True,
            capture_output=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False
    return True


def _stage_installables(repo: Repo, target: Path) -> None:
    """Stage only what the install produced — never a blanket ``git add -A`` (§16 git conduzido).

    Keeps a stray base clone sitting in the project from being swept into the first commit (024).
    """
    paths = [dest for _, dest in _ARTIFACTS]
    paths += ["docs", ".claude/skills", ".specify", ".github"]
    existing = [p for p in paths if (target / p).exists()]
    if existing:
        repo.git.add("--", *existing)


# --- orchestration ----------------------------------------------------------


def run_init(
    *,
    project_name: str,
    target: Path,
    language: str = "pt-BR",
    remote: str = "",
    username: str = "",
    email: str = "",
    templates_dir: Path | None = None,
    yes: bool = False,
    skip_spec_kit: bool = False,
) -> dict[str, Any]:
    """Install the methodology into ``target`` (conducted, checkpoint-gated, idempotent)."""
    tdir = templates_dir or default_templates_dir()
    target = target.resolve()
    context = {
        "project_name": project_name,
        "language": language,
        "date": date_cls.today().isoformat(),
        "remote_url": remote or "(remoto a definir)",
    }

    def gate(label: str) -> None:
        typer.echo(f"  checkpoint: {label}")
        if not yes and not typer.confirm("  prosseguir?", default=True):
            raise typer.Abort()

    # --- Pré-IDE (US2) ---
    state = diagnose_environment(target, language=language)
    typer.echo(f"journey-init: {project_name} -> {target}")
    typer.echo(
        f"  ambiente: runtime={state.runtime.value} os={state.os} "
        f"git={state.git_present} ssh={state.ssh_ok} spec_kit={state.spec_kit_present}"
    )
    if state.preexisting_artifacts:
        typer.echo(
            f"  estado: {len(state.preexisting_artifacts)} artefato(s) pré-existente(s) "
            "— re-run seguro (não sobrescreve)"
        )
    if not state.ssh_ok:
        typer.echo("  aviso: nenhuma chave SSH em ~/.ssh — o push pode falhar")
    if is_cloud_sync(target):
        typer.echo("  AVISO: pasta em cloud-sync — recomendado filesystem nativo (FR-003)")
    problems = environment_problems(state)
    if problems:
        for problem in problems:
            typer.echo(f"  FALHA DE AMBIENTE: {problem}")
        typer.echo("  stop-and-self-heal: corrija o ambiente e re-rode o journey-init.")
        raise typer.Abort()
    gate("1º gate: confirmar pasta/projeto correto")
    state.folder_confirmed = True

    # --- Na-IDE (US1/US4) ---
    target.mkdir(parents=True, exist_ok=True)
    repo = _git_init(target, remote, username, email)
    if skip_spec_kit:
        typer.echo("  Spec Kit: pulado (--skip-spec-kit)")
        spec_kit_ok = False
    else:
        spec_kit_ok = _install_spec_kit(target)
        typer.echo("  Spec Kit: instalado" if spec_kit_ok else "  Spec Kit: indisponível (pulado)")
    result = materialize_artifacts(tdir, target, context)
    typer.echo(
        f"  artefatos: {len(result['created'])} criados, "
        f"{len(result['preserved'])} preservados, {len(result['merged'])} merge"
    )
    conductors = materialize_conductors(tdir, target)
    typer.echo(f"  condutores: {len(conductors['copied'])} skill(s) journey-* embarcada(s)")
    if conductors["copied"] and not conductor_cli_present():
        typer.echo("  " + conductor_install_hint(tdir.parent))
    gate("revisar artefatos antes do commit")
    _stage_installables(repo, target)
    if repo.head.is_valid() and not repo.index.diff("HEAD"):
        committed = False
        sha = str(repo.head.commit.hexsha)
        typer.echo("  commit: nada a commitar (re-run idempotente)")
    else:
        commit = repo.index.commit(_COMMIT_MESSAGE)
        sha = str(commit.hexsha)
        committed = True
        typer.echo(f"  commit: {sha[:8]} — {_COMMIT_MESSAGE}")
    pushed = False
    if committed and remote and repo.remotes:
        repo.remote("origin").push("main")
        pushed = True

    # --- Validação operacional (US3) ---
    ok, val_problems = validate_installation(target)
    if ok:
        typer.echo("  validação: artefatos habilitam o Opening Handshake ✓")
        typer.echo(
            "  próximo: abra uma sessão NOVA e limpa e pergunte 'qual o estado do projeto?' "
            "— a 1ª resposta deve começar confirmando a leitura de HANDOVER/ADR/constituição/git."
        )
    else:
        for problem in val_problems:
            typer.echo(f"  VALIDAÇÃO FALHOU: {problem}")
        typer.echo("  init NÃO concluído — corrija e re-rode.")
    typer.echo("journey-init: concluído." if ok else "journey-init: incompleto.")
    return {
        "created": len(result["created"]),
        "preserved": len(result["preserved"]),
        "merged": len(result["merged"]),
        "committed": committed,
        "commit": sha,
        "spec_kit": spec_kit_ok,
        "pushed": pushed,
        "validated": ok,
    }


def init(
    project_name: Annotated[str, typer.Option("--project-name", help="Project codename.")],
    target: Annotated[
        Path | None, typer.Option("--target", help="Target project directory.")
    ] = None,
    language: Annotated[
        str, typer.Option("--language", help="Doc language (pt-BR/en-US).")
    ] = "pt-BR",
    remote: Annotated[str, typer.Option("--remote", help="Git remote URL (optional).")] = "",
    username: Annotated[str, typer.Option("--git-username", help="git user.name.")] = "",
    email: Annotated[str, typer.Option("--git-email", help="git user.email.")] = "",
    templates: Annotated[
        Path | None, typer.Option("--templates", help="Templates dir (advanced).")
    ] = None,
    yes: Annotated[
        bool, typer.Option("--yes", help="Auto-confirm checkpoints (non-interactive).")
    ] = False,
    skip_spec_kit: Annotated[
        bool, typer.Option("--skip-spec-kit", help="Skip Spec Kit install.")
    ] = False,
) -> None:
    """Install the Journey methodology into a project (conducted, checkpoint-gated)."""
    run_init(
        project_name=project_name,
        target=target if target is not None else Path("."),
        language=language,
        remote=remote,
        username=username,
        email=email,
        templates_dir=templates,
        yes=yes,
        skip_spec_kit=skip_spec_kit,
    )
