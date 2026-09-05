"""Workspace contracts and implementations."""

from coding_agent.workspace.base import Workspace
from coding_agent.workspace.docker import DockerWorkspace
from coding_agent.workspace.local import LocalWorkspace
from coding_agent.workspace.models import CommandResult, FileInfo, FileResult

__all__ = ["CommandResult", "DockerWorkspace", "FileInfo", "FileResult", "LocalWorkspace", "Workspace"]