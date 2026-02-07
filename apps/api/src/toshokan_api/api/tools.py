from __future__ import annotations

from fastapi import APIRouter

from ..schemas import DictionaryLookupRequest

router = APIRouter(tags=["Tools"])


@router.post("/tools/dictionary:lookup")
def dictionary_lookup(payload: DictionaryLookupRequest) -> dict:
    _ = payload
    return {"detail": "Not implemented"}
