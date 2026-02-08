from __future__ import annotations

from ..domain import (
    DEFAULT_DAILY_UNIT_TARGET,
    Conversation,
    ConversationGoalSettings,
    ConversationSetup,
)
from ..ports import Clock, ConversationGoalRepository, ConversationRepository


class ConversationGoalService:
    def __init__(
        self, repository: ConversationGoalRepository, clock: Clock
    ) -> None:
        self._repository = repository
        self._clock = clock

    def get_settings(self, user_id: str) -> ConversationGoalSettings:
        existing = self._repository.get_settings(user_id)
        if existing is not None:
            return existing
        return ConversationGoalSettings(
            daily_unit_target=DEFAULT_DAILY_UNIT_TARGET,
            updated_at=self._clock.now(),
        )

    def update_settings(
        self, user_id: str, daily_unit_target: int
    ) -> ConversationGoalSettings:
        settings = ConversationGoalSettings(
            daily_unit_target=daily_unit_target,
            updated_at=self._clock.now(),
        )
        self._repository.save_settings(user_id, settings)
        return settings


class ConversationService:
    def __init__(self, repository: ConversationRepository, clock: Clock) -> None:
        self._repository = repository
        self._clock = clock

    def create(
        self, user_id: str, title: str | None, setup: ConversationSetup
    ) -> Conversation:
        _ = self._clock
        return self._repository.create(user_id, title, setup)

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
        return self._repository.list(
            user_id=user_id,
            limit=limit,
            cursor=cursor,
            archived=archived,
            starred=starred,
            sort=sort,
            query=query,
        )

    def archive(self, user_id: str, conversation_id: str) -> Conversation | None:
        return self._repository.archive(user_id, conversation_id)
