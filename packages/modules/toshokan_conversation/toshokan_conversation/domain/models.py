from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


DEFAULT_DAILY_UNIT_TARGET = 1


@dataclass(frozen=True)
class ConversationGoalSettings:
    daily_unit_target: int
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.daily_unit_target < 1:
            raise ValueError("daily_unit_target must be >= 1.")
