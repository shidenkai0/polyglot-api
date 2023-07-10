from enum import StrEnum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.tutor.models import ModelName


class TutorCreate(BaseModel):
    name: str
    language: str
    visible: bool = True
    model: ModelName = ModelName.GPT3_5_TURBO
    personality_prompt: str = ""


class TutorUpdate(BaseModel):
    name: Optional[str]
    visible: Optional[bool]
    language: Optional[str]
    model: Optional[ModelName]
    personality_prompt: str = ""


class TutorRead(BaseModel):
    id: UUID
    name: str
    visible: bool
    language: str
    model: ModelName
