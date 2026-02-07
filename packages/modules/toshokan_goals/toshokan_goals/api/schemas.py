from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict

from ..domain import DashboardSnapshot


class DashboardToday(BaseModel):
    completed: int
    target: int
    achieved: bool

    model_config = ConfigDict(extra="forbid")


class DashboardCalendarDay(BaseModel):
    date: date
    completed: int
    target: int
    achieved: bool

    model_config = ConfigDict(extra="forbid")


class DashboardStreak(BaseModel):
    current: int
    last_achieved_date: date | None = None

    model_config = ConfigDict(extra="forbid")


class DashboardResponse(BaseModel):
    today: DashboardToday
    calendar: list[DashboardCalendarDay]
    streak: DashboardStreak

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def from_snapshot(cls, snapshot: DashboardSnapshot) -> "DashboardResponse":
        return cls(
            today=DashboardToday(
                completed=snapshot.today.completed_units,
                target=snapshot.today.target,
                achieved=snapshot.today.achieved,
            ),
            calendar=[
                DashboardCalendarDay(
                    date=day.date,
                    completed=day.completed_units,
                    target=day.target,
                    achieved=day.achieved,
                )
                for day in snapshot.calendar
            ],
            streak=DashboardStreak(
                current=snapshot.streak.current,
                last_achieved_date=snapshot.streak.last_achieved_date,
            ),
        )
