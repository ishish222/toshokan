from __future__ import annotations

from datetime import date
from uuid import UUID

from ..domain.entities import GoalResult
from ..ports.goals import GoalProvider


class FakeGoalProvider(GoalProvider):
    """Demo goal provider returning dummy grammar/kanji goals.

    Useful for testing and development before real goal modules exist.
    """

    def get_goals(self, user_id: UUID, target_date: date) -> list[GoalResult]:
        return [
            GoalResult(
                goal_type="grammar",
                label="Grammar reviews",
                achieved=True,
                current=5,
                target=5,
            ),
            GoalResult(
                goal_type="kanji",
                label="Kanji reviews",
                achieved=False,
                current=3,
                target=10,
            ),
        ]
