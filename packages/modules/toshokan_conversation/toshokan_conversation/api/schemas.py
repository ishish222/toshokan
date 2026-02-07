from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConversationGoals(BaseModel):
    daily_unit_target: int
    updated_at: datetime

    model_config = ConfigDict(extra="forbid")


class ConversationGoalsUpdate(BaseModel):
    daily_unit_target: int

    model_config = ConfigDict(extra="forbid")
