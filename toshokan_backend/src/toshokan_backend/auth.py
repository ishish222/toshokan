from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Optional

import jwt
from fastapi import HTTPException, Request, status
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
    issuer = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}"
    jwks_url = f"{issuer}/.well-known/jwks.json"
    return {
        "region": region,
        "pool_id": pool_id,
        "client_id": client_id,
        "issuer": issuer,
        "jwks_url": jwks_url,
    }


def get_jwks_client() -> jwt.PyJWKClient:
    global JWKS_CLIENT
    if JWKS_CLIENT is None:
        config = get_cognito_config()
        JWKS_CLIENT = jwt.PyJWKClient(config["jwks_url"])
    return JWKS_CLIENT


def extract_bearer_token(request: Request) -> str:
    header = request.headers.get("Authorization")
    if not header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing.",
        )
    parts = header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format.",
        )
    return parts[1]


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


def is_open_route(path: str) -> bool:
    if path == "/openapi.json":
        return True
    if path.startswith("/docs"):
        return True
    if path.startswith("/redoc"):
        return True
    if path in {"/health", "/favicon.ico"}:
        return True
    return False


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if is_open_route(request.url.path):
            return await call_next(request)

        try:
            id_token = extract_bearer_token(request)
            payload = decode_id_token(id_token)
            request.state.user = build_user(payload)
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )
        except Exception as exc:
            logging.exception("Auth error")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Authentication configuration error."},
            )

        return await call_next(request)
