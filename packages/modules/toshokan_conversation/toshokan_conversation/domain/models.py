from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


DEFAULT_DAILY_UNIT_TARGET = 1


@dataclass(frozen=True)
class ConversationGoalSettings:
    daily_unit_target: int
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.daily_unit_target < 1:
            raise ValueError("daily_unit_target must be >= 1.")


@dataclass(frozen=True)
class GrammarTarget:
    id: str
    label: str
    description: str | None = None


@dataclass(frozen=True)
class ConversationSetup:
    formality: Literal["formal", "informal"]
    situation: str
    initiator: Literal["system", "user"]
    grammar_focus: list[GrammarTarget] = field(default_factory=list)


@dataclass(frozen=True)
class Conversation:
    conversation_id: str
    title: str | None
    started_at: datetime
    status: Literal["active", "archived"] = "active"
    setup: ConversationSetup | None = None
