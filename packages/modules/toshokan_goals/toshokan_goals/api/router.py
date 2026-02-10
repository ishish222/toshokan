from __future__ import annotations

from datetime import date
from typing import Callable, Protocol
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from ..app import DailyGoalsService
from ..domain.entities import GoalResult as DomainGoalResult
from .schemas import (
    DailyGoalCalendar,
    DailyGoalDay,
    DailyGoalToday,
    GoalProgress,
    StreakInfo,
)


class AuthContext(Protocol):
    user_id: UUID
    customer_ids: list[UUID]
    groups: list[str]

    @property
    def is_backoffice(self) -> bool:
        raise NotImplementedError


def create_router(service: DailyGoalsService, get_auth_context: Callable[..., AuthContext]) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/daily-goals/today",
        tags=["DailyGoals"],
        summary="Get today's daily goal status for the current user",
        response_model=DailyGoalToday,
    )
    def get_today(auth: AuthContext = Depends(get_auth_context)) -> DailyGoalToday:
        result = service.get_today(user_id=auth.user_id)
        return DailyGoalToday(
            date=result["date"],
            achieved=result["achieved"],
            goals=[_to_goal_progress(g) for g in result["goals"]],
            streak=result["streak"],
        )

    @router.get(
        "/daily-goals/calendar",
        tags=["DailyGoals"],
        summary="Get daily goal calendar for the current user",
        response_model=DailyGoalCalendar,
    )
    def get_calendar(
        from_date: date = Query(..., alias="from"),
        to_date: date = Query(..., alias="to"),
        auth: AuthContext = Depends(get_auth_context),
    ) -> DailyGoalCalendar:
        records = service.get_calendar(user_id=auth.user_id, from_date=from_date, to_date=to_date)
        return DailyGoalCalendar(
            items=[DailyGoalDay(date=r.date, achieved=r.achieved) for r in records],
        )

    @router.get(
        "/daily-goals/streak",
        tags=["DailyGoals"],
        summary="Get current streak for the current user",
        response_model=StreakInfo,
    )
    def get_streak(auth: AuthContext = Depends(get_auth_context)) -> StreakInfo:
        streak = service.get_streak(user_id=auth.user_id)
        return StreakInfo(current_streak=streak)

    return router


def _to_goal_progress(goal: DomainGoalResult) -> GoalProgress:
    return GoalProgress(
        goal_type=goal.goal_type,
        label=goal.label,
        achieved=goal.achieved,
        current=goal.current,
        target=goal.target,
    )
