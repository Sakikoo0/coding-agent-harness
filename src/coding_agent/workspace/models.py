"""Typed results returned by workspace operations."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Captured output from one command execution."""

    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool = False

    @property
    def output(self) -> str:
        """Return combined output for compatibility with the baseline agent."""
        return self.stdout + self.stderr

    @property
    def return_code(self) -> int:
        """Return the exit code."""
        return self.exit_code

@dataclass(frozen=True, slots=True)
class FileResult:
    """Content read from or written to a workspace path."""

    path: str
    content: str