from enum import StrEnum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.tutor.models import ModelName


class PublicModelName(StrEnum):
    """Public model name."""

    GPT4 = "gpt4"
    GPT3_5_TURBO = "gpt35"


_public_to_internal_model = {
    PublicModelName.GPT4: ModelName.GPT4,
    PublicModelName.GPT3_5_TURBO: ModelName.GPT3_5_TURBO,
}

_internal_to_public_model = {v: k for k, v in _public_to_internal_model.items()}


def public_to_internal_model_name(public_model_name: PublicModelName) -> ModelName:
    """Convert a public model name to an internal model name."""
    return _public_to_internal_model[public_model_name]


def internal_to_public_model_name(internal_model_name: ModelName) -> PublicModelName:
    """Convert an internal model name to a public model name."""
    return _internal_to_public_model[internal_model_name]


class TutorCreate(BaseModel):
    """Tutor create schema."""

    name: str
    language: str
    visible: bool = True
    model: PublicModelName = PublicModelName.GPT3_5_TURBO
    personality_prompt: str = ""


class TutorUpdate(BaseModel):
    """Tutor update schema."""

    name: Optional[str]
    visible: Optional[bool]
    language: Optional[str]
    model: Optional[PublicModelName]
    personality_prompt: str = ""


class TutorRead(BaseModel):
    """Tutor read schema."""

    id: UUID
    name: str
    visible: bool
    language: str
    model: PublicModelName
