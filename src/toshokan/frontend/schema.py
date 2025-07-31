from pydantic import BaseModel, Field


class UnknownKanji(BaseModel):
    kanji: str = Field(description="The work using unknown kanji")
    hiragana: str = Field(description="The hiragana of the unknown kanji")
    explanation: str = Field(description="The explanation of the word in English")


class AllKanji(BaseModel):
    kanji: str = Field(description="The kanji in the sentence, separated by commas")


class ConversationKanjiResponse(BaseModel):
    unknown_kanji: list[UnknownKanji] = Field(description="The unknown kanji in the response")


class ConversationResponse(BaseModel):
    response: str = Field(description="Your response to the user's message (in Japanese)")
    notes: str = Field(description="Notes to the user about the response (in English)")
