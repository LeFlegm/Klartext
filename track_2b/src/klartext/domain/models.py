from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

DocumentType = Literal["tax", "health_insurance", "debt_enforcement", "other"]


class SourcedText(BaseModel):
    """A piece of information extracted from the letter, with its verbatim source."""

    value: str
    source_span: str = Field(description="Exact quote from the letter supporting the value")
    verified: bool = False  # set by our validator, never by the model


class Deadline(SourcedText):
    iso_date: date | None = None


class Extraction(BaseModel):
    """What the model returns for one letter."""

    document_type: DocumentType
    sender: SourcedText
    deadline: Deadline | None = None
    actions: list[SourcedText] = []
    consequences: list[SourcedText] = []


class Explanation(BaseModel):
    language: str  # BCP-47 code, e.g. "tr", "fr", "ti"
    text: str


class LetterResult(BaseModel):
    """What the API returns to the frontend for one letter."""

    id: str
    filename: str
    extraction: Extraction
    explanation: Explanation | None = None
    days_left: int | None = None
    unverified_count: int = 0
    model_used: str
    escalated: bool = False
    latency_ms: int