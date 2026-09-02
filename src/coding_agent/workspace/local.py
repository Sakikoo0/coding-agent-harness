"""Workspace implementation backed by the local host."""

import asyncio
import os
import signal
import subprocess
from collections.abc import Mapping
from pathlib import Path

from coding_agent.workspace.models import CommandResult, FileResult


class LocalWorkspace:
    """Run commands and file operations directly on a trusted local host."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()

        if not self.root.is_dir():
            raise ValueError(f"Workspace root is not a directory: {self.root}")

    async def execute(
        self, 
        command: str,
        *,
        cwd: str | Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout: float | None = 30.0
    ) -> CommandResult:
        """Execute a command, defaulting to the root and inherited environment.

        Relative working directories are resolved from ``root``. Environment
        values supplied by the caller override inherited host values.
        """
        return await asyncio.to_thread(
            self._execute, 
            command,
            cwd=cwd,
            env=env,
            timeout=timeout
        )

    def _execute(
        self, 
        command: str,
        *,
        cwd: str | Path | None,
        env: Mapping[str, str] | None,
        timeout: float | None
    ) -> CommandResult:
        working_dir = self.root if cwd is None else self.root / Path(cwd)
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=working_dir,
            env=os.environ | dict(env or {}),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=os.name == "posix",
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            self._kill_process_group(process)
            stdout, stderr = process.communicate()
            return CommandResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=-1,
                timed_out=True,
            )
        return CommandResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=process.returncode,
        )

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

    @staticmethod
    def _kill_process_group(process: subprocess.Popen[str]) -> None:
        try:
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
        except ProcessLookupError:
            pass