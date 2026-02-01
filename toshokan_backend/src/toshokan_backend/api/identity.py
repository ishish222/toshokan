from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["Identity"])


@router.get("/me")
def get_me() -> dict:
    return {"detail": "Not implemented"}
