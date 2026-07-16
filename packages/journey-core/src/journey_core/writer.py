r"""Write routing by execution mode (ADR-0004 §7.6, FR-002).

Writes always target the runtime where the repository lives. Writing into a WSL
repository via a UNC path (``\\wsl.localhost\``) is vetoed because it corrupts
identity, file mode, and line endings (ADR-0004, Foundation history).
"""

from __future__ import annotations

import os
import platform
from pathlib import Path

from journey_core.exceptions import WriteRoutingError
from journey_core.models.project_state import Runtime

_UNC_PREFIXES = ("\\\\wsl.localhost\\", "\\\\wsl$\\", "//wsl.localhost/", "//wsl$/")


def detect_runtime() -> Runtime:
    """Detect the runtime where this process is executing.

    Returns:
        ``WSL_TUNNEL`` when running inside WSL, ``WINDOWS`` on native Windows,
        otherwise ``NATIVE``.
    """
    if os.name == "nt":
        return Runtime.WINDOWS
    if "microsoft" in platform.uname().release.lower():
        return Runtime.WSL_TUNNEL
    return Runtime.NATIVE


def is_unc_path(path: str | Path) -> bool:
    """Return whether ``path`` is a forbidden UNC path into a WSL repository."""
    lowered = str(path).lower()
    return any(lowered.startswith(prefix.lower()) for prefix in _UNC_PREFIXES)


def guard_write_target(path: str | Path) -> Path:
    """Validate a write target, vetoing UNC paths into WSL (ADR-0004).

    Args:
        path: The intended write destination.

    Returns:
        The path as a :class:`~pathlib.Path` when allowed.

    Raises:
        WriteRoutingError: If ``path`` is a UNC path into a WSL repository.
    """
    if is_unc_path(path):
        raise WriteRoutingError(
            f"Refusing to write via UNC path {path!r}; write through the repository "
            "runtime instead (ADR-0004 §7.6)."
        )
    return Path(path)
