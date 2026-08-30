"""Minimal linear coding-agent control loop."""

import json
from dataclasses import dataclass
from typing import Protocol

from coding_agent.agent.state import AgentState, RunStatus
from coding_agent.models.base import Message, Model, ModelResponse, ToolDefinition
from coding_agent.workspace.local import ShellResult

_DEFAULT_SYSTEM_PROMPT = "You are a coding agent. Use the shell tool when needed, then return a final answer."
_SHELL_TOOL = ToolDefinition(
    name="shell",
    description="Run a shell command in the working directory.",
    parameters={
        "type": "object",
        "properties": {"command": {"type": "string"}},
        "required": ["command"]
    }
)

class AgentProtocolError(ValueError):
    """Raised when a model response cannot be handled by the baseline loop."""

@dataclass(frozen=True, slots=True)
class ShellAction:
    """The only executable action supported by the baseline loop."""

    command: str
    tool_call_id: str

@dataclass(frozen=True, slots=True)
class FinalAnswer:
    """A model response that completes the run."""

    content: str

class ShellExecutor(Protocol):
    """Minimal execution boundary needed by the baseline loop."""

    def execute(self, command: str) -> ShellResult: ...

class Agent:
    """Run a model until it returns a final answer."""

    def __init__(
        self,
        model: Model,
        workspace: ShellExecutor,
        *,
        system_prompt: str = _DEFAULT_SYSTEM_PROMPT
    ) -> None:
        self.model = model
        self.workspace = workspace
        self.system_prompt = system_prompt
        self.state = AgentState()

    async def run(self, task: str) -> AgentState:
        self.state = AgentState(
            messages=[
                Message(role="system", content=self.system_prompt),
                Message(role="user", content=task)
            ],
            status=RunStatus.RUNNING
        )

        try:
            while self.state.status is RunStatus.RUNNING:
                await self.step()
        except Exception:
            self.state.status = RunStatus.FAILED
            raise
        return self.state

    async def step(self) -> None:
        response = await self.model.complete(self.state.messages, tools=[_SHELL_TOOL])
        self.state.add_usage(response.usage)
        self.state.messages.append(
            Message(role="assistant", content=response.content, tool_calls=response.tool_calls)
        )

        action = _parse_action(response)
        if isinstance(action, FinalAnswer):
            self.state.status = RunStatus.COMPLETED
            return

        result = self.workspace.execute(action.command)
        self.state.messages.append(
            Message(
                role="tool",
                content=json.dumps(
                    {
                        "output": result.output,
                        "return_code": result.return_code
                    },
                    ensure_ascii=False
                ),
                tool_call_id=action.tool_call_id
            )
        )

def _parse_action(response: ModelResponse) -> ShellAction | FinalAnswer:
    if not response.tool_calls:
        if response.content is None:
            raise AgentProtocolError("Final response must include content")
        return FinalAnswer(content=response.content)

    if len(response.tool_calls) != 1:
        raise AgentProtocolError("Baseline agent requires exactly one tool call per response")

    tool_call = response.tool_calls[0]
    if tool_call.name != _SHELL_TOOL.name:
        raise AgentProtocolError(f"Unsupported tool: {tool_call.name}")

    command = tool_call.arguments.get("command")
    if not isinstance(command, str) or not command.strip():
        raise AgentProtocolError("Shell tool requires a non-empty string command")
    return ShellAction(command=command, tool_call_id=tool_call.id)