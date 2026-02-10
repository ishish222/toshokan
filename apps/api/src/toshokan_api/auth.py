from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Optional, Protocol
from urllib.request import urlopen
from uuid import UUID
import json

import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, Request, status

from customer_accounts.ports import UserRepository


logger = logging.getLogger(__name__)

BACKOFFICE_GROUPS = {"backoffice", "admin"}


@dataclass(frozen=True)
class AuthContext:
    user_id: UUID
    groups: list[str]
    customer_ids: list[UUID]

    @property
    def is_backoffice(self) -> bool:
        return any(group in BACKOFFICE_GROUPS for group in self.groups)


class AuthProvider(Protocol):
    def authenticate(self, request: Request) -> Optional[AuthContext]:
        raise NotImplementedError


class HeaderAuthProvider:
    """Simple auth provider that uses user ID directly from Bearer token (for testing)."""

    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def authenticate(self, request: Request) -> Optional[AuthContext]:
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return None
        try:
            user_id = UUID(token)
        except ValueError:
            return None
        user = self._users.get_user(user_id)
        if user is None:
            return None
        groups_header = request.headers.get("X-User-Groups")
        groups = [group.strip() for group in groups_header.split(",")] if groups_header else (user.roles or [])
        return AuthContext(user_id=user.id, groups=groups, customer_ids=list(user.customer_ids))


class CognitoAuthProvider:
    """
    Auth provider that validates AWS Cognito JWT tokens.
    
    Environment variables:
    - COGNITO_USER_POOL_ID: The Cognito User Pool ID (e.g., "eu-central-1_SMPYtAEFp")
    - COGNITO_REGION: AWS region (e.g., "eu-central-1")
    - COGNITO_CLIENT_ID: Optional. If set, validates the 'aud' or 'client_id' claim.
    """

    def __init__(
        self,
        users: UserRepository,
        user_pool_id: Optional[str] = None,
        region: Optional[str] = None,
        client_id: Optional[str] = None,
    ) -> None:
        self._users = users
        self._user_pool_id = user_pool_id or os.getenv("COGNITO_USER_POOL_ID", "")
        self._region = region or os.getenv("COGNITO_REGION", "")
        self._client_id = client_id or os.getenv("COGNITO_CLIENT_ID")
        
        if not self._user_pool_id or not self._region:
            raise ValueError("COGNITO_USER_POOL_ID and COGNITO_REGION must be set")
        
        self._issuer = f"https://cognito-idp.{self._region}.amazonaws.com/{self._user_pool_id}"
        self._jwks_url = f"{self._issuer}/.well-known/jwks.json"
        self._jwks_client = PyJWKClient(self._jwks_url)

    def authenticate(self, request: Request) -> Optional[AuthContext]:
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return None
        
        try:
            # Get the signing key from JWKS
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)
            
            # Decode and validate the token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=self._issuer,
                options={
                    "verify_aud": False,  # Access tokens don't have 'aud', they have 'client_id'
                    "verify_exp": True,
                    "verify_iss": True,
                },
            )
            
            # Validate client_id if configured (for access tokens)
            if self._client_id:
                token_client_id = payload.get("client_id")
                if token_client_id != self._client_id:
                    logger.warning(f"Token client_id mismatch: expected {self._client_id}, got {token_client_id}")
                    return None
            
            # Validate token_use claim (should be 'access' for API calls)
            token_use = payload.get("token_use")
            if token_use != "access":
                logger.warning(f"Invalid token_use: expected 'access', got {token_use}")
                return None
            
            # Extract user information
            cognito_sub = payload.get("sub")
            if not cognito_sub:
                logger.warning("Token missing 'sub' claim")
                return None
            
            # Extract groups from cognito:groups claim
            cognito_groups = payload.get("cognito:groups", [])
            
            # Look up user by cognito_id (which matches the Cognito sub claim)
            user = self._users.get_user_by_cognito_id(cognito_sub)
            if user is not None:
                # Use groups from our store if available, otherwise use Cognito groups
                groups = user.roles if user.roles else cognito_groups
                customer_ids = list(user.customer_ids)
                user_id = user.id
            else:
                # User not in our store yet - use Cognito groups, empty customer_ids
                # This allows authenticated users to exist before registration is complete
                groups = cognito_groups
                customer_ids = []
                user_id = None  # No local user ID yet
                logger.info(f"User with cognito_id={cognito_sub} authenticated via Cognito but not found in local store")
            
            # We need a user_id for AuthContext - if not found, generate a placeholder
            # This allows partial auth for users who haven't completed registration
            if user_id is None:
                # For unregistered users, we can't provide full access
                # They can only call registration endpoints
                from uuid import UUID
                user_id = UUID('00000000-0000-0000-0000-000000000000')  # Placeholder
            
            return AuthContext(user_id=user_id, groups=groups, customer_ids=customer_ids)
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error during authentication: {e}")
            return None


async def auth_middleware(request: Request, call_next):
    provider: Optional[AuthProvider] = getattr(request.app.state, "auth_provider", None)
    request.state.auth = provider.authenticate(request) if provider else None
    return await call_next(request)


def get_auth_context(request: Request) -> AuthContext:
    auth: Optional[AuthContext] = getattr(request.state, "auth", None)
    if auth is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return auth
