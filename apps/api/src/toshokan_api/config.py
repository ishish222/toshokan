from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from customer_accounts.config import CustomerAccountsConfig, get_config as get_ca_config


DEFAULT_CORS_ORIGINS = [
    "https://dashboard.local:3000",
    "https://127.0.0.1:3000",
    "https://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]


def _split_env_list(value: Optional[str], default: list[str]) -> list[str]:
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def _env_bool(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class ApiConfig:
    api_prefix: str
    cors_allow_origins: list[str]
    cognito_user_pool_id: Optional[str]
    cognito_region: Optional[str]
    cognito_client_id: Optional[str]
    storage_backend: str
    sqlite_path: str
    module_ca_enabled: bool
    customer_accounts: Optional[CustomerAccountsConfig]
    module_nt_enabled: bool


@lru_cache
def get_config() -> ApiConfig:
    module_ca_enabled = _env_bool("MODULE_CA_ENABLED", True)
    module_nt_enabled = _env_bool("MODULE_NAVIGATOR_TESTS_ENABLED", True)
    return ApiConfig(
        api_prefix=os.getenv("API_PREFIX", "/v1"),
        cors_allow_origins=_split_env_list(os.getenv("CORS_ALLOW_ORIGINS"), DEFAULT_CORS_ORIGINS),
        cognito_user_pool_id=os.getenv("COGNITO_USER_POOL_ID"),
        cognito_region=os.getenv("COGNITO_REGION"),
        cognito_client_id=os.getenv("COGNITO_CLIENT_ID"),
        storage_backend=os.getenv("API_STORAGE_BACKEND", "sqlite").strip().lower(),
        sqlite_path=os.getenv("API_SQLITE_PATH", "/tmp/navigator.sqlite"),
        module_ca_enabled=module_ca_enabled,
        customer_accounts=get_ca_config() if module_ca_enabled else None,
        module_nt_enabled=module_nt_enabled,
    )
