from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Dict, Optional
from uuid import UUID, uuid4

from toshokan_goals.app.service import DailyGoalsService
from toshokan_goals.domain.entities import DailyGoalRecord, GoalResult
from toshokan_goals.ports.goals import DailyGoalRepository, GoalProvider


# ---------- inline fakes ----------


class _FakeProvider(GoalProvider):
    def __init__(self, goals: list[GoalResult]) -> None:
        self._goals = goals

    def get_goals(self, user_id: UUID, target_date: date) -> list[GoalResult]:
        return list(self._goals)


@dataclass
class _FakeRepository(DailyGoalRepository):
    records: Dict[tuple[UUID, date], DailyGoalRecord] = field(default_factory=dict)

    def save_record(self, record: DailyGoalRecord) -> DailyGoalRecord:
        self.records[(record.user_id, record.date)] = record
        return record

    def get_record(self, user_id: UUID, target_date: date) -> Optional[DailyGoalRecord]:
        return self.records.get((user_id, target_date))

    def list_records(self, user_id: UUID, from_date: date, to_date: date) -> list[DailyGoalRecord]:
        results = [
            r for (uid, d), r in self.records.items()
            if uid == user_id and from_date <= d <= to_date
        ]
        return sorted(results, key=lambda r: r.date)

    def get_streak(self, user_id: UUID) -> int:
        user_records = sorted(
            [r for (uid, _), r in self.records.items() if uid == user_id],
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


# ---------- helpers ----------


_USER_ID = uuid4()


def _service(
    providers: list[GoalProvider] | None = None,
    repository: _FakeRepository | None = None,
    user_timezone: str = "UTC",
) -> tuple[DailyGoalsService, _FakeRepository]:
    repo = repository or _FakeRepository()
    svc = DailyGoalsService(
        providers=providers or [],
        repository=repo,
        get_user_timezone=lambda _uid: user_timezone,
    )
    return svc, repo


def _record(target_date: date, achieved: bool) -> DailyGoalRecord:
    return DailyGoalRecord(
        id=uuid4(),
        user_id=_USER_ID,
        date=target_date,
        achieved=achieved,
        goals=[],
        created_at=datetime.now(timezone.utc),
    )


# ---------- domain tests ----------


def test_goal_result_is_frozen():
    g = GoalResult(goal_type="grammar", label="Grammar", achieved=True, current=5, target=5)
    try:
        g.current = 10  # type: ignore[misc]
        assert False, "Should be frozen"
    except AttributeError:
        pass


def test_daily_goal_record_is_frozen():
    r = _record(date(2025, 1, 1), True)
    try:
        r.achieved = False  # type: ignore[misc]
        assert False, "Should be frozen"
    except AttributeError:
        pass


# ---------- service: evaluate_day ----------


def test_evaluate_day_all_achieved():
    provider = _FakeProvider([
        GoalResult(goal_type="grammar", label="Grammar", achieved=True, current=5, target=5),
        GoalResult(goal_type="kanji", label="Kanji", achieved=True, current=10, target=10),
    ])
    svc, repo = _service(providers=[provider])
    record = svc.evaluate_day(user_id=_USER_ID, target_date=date(2025, 6, 15))
    assert record.achieved is True
    assert len(record.goals) == 2
    assert record.date == date(2025, 6, 15)
    assert repo.get_record(_USER_ID, date(2025, 6, 15)) is not None


def test_evaluate_day_partial():
    provider = _FakeProvider([
        GoalResult(goal_type="grammar", label="Grammar", achieved=True, current=5, target=5),
        GoalResult(goal_type="kanji", label="Kanji", achieved=False, current=3, target=10),
    ])
    svc, repo = _service(providers=[provider])
    record = svc.evaluate_day(user_id=_USER_ID, target_date=date(2025, 6, 15))
    assert record.achieved is False


def test_evaluate_day_no_providers():
    svc, _repo = _service(providers=[])
    record = svc.evaluate_day(user_id=_USER_ID, target_date=date(2025, 6, 15))
    assert record.achieved is True
    assert record.goals == []


# ---------- service: streak ----------


def test_streak_continuous_chain():
    repo = _FakeRepository()
    repo.save_record(_record(date(2025, 6, 13), True))
    repo.save_record(_record(date(2025, 6, 14), True))
    repo.save_record(_record(date(2025, 6, 15), True))
    svc, _ = _service(repository=repo)
    assert svc.get_streak(_USER_ID) == 3


def test_streak_resets_on_miss():
    repo = _FakeRepository()
    repo.save_record(_record(date(2025, 6, 13), True))
    repo.save_record(_record(date(2025, 6, 14), False))
    repo.save_record(_record(date(2025, 6, 15), True))
    svc, _ = _service(repository=repo)
    assert svc.get_streak(_USER_ID) == 1


def test_streak_all_missed():
    repo = _FakeRepository()
    repo.save_record(_record(date(2025, 6, 14), False))
    repo.save_record(_record(date(2025, 6, 15), False))
    svc, _ = _service(repository=repo)
    assert svc.get_streak(_USER_ID) == 0


def test_streak_empty():
    svc, _ = _service()
    assert svc.get_streak(_USER_ID) == 0


# ---------- service: today ----------


def test_today_with_no_providers():
    svc, _ = _service(providers=[])
    result = svc.get_today(user_id=_USER_ID)
    assert result["achieved"] is True
    assert result["goals"] == []
    assert result["streak"] == 0


def test_today_aggregates_providers():
    p1 = _FakeProvider([GoalResult("grammar", "Grammar", True, 5, 5)])
    p2 = _FakeProvider([GoalResult("kanji", "Kanji", False, 3, 10)])
    svc, _ = _service(providers=[p1, p2])
    result = svc.get_today(user_id=_USER_ID)
    assert result["achieved"] is False
    assert len(result["goals"]) == 2


# ---------- service: calendar ----------


def test_calendar_returns_range():
    repo = _FakeRepository()
    repo.save_record(_record(date(2025, 6, 10), True))
    repo.save_record(_record(date(2025, 6, 11), False))
    repo.save_record(_record(date(2025, 6, 15), True))
    svc, _ = _service(repository=repo)
    records = svc.get_calendar(_USER_ID, date(2025, 6, 10), date(2025, 6, 12))
    assert len(records) == 2
    assert records[0].date == date(2025, 6, 10)
    assert records[1].date == date(2025, 6, 11)
