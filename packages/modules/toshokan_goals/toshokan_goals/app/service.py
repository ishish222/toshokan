from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Callable, Optional
from uuid import UUID, uuid4

from ..domain.entities import DailyGoalRecord, GoalResult
from ..ports.goals import DailyGoalRepository, GoalProvider

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    from backports.zoneinfo import ZoneInfo  # type: ignore[no-redef]

DEFAULT_TIMEZONE = "UTC"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _user_today(tz_name: Optional[str]) -> date:
    """Determine "today" in the user's timezone."""
    tz = ZoneInfo(tz_name) if tz_name else ZoneInfo(DEFAULT_TIMEZONE)
    return datetime.now(tz).date()


@dataclass
class DailyGoalsService:
    providers: list[GoalProvider]
    repository: DailyGoalRepository
    get_user_timezone: Callable[[UUID], Optional[str]]

    # -- queries --

    def get_today(self, user_id: UUID) -> dict:
        """Return today's goal status with per-goal breakdown and current streak."""
        tz_name = self.get_user_timezone(user_id)
        today = _user_today(tz_name)

        goals: list[GoalResult] = []
        for provider in self.providers:
            goals.extend(provider.get_goals(user_id, today))

        achieved = all(g.achieved for g in goals) if goals else True
        streak = self.repository.get_streak(user_id)

        return {
            "date": today,
            "achieved": achieved,
            "goals": goals,
            "streak": streak,
        }

    def get_calendar(self, user_id: UUID, from_date: date, to_date: date) -> list[DailyGoalRecord]:
        return self.repository.list_records(user_id, from_date, to_date)

    def get_streak(self, user_id: UUID) -> int:
        return self.repository.get_streak(user_id)

    # -- commands --

    def evaluate_day(self, user_id: UUID, target_date: date) -> DailyGoalRecord:
        """Evaluate all goal providers for a given day, persist, and return the record."""
        goals: list[GoalResult] = []
        for provider in self.providers:
            goals.extend(provider.get_goals(user_id, target_date))

        achieved = all(g.achieved for g in goals) if goals else True

        record = DailyGoalRecord(
            id=uuid4(),
            user_id=user_id,
            date=target_date,
            achieved=achieved,
            goals=goals,
            created_at=_now(),
        )
        return self.repository.save_record(record)
