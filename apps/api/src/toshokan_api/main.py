from __future__ import annotations

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import conversations, didascalia, identity, tools
from .auth import AuthMiddleware
from toshokan_conversation.api import conversation_goals, grammar_targets
from toshokan_conversation.adapters import (
    load_default_grammar_targets,
    set_default_grammar_targets,
)
from toshokan_goals.api import router as goals_router

load_dotenv(find_dotenv())


def create_app() -> FastAPI:
    app = FastAPI(title="Toshokan API")
    app.add_middleware(AuthMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://dashboard.local:3000",
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
    app.include_router(goals_router, prefix=api_prefix)
    app.include_router(conversation_goals.router, prefix=api_prefix)
    app.include_router(grammar_targets.router, prefix=api_prefix)
    app.include_router(conversations.router, prefix=api_prefix)
    app.include_router(didascalia.router, prefix=api_prefix)
    app.include_router(tools.router, prefix=api_prefix)

    @app.on_event("startup")
    def _load_default_grammar_targets() -> None:
        set_default_grammar_targets(load_default_grammar_targets())

    return app


app = create_app()
