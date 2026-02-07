from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel


class SuggestSituationRequest(BaseModel):
    formality: Literal["formal", "informal"]


class ConversationSetupPatch(BaseModel):
    formality: Optional[Literal["formal", "informal"]] = None
    situation: Optional[str] = None
    initiator: Optional[Literal["system", "user"]] = None
    grammar_focus: Optional[List[dict]] = None


class ConversationGoalsUpdate(BaseModel):
    daily_unit_target: int


class UserMessage(BaseModel):
    text: str
    input_language: Optional[str] = None
    hiragana_hint_enabled: Optional[bool] = None


class CreateTurnRequest(BaseModel):
    user_message: UserMessage
    client_context: Optional[dict] = None


class ConversationPreferencesPatch(BaseModel):
    hiragana_hint_enabled: Optional[bool] = None


class DictionaryLookupRequest(BaseModel):
    query: str
    direction: Literal["en_to_ja", "ja_to_en"]
    limit: Optional[int] = 5


class MeOnboarding(BaseModel):
    goals_configured: bool = False


class MeDefaults(BaseModel):
    hiragana_hint_enabled: bool = False


class Me(BaseModel):
    user_id: str
    email: str
    created_at: datetime
    display_name: Optional[str] = None
    onboarding: Optional[MeOnboarding] = None
    defaults: Optional[MeDefaults] = None
