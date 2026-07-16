# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
"""Read local git state (commits, branches, tags) via gitpython — Phase A, no network (FR-013).

GitPython exposes several dynamically-typed members; pyright's unknown-type checks
are relaxed at this thin boundary only (file-level comment above), and every value
is immediately wrapped in a typed pydantic model.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from git import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError
from pydantic import BaseModel

from journey_core.exceptions import JourneyError


class CommitInfo(BaseModel):
    """A single commit, reduced to the fields the roadmap needs."""

    sha: str
    authored_at: datetime
    summary: str


class GitState(BaseModel):
    """Local git state read without any network access (Phase A, FR-013)."""

    head_sha: str
    branch: str | None = None
    commits: list[CommitInfo] = []


def read_git_state(repo_path: str | Path, max_commits: int = 500) -> GitState:
    """Read commits and the current branch from a local git repository.

    Args:
        repo_path: Path to the repository root.
        max_commits: Upper bound on commits read (most recent first).

    Returns:
        The local :class:`GitState`.

    Raises:
        JourneyError: If ``repo_path`` is not a git repository.
    """
    try:
        repo = Repo(repo_path)
    except (InvalidGitRepositoryError, NoSuchPathError) as exc:
        raise JourneyError(f"Not a git repository: {repo_path!r}") from exc

    commits: list[CommitInfo] = []
    for commit in repo.iter_commits(max_count=max_commits):
        commits.append(
            CommitInfo(
                sha=str(commit.hexsha),
                authored_at=commit.authored_datetime,
                summary=str(commit.summary),
            )
        )

    branch = None if repo.head.is_detached else str(repo.active_branch.name)
    return GitState(head_sha=str(repo.head.commit.hexsha), branch=branch, commits=commits)


def commits_since_last_tag(repo_path: str | Path, max_commits: int = 1000) -> list[CommitInfo]:
    """Commits since the most recent tag — or ALL commits when the repo has no tag (feature 009).

    No tag is the **normal first-release case**, not an error: it degrades to the full history
    gracefully (no alarming warning). Most-recent commits first. Reuses :class:`CommitInfo`.

    Raises:
        JourneyError: If ``repo_path`` is not a git repository.
    """
    try:
        repo = Repo(repo_path)
    except (InvalidGitRepositoryError, NoSuchPathError) as exc:
        raise JourneyError(f"Not a git repository: {repo_path!r}") from exc

    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    if tags:
        iterator = repo.iter_commits(f"{tags[-1].name}..HEAD", max_count=max_commits)
    else:
        iterator = repo.iter_commits(max_count=max_commits)

    commits: list[CommitInfo] = []
    for commit in iterator:
        commits.append(
            CommitInfo(
                sha=str(commit.hexsha),
                authored_at=commit.authored_datetime,
                summary=str(commit.summary),
            )
        )
    return commits


def commits_since_date(
    repo_path: str | Path, since: date, max_commits: int = 2000
) -> list[CommitInfo]:
    """Commits authored on or after ``since`` (feature 003 — retrospective audit, FR-001).

    Most-recent first. Filters by authored date (not commit date); ``max_commits`` bounds the scan.
    Reuses :class:`CommitInfo`.

    Raises:
        JourneyError: If ``repo_path`` is not a git repository.
    """
    try:
        repo = Repo(repo_path)
    except (InvalidGitRepositoryError, NoSuchPathError) as exc:
        raise JourneyError(f"Not a git repository: {repo_path!r}") from exc

    commits: list[CommitInfo] = []
    for commit in repo.iter_commits(max_count=max_commits):
        if commit.authored_datetime.date() < since:
            continue
        commits.append(
            CommitInfo(
                sha=str(commit.hexsha),
                authored_at=commit.authored_datetime,
                summary=str(commit.summary),
            )
        )
    return commits
