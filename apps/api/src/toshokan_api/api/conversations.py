from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from ..schemas import (
    ConversationPreferencesPatch,
    ConversationCreateRequest,
    ConversationSetupPatch,
    CreateTurnRequest,
    SuggestSituationRequest,
)
from toshokan_conversation.adapters import InMemoryConversationRepository, SystemClock
from toshokan_conversation.app import ConversationService
from toshokan_conversation.domain import ConversationSetup, GrammarTarget

router = APIRouter(tags=["Conversations"])

_clock = SystemClock()
_repository = InMemoryConversationRepository(_clock)
_service = ConversationService(_repository, _clock)


def _require_user_id(request: Request) -> str:
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized.",
        )
    return user.user_id


@router.post("/situations:suggest")
def suggest_situation(payload: SuggestSituationRequest) -> dict:
    _ = payload
    return {"detail": "Not implemented"}


@router.get("/conversations")
def list_conversations(
    request: Request,
    limit: int = 20,
    cursor: str | None = None,
    archived: bool | None = None,
    starred: bool | None = None,
    sort: str | None = None,
    q: str | None = None,
) -> dict:
    user_id = _require_user_id(request)
    items, next_cursor = _service.list(
        user_id=user_id,
        limit=limit,
        cursor=cursor,
        archived=archived,
        starred=starred,
        sort=sort,
        query=q,
    )
    return {
        "items": [
            {
                "conversation_id": item.conversation_id,
                "title": item.title,
                "started_at": item.started_at.isoformat(),
                "status": item.status,
            }
            for item in items
        ],
        "next_cursor": next_cursor,
    }


@router.post("/conversations")
def create_conversation(
    request: Request, payload: ConversationCreateRequest
) -> dict:
    user_id = _require_user_id(request)
    setup = ConversationSetup(
        formality=payload.setup.formality,
        situation=payload.setup.situation,
        initiator=payload.setup.initiator,
        grammar_focus=[
            GrammarTarget(
                id=item.get("id", ""),
                label=item.get("label", ""),
                description=item.get("description"),
            )
            for item in payload.setup.grammar_focus
        ],
    )
    conversation = _service.create(user_id, payload.title, setup)
    return {
        "conversation_id": conversation.conversation_id,
        "title": conversation.title,
        "started_at": conversation.started_at.isoformat(),
        "status": conversation.status,
        "setup": {
            "formality": setup.formality,
            "situation": setup.situation,
            "initiator": setup.initiator,
            "grammar_focus": [
                {
                    "id": item.id,
                    "label": item.label,
                    "description": item.description,
                }
                for item in setup.grammar_focus
            ],
        },
    }


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
def archive_conversation(request: Request, conversation_id: str) -> dict:
    user_id = _require_user_id(request)
    conversation = _service.archive(user_id, conversation_id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )
    return {
        "conversation_id": conversation.conversation_id,
        "title": conversation.title,
        "started_at": conversation.started_at.isoformat(),
        "status": conversation.status,
        "setup": (
            {
                "formality": conversation.setup.formality,
                "situation": conversation.setup.situation,
                "initiator": conversation.setup.initiator,
                "grammar_focus": conversation.setup.grammar_focus,
            }
            if conversation.setup
            else None
        ),
    }


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
