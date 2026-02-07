from __future__ import annotations

from datetime import date, datetime, timezone

from toshokan_goals.adapters.in_memory import (
    InMemoryDailyCompletionRepository,
    InMemoryGoalRepository,
)
from toshokan_goals.app import GoalService
from toshokan_goals.domain import GoalDefinition


class FixedClock:
    def __init__(self, today: date) -> None:
        self._today = today

    def today(self) -> date:
        return self._today

    def now(self) -> datetime:
        return datetime.combine(self._today, datetime.min.time(), tzinfo=timezone.utc)


def test_dashboard_streak_counts_consecutive_days() -> None:
    goal_repo = InMemoryGoalRepository()
    completion_repo = InMemoryDailyCompletionRepository()
    clock = FixedClock(date(2026, 2, 7))
    service = GoalService(goal_repo, completion_repo, clock)

    goal_repo.save_goal(
        "user-1",
        GoalDefinition(daily_unit_target=1, updated_at=clock.now()),
    )

    service.record_daily_completion("user-1", date(2026, 2, 7), True)
    service.record_daily_completion("user-1", date(2026, 2, 6), True)
    service.record_daily_completion("user-1", date(2026, 2, 5), False)

    snapshot = service.get_dashboard("user-1", date(2026, 2, 1), date(2026, 2, 7))

    assert snapshot.streak.current == 2
    assert snapshot.streak.last_achieved_date == date(2026, 2, 7)


def test_calendar_includes_each_day_in_range() -> None:
    goal_repo = InMemoryGoalRepository()
    completion_repo = InMemoryDailyCompletionRepository()
    clock = FixedClock(date(2026, 2, 7))
    service = GoalService(goal_repo, completion_repo, clock)

    goal_repo.save_goal(
        "user-1",
        GoalDefinition(daily_unit_target=1, updated_at=clock.now()),
    )
    service.record_daily_completion("user-1", date(2026, 2, 3), True)

    snapshot = service.get_dashboard("user-1", date(2026, 2, 1), date(2026, 2, 3))

    assert [day.date for day in snapshot.calendar] == [
        date(2026, 2, 1),
        date(2026, 2, 2),
        date(2026, 2, 3),
    ]
    assert snapshot.calendar[-1].achieved is True
