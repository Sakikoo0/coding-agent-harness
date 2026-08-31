"""Provider-independent workspace contract."""

from pathlib import Path
from typing import Protocol

from coding_agent.workspace.models import CommandResult, FileResult


class Workspace(Protocol):
    """Execution and file-operation boundary used by the agent runtime."""

    async def execute(self, command: str) -> CommandResult:
        """Execute a command in the workspace's working directory."""
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