from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class ToshokanGoalsConfig:
    demo_data_enabled: bool


@lru_cache
def get_config() -> ToshokanGoalsConfig:
    demo_raw = os.getenv("GOALS_DEMO_DATA_ENABLED", "true").strip().lower()
    return ToshokanGoalsConfig(
        demo_data_enabled=demo_raw in {"1", "true", "yes", "y", "on"},
    )
