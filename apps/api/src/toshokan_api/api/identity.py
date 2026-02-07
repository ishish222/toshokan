from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from ..auth import (
    build_code_challenge,
    build_code_verifier,
    build_login_url,
    build_logout_url,
    build_state,
    clear_auth_cookies,
    exchange_code_for_tokens,
    set_auth_cookies,
)
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


def get_frontend_base_url() -> str:
    return os.environ.get("FRONTEND_BASE_URL", "https://dashboard.local:3000")


def get_login_redirect_uri() -> str:
    override = os.environ.get("COGNITO_DOMAIN_REDIRECT_URI_LOGIN")
    if override:
        return override
    return f"{get_frontend_base_url()}/login_done"


def get_logout_redirect_uri() -> str:
    override = os.environ.get("COGNITO_DOMAIN_REDIRECT_URI_LOGOUT")
    if override:
        return override
    return f"{get_frontend_base_url()}/logout_done"


@router.get("/login")
def login(request: Request) -> RedirectResponse:
    code_verifier = build_code_verifier()
    state = build_state()
    code_challenge = build_code_challenge(code_verifier)
    login_url = build_login_url(get_login_redirect_uri(), state, code_challenge)

    response = RedirectResponse(login_url)
    secure_cookie = request.url.scheme == "https"
    response.set_cookie(
        "pkce_verifier",
        code_verifier,
        httponly=True,
        secure=secure_cookie,
        samesite="Lax",
        max_age=600,
    )
    response.set_cookie(
        "oauth_state",
        state,
        httponly=True,
        secure=secure_cookie,
        samesite="Lax",
        max_age=600,
    )
    return response


@router.get("/login_done")
def login_done(request: Request) -> RedirectResponse:
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    if not code or not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code or state.",
        )

    stored_state = request.cookies.get("oauth_state")
    if not stored_state or stored_state != state:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OAuth state.",
        )

    code_verifier = request.cookies.get("pkce_verifier")
    if not code_verifier:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing PKCE verifier.",
        )

    token_payload = exchange_code_for_tokens(
        code, get_login_redirect_uri(), code_verifier
    )

    response = RedirectResponse(
        f"{get_login_redirect_uri()}?done=1",
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )
    secure_cookie = request.url.scheme == "https"
    set_auth_cookies(response, token_payload, secure=secure_cookie)
    response.delete_cookie("pkce_verifier")
    response.delete_cookie("oauth_state")
    return response


@router.get("/logout")
def logout() -> RedirectResponse:
    logout_url = build_logout_url(get_logout_redirect_uri())
    response = RedirectResponse(logout_url)
    clear_auth_cookies(response)
    return response


@router.get("/logout_done")
def logout_done() -> dict:
    return {"ok": True}
