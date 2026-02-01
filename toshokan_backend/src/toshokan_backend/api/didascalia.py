from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["Didascalia"])


@router.get("/conversations/{conversation_id}/turns/{turn_id}/didascalia")
def get_didascalia_for_turn(conversation_id: str, turn_id: str) -> dict:
    _ = conversation_id
    _ = turn_id
    return {"detail": "Not implemented"}


@router.get("/conversations/{conversation_id}/didascalia/latest")
def get_latest_didascalia(conversation_id: str) -> dict:
    _ = conversation_id
    return {"detail": "Not implemented"}
