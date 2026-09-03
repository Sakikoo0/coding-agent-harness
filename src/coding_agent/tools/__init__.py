"""Typed tools and registry dispatch."""

from coding_agent.tools.base import Tool, ToolContext
from coding_agent.tools.registry import (
    DuplicateToolError,
    ReadFileTool,
    ShellTool,
    ToolArgumentsError,
    ToolRegistry,
    ToolRegistryError,
    UnknownToolError,
    WriteFileTool,
    default_tool_registry,
)

__all__ = [
    "DuplicateToolError",
    "ReadFileTool",
    "ShellTool",
    "Tool",
    "ToolArgumentsError",
    "ToolContext",
    "ToolRegistry",
    "ToolRegistryError",
    "UnknownToolError",
    "WriteFileTool",
    "default_tool_registry",
]