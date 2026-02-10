from __future__ import annotations

from typing import Iterable
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from navigator_api.auth import AuthContext, get_auth_context
from navigator_api.main import create_app


def _default_customer_ids(store) -> list[UUID]:
    return [customer_id for customer_id in store.customers.keys()]


def _make_auth(app: FastAPI, groups: Iterable[str], customer_ids: list[UUID] | None = None) -> AuthContext:
    store = app.state.customer_accounts_store
    return AuthContext(
        user_id=store.current_user_id,
        groups=list(groups),
        customer_ids=customer_ids or _default_customer_ids(store),
    )


def _client_for(app: FastAPI, auth: AuthContext) -> TestClient:
    app.dependency_overrides[get_auth_context] = lambda: auth
    return TestClient(app)


@pytest.fixture
def app_base() -> FastAPI:
    import os
    from navigator_api.config import get_config
    # Force in-memory backend and clear seed data for test isolation
    os.environ["API_STORAGE_BACKEND"] = "memory"
    os.environ.pop("SEED_DATA_PATH", None)
    get_config.cache_clear()
    return create_app()


@pytest.fixture
def client_user(app_base: FastAPI) -> TestClient:
    auth = _make_auth(app_base, groups=["user"])
    return _client_for(app_base, auth)


@pytest.fixture
def client_backoffice(app_base: FastAPI) -> TestClient:
    auth = _make_auth(app_base, groups=["backoffice"])
    return _client_for(app_base, auth)
