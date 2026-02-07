from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import (
    conversations,
    conversation_goals,
    dashboard,
    didascalia,
    identity,
    tools,
)
from .auth import AuthMiddleware


def create_app() -> FastAPI:
    app = FastAPI(title="Toshokan API")
    app.add_middleware(AuthMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://127.0.0.1:3000",
            "https://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    api_prefix = "/v1"
    app.include_router(identity.router, prefix=api_prefix)
    app.include_router(dashboard.router, prefix=api_prefix)
    app.include_router(conversation_goals.router, prefix=api_prefix)
    app.include_router(conversations.router, prefix=api_prefix)
    app.include_router(didascalia.router, prefix=api_prefix)
    app.include_router(tools.router, prefix=api_prefix)
    return app


app = create_app()
