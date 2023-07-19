from uuid import UUID

from pydantic import BaseModel, EmailStr, validator

from app.config import settings

supported_languages = settings.SUPPORTED_LANGUAGES


class UserCreate(BaseModel):
    email: EmailStr
    firebase_id_token: str
    name: str
    language: str

    @validator("language")
    def validate_language(cls, v):
        """
        Validates if the language is supported by the application.

        Args:
            cls: The class that contains the validator.
            v: The value of the language field.

        Raises:
            ValueError: If the language is not supported by the application.

        Returns:
            The validated language value.
        """
        if v not in supported_languages:
            raise ValueError(f"Language {v} is not supported")
        return v


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    firebase_uid: str
    name: str
    language: str
