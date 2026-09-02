"""Provider-independent workspace contract."""

from collections.abc import Mapping
from pathlib import Path
from typing import Protocol

from coding_agent.workspace.models import CommandResult, FileResult


class Workspace(Protocol):
    """Execution and file-operation boundary used by the agent runtime."""

    async def execute(
        self, 
        command: str,
        *,
        cwd: str | Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout: float | None = 30.0
    ) -> CommandResult:
        """Execute a command with optional cwd, environment overrides, and timeout."""
        ...

    async def read_file(self, path: str | Path) -> FileResult:
        """Read a UTF-8 text file from the workspace."""
        ...

    async def write_file(self, path: str | Path, content: str) -> FileResult:
        """Write a UTF-8 text file in the workspace."""
        ...

    async def close(self) -> None:
        """Release resources owned by the workspace."""
        ...