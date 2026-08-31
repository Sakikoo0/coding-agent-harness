"""Workspace contracts and implementations."""

from coding_agent.workspace.base import Workspace
from coding_agent.workspace.local import LocalWorkspace
from coding_agent.workspace.models import CommandResult, FileResult

__all__ = ["CommandResult", "FileResult", "LocalWorkspace", "Workspace"]