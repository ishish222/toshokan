from __future__ import annotations

from datetime import date, datetime
from typing import Protocol

from ..domain import DailyCompletionRecord, GoalDefinition


class GoalRepository(Protocol):
    def get_goal(self, user_id: str) -> GoalDefinition | None:
        raise NotImplementedError

    def save_goal(self, user_id: str, goal: GoalDefinition) -> None:
        raise NotImplementedError


class DailyCompletionRepository(Protocol):
    def get_completion(self, user_id: str, day: date) -> bool | None:
        raise NotImplementedError

    def set_completion(self, user_id: str, record: DailyCompletionRecord) -> None:
        raise NotImplementedError

    def list_range(
        self, user_id: str, start_date: date, end_date: date
    ) -> list[DailyCompletionRecord]:
        raise NotImplementedError


class Clock(Protocol):
    def today(self) -> date:
        raise NotImplementedError

    def now(self) -> datetime:
        raise NotImplementedError
