from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlencode
from urllib.request import Request as UrlRequest
from urllib.request import urlopen
import base64
import hashlib
import json
import secrets

import jwt
from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

JWKS_CLIENT: jwt.PyJWKClient | None = None


class AuthUser(BaseModel):
    user_id: str
    email: str
    display_name: Optional[str] = None
    created_at: datetime
    claims: dict


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_cognito_config() -> dict:
    region = require_env("COGNITO_DOMAIN_REGION")
    pool_id = require_env("COGNITO_DOMAIN_USER_POOL_ID")
    client_id = require_env("COGNITO_DOMAIN_CLIENT_ID")
    domain = require_env("COGNITO_DOMAIN")
    issuer = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}"
    jwks_url = f"{issuer}/.well-known/jwks.json"
    return {
        "region": region,
        "pool_id": pool_id,
        "client_id": client_id,
        "domain": domain,
        "issuer": issuer,
        "jwks_url": jwks_url,
    }


def get_jwks_client() -> jwt.PyJWKClient:
    global JWKS_CLIENT
    if JWKS_CLIENT is None:
        config = get_cognito_config()
        JWKS_CLIENT = jwt.PyJWKClient(config["jwks_url"])
    return JWKS_CLIENT


def extract_id_token(request: Request) -> str:
    header = request.headers.get("Authorization")
    if header:
        parts = header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]

    cookie_token = request.cookies.get("id_token")
    if cookie_token:
        return cookie_token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authorization token missing.",
    )


def decode_id_token(id_token: str) -> dict:
    config = get_cognito_config()
    signing_key = get_jwks_client().get_signing_key_from_jwt(id_token)
    if not signing_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find signing key.",
        )
    return jwt.decode(
        id_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=config["client_id"],
        issuer=config["issuer"],
    )


def build_user(payload: dict) -> AuthUser:
    cognito_id = payload.get("sub")
    email = payload.get("email")
    if not cognito_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cognito subject missing in token.",
        )
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email missing in token.",
        )

    created_at = payload.get("auth_time") or payload.get("iat")
    if created_at is None:
        created_at_dt = datetime.now(timezone.utc)
    else:
        created_at_dt = datetime.fromtimestamp(created_at, tz=timezone.utc)

    display_name = (
        payload.get("name")
        or payload.get("preferred_username")
        or payload.get("cognito:username")
    )

    return AuthUser(
        user_id=cognito_id,
        email=email,
        display_name=display_name,
        created_at=created_at_dt,
        claims=payload,
    )


def build_code_verifier() -> str:
    return secrets.token_urlsafe(64)


def build_code_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("utf-8")


def build_state() -> str:
    return secrets.token_urlsafe(32)


def build_login_url(redirect_uri: str, state: str, code_challenge: str) -> str:
    config = get_cognito_config()
    query = urlencode(
        {
            "response_type": "code",
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
    )
    return f"{config['domain']}/oauth2/authorize?{query}"


def exchange_code_for_tokens(
    code: str, redirect_uri: str, code_verifier: str
) -> dict:
    config = get_cognito_config()
    body = urlencode(
        {
            "grant_type": "authorization_code",
            "client_id": config["client_id"],
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
        }
    ).encode("utf-8")
    request = UrlRequest(
        f"{config['domain']}/oauth2/token",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(request) as response:
        payload = response.read()
        return json.loads(payload.decode("utf-8"))


def get_auth_cookie_samesite() -> str:
    return os.environ.get("AUTH_COOKIE_SAMESITE", "Lax")


def get_auth_cookie_secure(default_secure: bool) -> bool:
    override = os.environ.get("AUTH_COOKIE_SECURE")
    if override is None:
        return default_secure
    return override.lower() in {"1", "true", "yes", "on"}


def set_auth_cookies(response: Response, token_payload: dict, secure: bool) -> None:
    expires_in = int(token_payload.get("expires_in", 3600))
    access_token = token_payload.get("access_token")
    id_token = token_payload.get("id_token")
    refresh_token = token_payload.get("refresh_token")
    samesite = get_auth_cookie_samesite()
    secure_cookie = get_auth_cookie_secure(secure)

    if access_token:
        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
            secure=secure_cookie,
            samesite=samesite,
            max_age=expires_in,
        )
    if id_token:
        response.set_cookie(
            "id_token",
            id_token,
            httponly=True,
            secure=secure_cookie,
            samesite=samesite,
            max_age=expires_in,
        )
    if refresh_token:
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=secure_cookie,
            samesite=samesite,
            max_age=int(timedelta(days=30).total_seconds()),
        )


def clear_auth_cookies(response: Response) -> None:
    samesite = get_auth_cookie_samesite()
    secure_cookie = get_auth_cookie_secure(False)
    for name in (
        "access_token",
        "id_token",
        "refresh_token",
        "oauth_state",
        "pkce_verifier",
    ):
        response.delete_cookie(name, samesite=samesite, secure=secure_cookie)


def build_logout_url(logout_uri: str) -> str:
    config = get_cognito_config()
    query = urlencode(
        {
            "client_id": config["client_id"],
            "logout_uri": logout_uri,
        }
    )
    return f"{config['domain']}/logout?{query}"


def is_open_route(path: str) -> bool:
    if path == "/openapi.json":
        return True
    if path.startswith("/docs"):
        return True
    if path.startswith("/redoc"):
        return True
    if path in {"/health", "/favicon.ico"}:
        return True
    if path in {
        "/v1/login",
        "/v1/login_done",
        "/v1/logout",
        "/v1/logout_done",
    }:
        return True
    return False


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if is_open_route(request.url.path):
            return await call_next(request)

        try:
            id_token = extract_id_token(request)
            payload = decode_id_token(id_token)
            request.state.user = build_user(payload)
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )
        except Exception:
            logging.exception("Auth error")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Authentication configuration error."},
            )

        return await call_next(request)
