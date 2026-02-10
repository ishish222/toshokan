from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Callable, Optional
from uuid import UUID

from .adapters.fake_goal_provider import FakeGoalProvider
from .adapters.in_memory import InMemoryDailyGoalRepository, InMemoryDailyGoalStore
from .adapters.sqlite import SqliteDailyGoalRepository
from .adapters.sqlite_schema import ensure_schema as ensure_goals_schema
from .app import DailyGoalsService
from .config import ToshokanGoalsConfig
from .ports.goals import GoalProvider


@dataclass(frozen=True)
class ToshokanGoalsComponents:
    service: DailyGoalsService
    store: Optional[InMemoryDailyGoalStore]


def build(
    *,
    storage_backend: str,
    config: ToshokanGoalsConfig,
    get_user_timezone: Callable[[UUID], Optional[str]],
    sqlite_connection: sqlite3.Connection | None = None,
    extra_providers: list[GoalProvider] | None = None,
) -> ToshokanGoalsComponents:
    store: Optional[InMemoryDailyGoalStore] = None

    if storage_backend == "sqlite":
        assert sqlite_connection is not None, "sqlite_connection required for sqlite backend"
        ensure_goals_schema(sqlite_connection)
        repository = SqliteDailyGoalRepository(sqlite_connection)
    else:
        store = InMemoryDailyGoalStore()
        repository = InMemoryDailyGoalRepository(store)

    providers: list[GoalProvider] = list(extra_providers or [])
    if config.demo_data_enabled:
        providers.append(FakeGoalProvider())

    service = DailyGoalsService(
        providers=providers,
        repository=repository,
        get_user_timezone=get_user_timezone,
    )
    return ToshokanGoalsComponents(service=service, store=store)
