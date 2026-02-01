from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard")
def get_dashboard() -> dict:
    return {"detail": "Not implemented"}
