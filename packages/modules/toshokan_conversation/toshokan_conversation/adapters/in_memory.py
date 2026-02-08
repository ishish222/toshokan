from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

from ..domain import Conversation, ConversationSetup
from ..ports import Clock, ConversationRepository


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class InMemoryConversationRepository(ConversationRepository):
    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._store: dict[str, list[Conversation]] = {}

    def create(
        self, user_id: str, title: str | None, setup: ConversationSetup
    ) -> Conversation:
        conversation = Conversation(
            conversation_id=str(uuid4()),
            title=title,
            started_at=self._clock.now(),
            status="active",
            setup=setup,
        )
        self._store.setdefault(user_id, []).insert(0, conversation)
        return conversation

    def list(
        self,
        user_id: str,
        limit: int = 20,
        cursor: str | None = None,
        archived: bool | None = None,
        starred: bool | None = None,
        sort: str | None = None,
        query: str | None = None,
    ) -> tuple[list[Conversation], str | None]:
        _ = archived
        _ = starred
        _ = sort
        _ = query
        items = list(self._store.get(user_id, []))
        start_index = int(cursor) if cursor and cursor.isdigit() else 0
        page = items[start_index:start_index + limit]
        next_cursor = (
            str(start_index + limit) if start_index + limit < len(items) else None
        )
        return page, next_cursor

    def archive(self, user_id: str, conversation_id: str) -> Conversation | None:
        items = self._store.get(user_id, [])
        for index, item in enumerate(items):
            if item.conversation_id == conversation_id:
                archived = replace(item, status="archived")
                items[index] = archived
                return archived
        return None
