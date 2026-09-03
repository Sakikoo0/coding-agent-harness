"""Contracts shared by tools and the tool runtime."""

from dataclasses import dataclass
from typing import Any, Protocol

from coding_agent.models.base import ToolDefinition, ToolResult
from coding_agent.workspace.base import Workspace


@dataclass(frozen=True, slots=True)
class ToolContext:
    """Per-run dependencies available to every tool invocation."""

    workspace: Workspace
    run_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.run_id, str) or not self.run_id.strip():
            raise ValueError("run_id cannot be blank")

class Tool(Protocol):
    """Executable tool with an explicit model-facing schema."""

    name: str
    description: str

    def definition(self) -> ToolDefinition:
        """Return the schema advertised to the model."""
        ...

    async def execute(
        self,
        arguments: dict[str, Any],
        context: ToolContext
    ) -> ToolResult:
        """Execute one validated invocation in the supplied run context."""
        ...