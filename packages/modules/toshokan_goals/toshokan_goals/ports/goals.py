from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional
from uuid import UUID

from ..domain.entities import DailyGoalRecord, GoalResult


class GoalProvider(ABC):
    """Interface that each specific goal module (grammar, kanji, etc.) implements."""

    @abstractmethod
    def get_goals(self, user_id: UUID, target_date: date) -> list[GoalResult]:
        """Return the current progress for all goals this provider manages."""


class DailyGoalRepository(ABC):
    """Persistence port for daily goal evaluation records."""

    @abstractmethod
    def save_record(self, record: DailyGoalRecord) -> DailyGoalRecord: ...

    @abstractmethod
    def get_record(self, user_id: UUID, target_date: date) -> Optional[DailyGoalRecord]: ...

    @abstractmethod
    def list_records(self, user_id: UUID, from_date: date, to_date: date) -> list[DailyGoalRecord]: ...

    @abstractmethod
    def get_streak(self, user_id: UUID) -> int:
        """Return the length of the continuous chain of achieved days ending at the most recent completed day."""
