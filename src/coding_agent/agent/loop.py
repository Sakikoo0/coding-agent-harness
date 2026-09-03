"""Minimal linear coding-agent control loop."""

from dataclasses import dataclass
from uuid import uuid4

from coding_agent.agent.state import AgentState, RunStatus
from coding_agent.models.base import Message, Model, ModelResponse, ToolCall
from coding_agent.tools import ToolArgumentsError, ToolContext, ToolRegistry, UnknownToolError, default_tool_registry
from coding_agent.workspace.base import Workspace

_DEFAULT_SYSTEM_PROMPT = "You are a coding agent. Use the available tools when needed, then return a final answer."

class AgentProtocolError(ValueError):
    """Raised when a model response cannot be handled by the baseline loop."""

@dataclass(frozen=True, slots=True)
class FinalAnswer:
    """A model response that completes the run."""

    content: str


class Agent:
    """Run a model until it returns a final answer."""

    def __init__(
        self,
        model: Model,
        workspace: Workspace,
        *,
        tool_registry: ToolRegistry | None = None,
        system_prompt: str = _DEFAULT_SYSTEM_PROMPT
    ) -> None:
        self.model = model
        self.workspace = workspace
        self.tool_registry = tool_registry or default_tool_registry()
        self.system_prompt = system_prompt
        self.state = AgentState()
        self._tool_context: ToolContext | None = None

    async def run(self, task: str) -> AgentState:
        self.state = AgentState(
            messages=[
                Message(role="system", content=self.system_prompt),
                Message(role="user", content=task)
            ],
            status=RunStatus.RUNNING
        )

        self._tool_context = ToolContext(workspace=self.workspace, run_id=uuid4().hex)
        try:
            while self.state.status is RunStatus.RUNNING:
                await self.step()
        except Exception:
            self.state.status = RunStatus.FAILED
            raise
        return self.state

    async def step(self) -> None:
        response = await self.model.complete(self.state.messages, tools=self.tool_registry.definitions())
        self.state.add_usage(response.usage)
        self.state.messages.append(
            Message(role="assistant", content=response.content, tool_calls=response.tool_calls)
        )

        action = _parse_action(response)
        if isinstance(action, FinalAnswer):
            self.state.status = RunStatus.COMPLETED
            return

        if self._tool_context is None:
            raise RuntimeError("Agent step requires an active run")
        try:
            result = await self.tool_registry.execute(action, self._tool_context)
        except (UnknownToolError, ToolArgumentsError) as error:
            raise AgentProtocolError(str(error)) from error
        self.state.messages.append(
            Message(
                role="tool",
                content=result.model_dump_json(),
                tool_call_id=action.id,
            )
        )

def _parse_action(response: ModelResponse) -> ToolCall | FinalAnswer:
    if not response.tool_calls:
        if response.content is None:
            raise AgentProtocolError("Final response must include content")
        return FinalAnswer(content=response.content)

    if len(response.tool_calls) != 1:
        raise AgentProtocolError("Baseline agent requires exactly one tool call per response")

    return response.tool_calls[0]