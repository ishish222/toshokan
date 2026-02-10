from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Optional
from uuid import UUID

from ..domain.entities import DailyGoalRecord
from ..ports.goals import DailyGoalRepository


@dataclass
class InMemoryDailyGoalStore:
    """In-memory backing store keyed by (user_id, date)."""

    records: Dict[tuple[UUID, date], DailyGoalRecord] = field(default_factory=dict)


class InMemoryDailyGoalRepository(DailyGoalRepository):
    def __init__(self, store: InMemoryDailyGoalStore) -> None:
        self._store = store

    def save_record(self, record: DailyGoalRecord) -> DailyGoalRecord:
        self._store.records[(record.user_id, record.date)] = record
        return record

    def get_record(self, user_id: UUID, target_date: date) -> Optional[DailyGoalRecord]:
        return self._store.records.get((user_id, target_date))

    def list_records(self, user_id: UUID, from_date: date, to_date: date) -> list[DailyGoalRecord]:
        results = [
            record
            for (uid, d), record in self._store.records.items()
            if uid == user_id and from_date <= d <= to_date
        ]
        return sorted(results, key=lambda r: r.date)

    def get_streak(self, user_id: UUID) -> int:
        user_records = sorted(
            [r for (uid, _), r in self._store.records.items() if uid == user_id],
            key=lambda r: r.date,
            reverse=True,
        )
        streak = 0
        for record in user_records:
            if record.achieved:
                streak += 1
            else:
                break
        return streak
