from __future__ import annotations

from pydantic import BaseModel


class ConversationGoalsUpdate(BaseModel):
    daily_unit_target: int
