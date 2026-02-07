from __future__ import annotations

from ..domain import DEFAULT_DAILY_UNIT_TARGET, ConversationGoalSettings
from ..ports import Clock, ConversationGoalRepository


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
