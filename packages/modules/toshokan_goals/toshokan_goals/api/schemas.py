from __future__ import annotations

from datetime import date
from typing import List

from pydantic import BaseModel, Field


class GoalProgress(BaseModel):
    goal_type: str
    label: str
    achieved: bool
    current: int = Field(ge=0)
    target: int = Field(ge=1)


class DailyGoalToday(BaseModel):
    date: date
    achieved: bool
    goals: List[GoalProgress]
    streak: int = Field(ge=0)


class DailyGoalDay(BaseModel):
    date: date
    achieved: bool


class DailyGoalCalendar(BaseModel):
    items: List[DailyGoalDay]


class StreakInfo(BaseModel):
    current_streak: int = Field(ge=0)
