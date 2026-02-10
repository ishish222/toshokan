from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class GoalResult:
    """Progress snapshot for a single module-provided goal on a given day."""

    goal_type: str
    label: str
    achieved: bool
    current: int
    target: int


@dataclass(frozen=True)
class DailyGoalRecord:
    """Persisted evaluation of all goals for one user on one day."""

    id: UUID
    user_id: UUID
    date: date
    achieved: bool
    goals: list[GoalResult]
    created_at: datetime
