from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Auth"], summary="Health check")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
