from pathlib import Path

import pytest
from journey_core.exceptions import JourneyError
from journey_core.parsers import GitState, read_git_state


def test_read_git_state_on_this_repo() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    state = read_git_state(repo_root)
    assert isinstance(state, GitState)
    assert len(state.head_sha) == 40
    assert len(state.commits) > 0
    assert all(commit.summary for commit in state.commits)


def test_read_git_state_rejects_non_repo(tmp_path: Path) -> None:
    with pytest.raises(JourneyError):
        read_git_state(tmp_path)
