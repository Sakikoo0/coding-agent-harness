"""Typed tools and registry dispatch."""

from coding_agent.tools.base import Tool, ToolContext
from coding_agent.tools.filesystem import (
    EditFileTool,
    FileSystemConfig,
    FindFilesTool,
    ListDirectoryTool,
    ReadFileTool,
    SearchFilesTool,
    WriteFileTool,
    filesystem_tools,
)
from coding_agent.tools.registry import (
    DuplicateToolError,
    ShellTool,
    ToolArgumentsError,
    ToolRegistry,
    ToolRegistryError,
    UnknownToolError,
    default_tool_registry,
)

__all__ = [
    "DuplicateToolError",
    "EditFileTool",
    "FileSystemConfig",
    "FindFilesTool",
    "ListDirectoryTool",
    "ReadFileTool",
    "SearchFilesTool",
    "ShellTool",
    "Tool",
    "ToolArgumentsError",
    "ToolContext",
    "ToolRegistry",
    "ToolRegistryError",
    "UnknownToolError",
    "WriteFileTool",
    "default_tool_registry",
    "filesystem_tools",
]