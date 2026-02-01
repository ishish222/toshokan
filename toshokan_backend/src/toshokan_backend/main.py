from __future__ import annotations

from fastapi import FastAPI

from .api import (
    conversations,
    conversation_goals,
    dashboard,
    didascalia,
    identity,
    tools,
)


def create_app() -> FastAPI:
    app = FastAPI(title="Toshokan API")
    api_prefix = "/v1"
    app.include_router(identity.router, prefix=api_prefix)
    app.include_router(dashboard.router, prefix=api_prefix)
    app.include_router(conversation_goals.router, prefix=api_prefix)
    app.include_router(conversations.router, prefix=api_prefix)
    app.include_router(didascalia.router, prefix=api_prefix)
    app.include_router(tools.router, prefix=api_prefix)
    return app


app = create_app()
