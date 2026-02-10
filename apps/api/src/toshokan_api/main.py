from __future__ import annotations

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import AuthProvider, CognitoAuthProvider, HeaderAuthProvider, auth_middleware, get_auth_context
from .api import health
from .config import get_config
from .wiring import build_customer_accounts_components, build_customer_accounts_router, build_navigator_tests_router

load_dotenv(find_dotenv())


def _create_auth_provider(users) -> AuthProvider:
    """
    Create the appropriate auth provider based on environment configuration.

    Uses CognitoAuthProvider if COGNITO_USER_POOL_ID and COGNITO_REGION are set,
    otherwise falls back to HeaderAuthProvider (for testing).
    """
    config = get_config()
    cognito_pool_id = config.cognito_user_pool_id
    cognito_region = config.cognito_region

    if cognito_pool_id and cognito_region:
        cognito_client_id = config.cognito_client_id
        return CognitoAuthProvider(
            users=users,
            user_pool_id=cognito_pool_id,
            region=cognito_region,
            client_id=cognito_client_id,
        )

    # Fallback to simple header auth (for testing without Cognito)
    return HeaderAuthProvider(users)


def create_app(
    components=None,
    auth_provider: AuthProvider | None = None,
) -> FastAPI:
    openapi_tags = [
        {"name": "Auth"},
        {"name": "User"},
        {"name": "Customer"},
        {"name": "Invitations"},
        {"name": "Targets"},
        {"name": "Credentials"},
        {"name": "Tests"},
        {"name": "Reports"},
    ]
    config = get_config()
    app = FastAPI(title="Navigator API", openapi_tags=openapi_tags)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    api_prefix = config.api_prefix
    components = components or build_customer_accounts_components()
    app.state.customer_accounts_store = components.store
    app.state.auth_provider = auth_provider or _create_auth_provider(components.users)
    app.middleware("http")(auth_middleware)
    app.include_router(health.router, prefix=api_prefix)
    app.include_router(build_customer_accounts_router(components.service, get_auth_context), prefix=api_prefix)
    if config.module_nt_enabled:
        app.include_router(build_navigator_tests_router(get_auth_context), prefix=api_prefix)
    return app


app = create_app()
