"""Typed state for an agent run."""

from enum import StrEnum

from pydantic import BaseModel, Field

from coding_agent.models import Message, Usage


class RunStatus(StrEnum):
    """Lifecycle states required by the baseline agent."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentState(BaseModel):
    """Conversation history, lifecycle status, and accumulated model usage."""

    messages: list[Message] = Field(default_factory=list)
    status: RunStatus = RunStatus.IDLE
    usage: Usage = Field(default_factory=Usage)

    def add_usage(self, usage: Usage) -> None:
        self.usage = self.usage + usage