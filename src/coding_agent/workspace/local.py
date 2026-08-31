"""Workspace implementation backed by the local host."""

import asyncio
import subprocess
from pathlib import Path

from coding_agent.workspace.models import CommandResult, FileResult


class LocalWorkspace:
    """Run commands and file operations directly on a trusted local host."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()

        if not self.root.is_dir():
            raise ValueError(f"Workspace root is not a directory: {self.root}")

    async def execute(self, command: str) -> CommandResult:
        return await asyncio.to_thread(self._execute, command)

    def _execute(self, command: str) -> CommandResult:
        completed = subprocess.run(
            command,
            shell=True,
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False
        )
        return CommandResult(output=completed.stdout, return_code=completed.returncode)

    async def read_file(self, path: str | Path) -> FileResult:
        workspace_path = self._workspace_path(path)
        content = await asyncio.to_thread(workspace_path.read_text, encoding="utf-8")
        return FileResult(path=str(path), content=content)

    async def write_file(self, path: str | Path, content: str) -> FileResult:
        workspace_path = self._workspace_path(path)
        await asyncio.to_thread(self._write_text, workspace_path, content)
        return FileResult(path=str(path), content=content)

    def _workspace_path(self, path: str | Path) -> Path:
        return self.root / Path(path)

    async def close(self) -> None:
        """Release workspace resources; local one-shot operations own none."""

    @staticmethod
    def _write_text(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
