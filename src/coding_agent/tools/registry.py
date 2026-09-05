"""Typed tool implementations and deterministic registry dispatch."""

import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from coding_agent.models.base import ToolCall, ToolDefinition, ToolResult
from coding_agent.tools.base import (
    DuplicateToolError,
    Tool,
    ToolArgumentsError,
    ToolContext,
    ToolRegistryError,
    UnknownToolError,
)
from coding_agent.tools.filesystem import filesystem_tools


class ToolRegistry:
    """Hold tools by name and dispatch typed model calls to them."""

    def __init__(self, tools: Iterable[Tool] = ()) -> None:
        self._tools: dict[str, Tool] = {}

        for tool in tools:
            self.register(tool)

    def register(self, tool: Tool) -> None:
        """Register one tool, rejecting ambiguous or inconsistent names."""
        definition = tool.definition()
        if definition.name != tool.name:
            raise ToolRegistryError(
                f"Tool name {tool.name!r} does not match definition name {definition.name!r}"
            )
        if tool.name in self._tools:
            raise DuplicateToolError(f"Tool {tool.name!r} is already registered")
        self._tools[tool.name] = tool

    def definitions(self) -> list[ToolDefinition]:
        """Return model-facing schemas in deterministic registration order."""
        return [tool.definition() for tool in self._tools.values()]

    def get(self, name: str) -> Tool:
        """Return a registered tool or fail without executing anything."""
        try:
            return self._tools[name]
        except KeyError as error:
            raise UnknownToolError(f"Unsupported tool: {name}") from error

    async def execute(self, call: ToolCall, context: ToolContext) -> ToolResult:
        """Dispatch one typed call to the matching tool."""
        tool = self.get(call.name)
        return await tool.execute(dict(call.arguments), context)

@dataclass(frozen=True, slots=True)
class ShellTool:
    """Run one command through the configured workspace."""

    name: str = "shell"
    description: str = "Run a shell command in the workspace."

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters={
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
                "additionalProperties": False
            }
        )

    async def execute(self, arguments: dict[str, Any], context: ToolContext) -> ToolResult:
        _require_exact_arguments(self.name, arguments, required={"command"})
        command = _require_non_empty_string(self.name, "command", arguments["command"])
        result = await context.workspace.execute(command)
        return ToolResult(
            content=json.dumps(
                {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.exit_code,
                    "timed_out": result.timed_out,
                },
                ensure_ascii=False,
            ),
            is_error=result.exit_code != 0 or result.timed_out,
        )

def default_tool_registry() -> ToolRegistry:
    """Build the current default tool set in stable model-facing order."""
    return ToolRegistry([ShellTool(), *filesystem_tools()])

def _require_exact_arguments(tool_name: str, arguments: dict[str, Any], *, required: set[str]) -> None:
    supplied = set(arguments)
    missing = required - supplied
    unexpected = supplied - required
    if missing:
        names = ", ".join(sorted(missing))
        raise ToolArgumentsError(f"Tool {tool_name!r} is missing required argument(s): {names}")
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise ToolArgumentsError(f"Tool {tool_name!r} received unexpected argument(s): {names}")


def _require_non_empty_string(tool_name: str, argument_name: str, value: Any) -> str:
    value = _require_string(tool_name, argument_name, value)
    if not value.strip():
        raise ToolArgumentsError(f"Tool {tool_name!r} argument {argument_name!r} cannot be blank")
    return value


def _require_string(tool_name: str, argument_name: str, value: Any) -> str:
    if not isinstance(value, str):
        raise ToolArgumentsError(f"Tool {tool_name!r} argument {argument_name!r} must be a string")
    return value
    

