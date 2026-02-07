from __future__ import annotations

from fastapi import APIRouter

from ..schemas import (
    ConversationPreferencesPatch,
    ConversationSetupPatch,
    CreateTurnRequest,
    SuggestSituationRequest,
)

router = APIRouter(tags=["Conversations"])


@router.post("/situations:suggest")
def suggest_situation(payload: SuggestSituationRequest) -> dict:
    _ = payload
    return {"detail": "Not implemented"}


@router.get("/conversations")
def list_conversations() -> dict:
    return {"detail": "Not implemented"}


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str) -> dict:
    _ = conversation_id
    return {"detail": "Not implemented"}


@router.patch("/conversations/{conversation_id}")
def update_conversation(conversation_id: str, payload: dict) -> dict:
    _ = conversation_id
    _ = payload
    return {"detail": "Not implemented"}


@router.delete("/conversations/{conversation_id}")
def archive_conversation(conversation_id: str) -> dict:
    _ = conversation_id
    return {"detail": "Not implemented"}


@router.get("/conversations/{conversation_id}/setup")
def get_conversation_setup(conversation_id: str) -> dict:
    _ = conversation_id
    return {"detail": "Not implemented"}


@router.patch("/conversations/{conversation_id}/setup")
def update_conversation_setup(
    conversation_id: str, payload: ConversationSetupPatch
) -> dict:
    _ = conversation_id
    _ = payload
    return {"detail": "Not implemented"}


@router.post("/conversations/{conversation_id}/turns")
def create_turn(conversation_id: str, payload: CreateTurnRequest) -> dict:
    _ = conversation_id
    _ = payload
    return {"detail": "Not implemented"}


@router.patch("/conversations/{conversation_id}/preferences")
def update_conversation_preferences(
    conversation_id: str, payload: ConversationPreferencesPatch
) -> dict:
    _ = conversation_id
    _ = payload
    return {"detail": "Not implemented"}
