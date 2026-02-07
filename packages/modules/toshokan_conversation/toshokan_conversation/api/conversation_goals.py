from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, status

from ..app import ConversationGoalService
from ..domain import ConversationGoalSettings
from ..ports import Clock, ConversationGoalRepository
from .schemas import ConversationGoals, ConversationGoalsUpdate

router = APIRouter(tags=["ConversationGoals"])


class InMemoryConversationGoalRepository(ConversationGoalRepository):
    def __init__(self) -> None:
        self._store: dict[str, ConversationGoalSettings] = {}

    def get_settings(self, user_id: str) -> ConversationGoalSettings | None:
        return self._store.get(user_id)

    def save_settings(self, user_id: str, settings: ConversationGoalSettings) -> None:
        self._store[user_id] = settings


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


_repository = InMemoryConversationGoalRepository()
_clock = SystemClock()
_service = ConversationGoalService(_repository, _clock)


@router.get("/modules/toshokan_conversation/goals")
def get_conversation_goals(request: Request) -> ConversationGoals:
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized.",
        )

    settings = _service.get_settings(user.user_id)
    return ConversationGoals(
        daily_unit_target=settings.daily_unit_target,
        updated_at=settings.updated_at,
    )


@router.put("/modules/toshokan_conversation/goals")
def update_conversation_goals(
    request: Request, payload: ConversationGoalsUpdate
) -> ConversationGoals:
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized.",
        )

    settings = _service.update_settings(user.user_id, payload.daily_unit_target)
    return ConversationGoals(
        daily_unit_target=settings.daily_unit_target,
        updated_at=settings.updated_at,
    )
