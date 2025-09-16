from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: int
    profile_image: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    name: str
    progress: int = Field(..., ge=0, le=100)
    description: Optional[str] = None


class TaskResponse(TaskBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskEventBase(BaseModel):
    task_name: str = Field(..., min_length=1, max_length=120)
    progress: int = Field(..., ge=0, le=100)
    note: Optional[str] = Field(None, max_length=255)
    source: Optional[str] = Field(None, max_length=120)


class TaskEventCreate(TaskEventBase):
    pass


class TaskEventResponse(BaseModel):
    id: int
    task_id: int
    task_name: str
    progress: int
    source: str
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ProgressReport(BaseModel):
    tasks: List[TaskResponse]
    events: List[TaskEventResponse]
    overall_progress: float
