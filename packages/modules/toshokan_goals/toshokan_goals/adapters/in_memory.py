from __future__ import annotations

from datetime import date, datetime, timezone

from ..domain import DailyCompletionRecord, GoalDefinition
from ..ports import Clock, DailyCompletionRepository, GoalRepository


class InMemoryGoalRepository(GoalRepository):
    def __init__(self) -> None:
        self._goals: dict[str, GoalDefinition] = {}

    def get_goal(self, user_id: str) -> GoalDefinition | None:
        return self._goals.get(user_id)

    def save_goal(self, user_id: str, goal: GoalDefinition) -> None:
        self._goals[user_id] = goal


class InMemoryDailyCompletionRepository(DailyCompletionRepository):
    def __init__(self) -> None:
        self._completions: dict[str, dict[date, bool]] = {}

    def get_completion(self, user_id: str, day: date) -> bool | None:
        return self._completions.get(user_id, {}).get(day)

    def set_completion(self, user_id: str, record: DailyCompletionRecord) -> None:
        self._completions.setdefault(user_id, {})[record.date] = record.completed

    def list_range(
        self, user_id: str, start_date: date, end_date: date
    ) -> list[DailyCompletionRecord]:
        user_map = self._completions.get(user_id, {})
        records = []
        for day, completed in user_map.items():
            if start_date <= day <= end_date:
                records.append(DailyCompletionRecord(date=day, completed=completed))
        return records


class SystemClock(Clock):
    def today(self) -> date:
        return datetime.now(timezone.utc).date()

    def now(self) -> datetime:
        return datetime.now(timezone.utc)
