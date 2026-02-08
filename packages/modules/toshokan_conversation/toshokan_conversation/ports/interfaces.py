from __future__ import annotations

from datetime import datetime
from typing import Protocol

from ..domain import Conversation, ConversationGoalSettings, ConversationSetup


class ConversationGoalRepository(Protocol):
    def get_settings(self, user_id: str) -> ConversationGoalSettings | None:
        raise NotImplementedError

    def save_settings(self, user_id: str, settings: ConversationGoalSettings) -> None:
        raise NotImplementedError


class Clock(Protocol):
    def now(self) -> datetime:
        raise NotImplementedError


class ConversationRepository(Protocol):
    def create(
        self, user_id: str, title: str | None, setup: ConversationSetup
    ) -> Conversation:
        raise NotImplementedError

    def list(
        self,
        user_id: str,
        limit: int = 20,
        cursor: str | None = None,
        archived: bool | None = None,
        starred: bool | None = None,
        sort: str | None = None,
        query: str | None = None,
    ) -> tuple[list[Conversation], str | None]:
        raise NotImplementedError

    def archive(self, user_id: str, conversation_id: str) -> Conversation | None:
        raise NotImplementedError
