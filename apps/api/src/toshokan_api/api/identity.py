from fastapi import APIRouter

from ..store import STORE
from ..schemas import User

router = APIRouter()


@router.get("/me", tags=["User"], summary="Get current user", response_model=User)
def get_current_user() -> User:
    return STORE.user
