from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from ..schemas import Me, MeDefaults, MeOnboarding

router = APIRouter(tags=["Identity"])


@router.get("/me", response_model=Me)
def get_me(request: Request) -> Me:
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized.",
        )

    return Me(
        user_id=user.user_id,
        email=user.email,
        created_at=user.created_at,
        display_name=user.display_name,
        onboarding=MeOnboarding(),
        defaults=MeDefaults(),
    )
