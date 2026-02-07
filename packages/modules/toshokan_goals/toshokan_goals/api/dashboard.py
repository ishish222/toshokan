from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException, Query, Request, status

from ..adapters import (
    InMemoryDailyCompletionRepository,
    InMemoryGoalRepository,
    SystemClock,
)
from ..app import GoalService
from .schemas import DashboardResponse

router = APIRouter(tags=["Dashboard"])

_goal_repository = InMemoryGoalRepository()
_completion_repository = InMemoryDailyCompletionRepository()
_clock = SystemClock()
_goal_service = GoalService(_goal_repository, _completion_repository, _clock)


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    request: Request,
    start_date: date = Query(...),
    end_date: date = Query(...),
) -> DashboardResponse:
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date must be before or equal to end_date.",
        )

    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized.",
        )

    snapshot = _goal_service.get_dashboard(user.user_id, start_date, end_date)
    return DashboardResponse.from_snapshot(snapshot)
