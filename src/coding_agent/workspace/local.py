"""Trusted local shell execution."""

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ShellResult:
    """Captured output from one shell process."""

    output: str
    return_code: int

class LocalWorkspace:
    """Run each command in a new host shell process rooted at one directory."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()

        if not self.root.is_dir():
            raise ValueError(f"Workspace root is not a directory: {self.root}")

    def execute(self, command: str) -> ShellResult:
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
        return ShellResult(output=completed.stdout, return_code=completed.returncode)