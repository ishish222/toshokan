from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


DEFAULT_DAILY_TARGET = 1


@dataclass(frozen=True)
class GoalDefinition:
    daily_unit_target: int
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.daily_unit_target < 1:
            raise ValueError("daily_unit_target must be >= 1.")


@dataclass(frozen=True)
class DailyCompletionRecord:
    date: date
    completed: bool


@dataclass(frozen=True)
class DailyGoalStatus:
    date: date
    completed_units: int
    target: int
    achieved: bool


@dataclass(frozen=True)
class GoalStreak:
    current: int
    last_achieved_date: date | None


@dataclass(frozen=True)
class DashboardSnapshot:
    today: DailyGoalStatus
    calendar: list[DailyGoalStatus]
    streak: GoalStreak
