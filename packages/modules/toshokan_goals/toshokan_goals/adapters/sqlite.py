from __future__ import annotations

import json
import sqlite3
from datetime import date
from typing import Optional
from uuid import UUID

from toshokan_platform.storage.helpers import dt_to_str, str_to_dt

from ..domain.entities import DailyGoalRecord, GoalResult
from ..ports.goals import DailyGoalRepository


def _goals_to_json(goals: list[GoalResult]) -> str:
    return json.dumps(
        [
            {
                "goal_type": g.goal_type,
                "label": g.label,
                "achieved": g.achieved,
                "current": g.current,
                "target": g.target,
            }
            for g in goals
        ]
    )


def _goals_from_json(value: str) -> list[GoalResult]:
    items = json.loads(value) if value else []
    return [
        GoalResult(
            goal_type=item["goal_type"],
            label=item["label"],
            achieved=item["achieved"],
            current=item["current"],
            target=item["target"],
        )
        for item in items
    ]


class SqliteDailyGoalRepository(DailyGoalRepository):
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save_record(self, record: DailyGoalRecord) -> DailyGoalRecord:
        self._connection.execute(
            """
            INSERT OR REPLACE INTO daily_goal_records (
                id, user_id, date, achieved, goals_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(record.id),
                str(record.user_id),
                record.date.isoformat(),
                int(record.achieved),
                _goals_to_json(record.goals),
                dt_to_str(record.created_at),
            ),
        )
        self._connection.commit()
        return record

    def get_record(self, user_id: UUID, target_date: date) -> Optional[DailyGoalRecord]:
        row = self._connection.execute(
            "SELECT * FROM daily_goal_records WHERE user_id = ? AND date = ?",
            (str(user_id), target_date.isoformat()),
        ).fetchone()
        return _row_to_record(row) if row else None

    def list_records(self, user_id: UUID, from_date: date, to_date: date) -> list[DailyGoalRecord]:
        rows = self._connection.execute(
            "SELECT * FROM daily_goal_records WHERE user_id = ? AND date >= ? AND date <= ? ORDER BY date ASC",
            (str(user_id), from_date.isoformat(), to_date.isoformat()),
        ).fetchall()
        return [_row_to_record(row) for row in rows]

    def get_streak(self, user_id: UUID) -> int:
        rows = self._connection.execute(
            "SELECT achieved FROM daily_goal_records WHERE user_id = ? ORDER BY date DESC",
            (str(user_id),),
        ).fetchall()
        streak = 0
        for row in rows:
            if row["achieved"]:
                streak += 1
            else:
                break
        return streak


def _row_to_record(row: sqlite3.Row) -> DailyGoalRecord:
    return DailyGoalRecord(
        id=UUID(row["id"]),
        user_id=UUID(row["user_id"]),
        date=date.fromisoformat(row["date"]),
        achieved=bool(row["achieved"]),
        goals=_goals_from_json(row["goals_json"]),
        created_at=str_to_dt(row["created_at"]),
    )
