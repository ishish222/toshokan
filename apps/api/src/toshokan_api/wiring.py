from __future__ import annotations

import os
from typing import Optional
from uuid import UUID

from customer_accounts.api import create_router as create_customer_accounts_router
from customer_accounts.ports import UserRepository
from customer_accounts.wiring import CustomerAccountsComponents
from customer_accounts.wiring import build as build_customer_accounts
from toshokan_goals.api import create_router as create_goals_router
from toshokan_goals.wiring import ToshokanGoalsComponents
from toshokan_goals.wiring import build as build_goals
from toshokan_platform.storage.sqlite import get_sqlite_connection

from .config import get_config


def build_customer_accounts_components() -> CustomerAccountsComponents:
    config = get_config()
    sqlite_connection = get_sqlite_connection(config.sqlite_path) if config.storage_backend == "sqlite" else None
    return build_customer_accounts(
        storage_backend=config.storage_backend,
        config=config.customer_accounts,
        sqlite_connection=sqlite_connection,
        seed_data_path=os.getenv("SEED_DATA_PATH"),
    )


def build_customer_accounts_router(service, get_auth_context):
    return create_customer_accounts_router(service, get_auth_context=get_auth_context)


def _make_get_user_timezone(users: UserRepository):
    """Create a callable that looks up a user's timezone from the user repository."""

    def get_user_timezone(user_id: UUID) -> Optional[str]:
        user = users.get_user(user_id)
        return user.timezone if user else None

    return get_user_timezone


def build_goals_components(users: UserRepository) -> ToshokanGoalsComponents:
    config = get_config()
    sqlite_connection = get_sqlite_connection(config.sqlite_path) if config.storage_backend == "sqlite" else None
    return build_goals(
        storage_backend=config.storage_backend,
        config=config.toshokan_goals,
        get_user_timezone=_make_get_user_timezone(users),
        sqlite_connection=sqlite_connection,
    )


def build_goals_router(service, get_auth_context):
    return create_goals_router(service, get_auth_context=get_auth_context)
