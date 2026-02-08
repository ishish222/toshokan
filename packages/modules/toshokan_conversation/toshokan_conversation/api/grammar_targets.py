from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from ..adapters import get_default_grammar_targets
from .schemas import GrammarTargetResponse

router = APIRouter(tags=["ConversationGoals"])


@router.get("/modules/toshokan_conversation/grammar-targets")
def list_grammar_targets(request: Request) -> list[GrammarTargetResponse]:
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized.",
        )

    return [
        GrammarTargetResponse(
            id=target.id,
            label=target.label,
            description=target.description,
        )
        for target in get_default_grammar_targets()
    ]
