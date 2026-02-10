from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _env_bool(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(name: str, default: int, minimum: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return max(minimum, int(raw_value))
    except ValueError:
        return default


@dataclass(frozen=True)
class CustomerAccountsConfig:
    invitation_ttl_days: int
    demo_data_enabled: bool


@lru_cache
def get_config() -> CustomerAccountsConfig:
    return CustomerAccountsConfig(
        invitation_ttl_days=_env_int("CA_INVITATION_TTL_DAYS", default=7, minimum=1),
        demo_data_enabled=_env_bool("CA_DEMO_DATA_ENABLED", default=True),
    )
