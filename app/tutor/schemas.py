from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.tutor.models import ModelName


class TutorCreate(BaseModel):
    name: str
    language: str
    visible: bool = True
    model: Optional[ModelName] = ModelName.GPT3_5_TURBO


class TutorUpdate(BaseModel):
    name: Optional[str]
    visible: Optional[bool]
    language: Optional[str]
    model: Optional[ModelName]


class TutorRead(BaseModel):
    id: UUID
    name: str
    visible: bool
    language: str
    model: ModelName
