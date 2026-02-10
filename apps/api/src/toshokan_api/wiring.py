from __future__ import annotations

import os

from customer_accounts.api import create_router as create_customer_accounts_router
from customer_accounts.wiring import CustomerAccountsComponents
from customer_accounts.wiring import build as build_customer_accounts
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
