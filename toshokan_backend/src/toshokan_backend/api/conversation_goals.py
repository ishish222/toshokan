from __future__ import annotations

from fastapi import APIRouter

from ..schemas import ConversationGoalsUpdate

router = APIRouter(tags=["ConversationGoals"])


@router.get("/modules/toshokan_conversation/goals")
def get_conversation_goals() -> dict:
    return {"detail": "Not implemented"}


@router.put("/modules/toshokan_conversation/goals")
def update_conversation_goals(payload: ConversationGoalsUpdate) -> dict:
    _ = payload
    return {"detail": "Not implemented"}
