from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskCreate(BaseModel):
    # extra="forbid": a client sending company_id, status, etc. gets a 422
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    assigned_to: UUID


class TaskStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: TaskStatus


class TaskOut(BaseModel):
    id: UUID
    company_id: UUID
    title: str
    description: str | None
    status: TaskStatus
    assigned_to: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime