from __future__ import annotations

from datetime import datetime
from typing import Protocol

from ..domain import ConversationGoalSettings


class ConversationGoalRepository(Protocol):
    def get_settings(self, user_id: str) -> ConversationGoalSettings | None:
        raise NotImplementedError

    def save_settings(self, user_id: str, settings: ConversationGoalSettings) -> None:
        raise NotImplementedError


class Clock(Protocol):
    def now(self) -> datetime:
        raise NotImplementedError
