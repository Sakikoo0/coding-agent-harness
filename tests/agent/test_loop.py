import json
from pathlib import Path

import pytest

from coding_agent.agent import Agent, AgentProtocolError, RunStatus
from coding_agent.models import FakeModel, ModelResponse, ToolCall, Usage
from coding_agent.workspace import CommandResult, FileResult, LocalWorkspace


class FakeWorkspace:
    def __init__(self) -> None:
        self.commands: list[str] = []

    async def execute(self, command: str) -> CommandResult:
        self.commands.append(command)
        return CommandResult(output="fake output\n", return_code=0)

    async def read_file(self, path: str | Path) -> FileResult:
        raise NotImplementedError

    async def write_file(self, path: str | Path, content: str) -> FileResult:
        raise NotImplementedError

    async def close(self) -> None:
        pass


async def test_agent_runs_shell_then_completes(tmp_path) -> None:
    command = "printf 'hello\\n'; printf 'run\\n' >> execution-count.txt"
    model = FakeModel(
        [
            ModelResponse(
                content="I will run the command.",
                tool_calls=[ToolCall(id="call-1", name="shell", arguments={"command": command})],
                usage=Usage(input_tokens=10, output_tokens=4, cost=0.01),
            ),
            ModelResponse(
                content="done",
                usage=Usage(input_tokens=12, output_tokens=2, cost=0.02),
            ),
        ]
    )
    agent = Agent(model=model, workspace=LocalWorkspace(tmp_path))

    state = await agent.run("Print hello once")

    assert state.status is RunStatus.COMPLETED
    assert [message.role for message in state.messages] == ["system", "user", "assistant", "tool", "assistant"]
    assert json.loads(state.messages[3].content or "") == {"output": "hello\n", "return_code": 0}
    assert state.messages[-1].content == "done"
    assert state.usage == Usage(input_tokens=22, output_tokens=6, cost=0.03)
    assert (tmp_path / "execution-count.txt").read_text().splitlines() == ["run"]


async def test_agent_rejects_unknown_tool_without_execution() -> None:
    workspace = FakeWorkspace()
    agent = Agent(
        model=FakeModel(
            [
                ModelResponse(
                    tool_calls=[ToolCall(id="call-1", name="delete_everything", arguments={})],
                )
            ]
        ),
        workspace=workspace,
    )

    with pytest.raises(AgentProtocolError, match="Unsupported tool"):
        await agent.run("Use an unsupported tool")

    assert agent.state.status is RunStatus.FAILED
    assert workspace.commands == []

async def test_agent_rejects_shell_call_without_command() -> None:
    workspace = FakeWorkspace()
    agent = Agent(
        model=FakeModel([ModelResponse(tool_calls=[ToolCall(id="call-1", name="shell", arguments={})])]),
        workspace=workspace,
    )

    with pytest.raises(AgentProtocolError, match="non-empty string command"):
        await agent.run("Run an invalid shell call")

    assert agent.state.status is RunStatus.FAILED
    assert workspace.commands == []
