"""Typed results returned by workspace operations."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Captured output from one command execution."""

    output: str
    return_code: int

@dataclass(frozen=True, slots=True)
class FileResult:
    """Content read from or written to a workspace path."""

    path: str
    content: str