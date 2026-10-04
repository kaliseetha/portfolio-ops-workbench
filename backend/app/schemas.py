from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ExceptionCategory(StrEnum):
    POSITION_MISMATCH = "Position mismatch"
    CASH_VARIANCE = "Cash variance"
    UNMATCHED_SECURITY = "Unmatched security"
    STALE_RECORD = "Stale record"


class ExceptionStatus(StrEnum):
    OPEN = "Open"
    INVESTIGATING = "Investigating"
    RESOLVED = "Resolved"
    DISMISSED = "Dismissed"


class ReviewStatus(StrEnum):
    INVESTIGATING = "Investigating"
    RESOLVED = "Resolved"
    DISMISSED = "Dismissed"


class Priority(StrEnum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quantity: str
    value: str
    asOf: str
    source: str


class ActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    previous_status: str | None
    status: str | None
    message: str
    actor: str
    created_at: datetime


class ExceptionSummary(BaseModel):
    id: str
    account: str
    household: str
    category: ExceptionCategory
    description: str
    priority: Priority
    status: ExceptionStatus
    age: str
    value: str


class ExceptionDetail(ExceptionSummary):
    rule: str
    internal: EvidenceResponse
    external: EvidenceResponse
    explanation: str
    checklist: list[str]
    activities: list[ActivityResponse]


class ExceptionListResponse(BaseModel):
    items: list[ExceptionSummary]
    total: int
    limit: int
    offset: int


class StatusUpdateRequest(BaseModel):
    status: ReviewStatus


class HealthResponse(BaseModel):
    status: str
    database: str


class StatusUpdateResponse(BaseModel):
    item: ExceptionDetail
