from __future__ import annotations

from datetime import date, timedelta

from ..domain import (
    DEFAULT_DAILY_TARGET,
    DashboardSnapshot,
    DailyCompletionRecord,
    DailyGoalStatus,
    GoalDefinition,
    GoalStreak,
)
from ..ports import Clock, DailyCompletionRepository, GoalRepository


class GoalService:
    def __init__(
        self,
        goal_repository: GoalRepository,
        completion_repository: DailyCompletionRepository,
        clock: Clock,
    ) -> None:
        self._goal_repository = goal_repository
        self._completion_repository = completion_repository
        self._clock = clock

    def update_goal_target(self, user_id: str, daily_unit_target: int) -> GoalDefinition:
        goal = GoalDefinition(
            daily_unit_target=daily_unit_target,
            updated_at=self._clock.now(),
        )
        self._goal_repository.save_goal(user_id, goal)
        return goal

    def record_daily_completion(
        self, user_id: str, day: date, completed: bool
    ) -> None:
        record = DailyCompletionRecord(date=day, completed=completed)
        self._completion_repository.set_completion(user_id, record)

    def get_dashboard(
        self, user_id: str, start_date: date, end_date: date
    ) -> DashboardSnapshot:
        goal = self._goal_repository.get_goal(user_id)
        if goal is None:
            goal = GoalDefinition(
                daily_unit_target=DEFAULT_DAILY_TARGET,
                updated_at=self._clock.now(),
            )

        completion_map = {
            record.date: record.completed
            for record in self._completion_repository.list_range(
                user_id, start_date, end_date
            )
        }

        calendar = [
            self._build_daily_status(
                day, goal.daily_unit_target, completion_map.get(day, False)
            )
            for day in _iter_dates(start_date, end_date)
        ]

        today = self._clock.today()
        today_completed = self._completion_repository.get_completion(user_id, today) or False
        today_status = self._build_daily_status(
            today, goal.daily_unit_target, today_completed
        )

        streak = self._build_streak(user_id, goal.daily_unit_target, today)

        return DashboardSnapshot(
            today=today_status,
            calendar=calendar,
            streak=streak,
        )

    def _build_daily_status(
        self, day: date, target: int, completed: bool
    ) -> DailyGoalStatus:
        completed_units = 1 if completed else 0
        achieved = completed_units >= target
        return DailyGoalStatus(
            date=day,
            completed_units=completed_units,
            target=target,
            achieved=achieved,
        )

    def _build_streak(self, user_id: str, target: int, today: date) -> GoalStreak:
        current = 0
        cursor = today
        last_achieved_date = None
        while True:
            completed = self._completion_repository.get_completion(user_id, cursor) or False
            achieved = (1 if completed else 0) >= target
            if not achieved:
                break
            if last_achieved_date is None:
                last_achieved_date = cursor
            current += 1
            cursor = cursor - timedelta(days=1)

        return GoalStreak(current=current, last_achieved_date=last_achieved_date)


def _iter_dates(start_date: date, end_date: date) -> list[date]:
    current = start_date
    dates: list[date] = []
    while current <= end_date:
        dates.append(current)
        current = current + timedelta(days=1)
    return dates
