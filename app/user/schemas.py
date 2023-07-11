from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    firebase_id_token: str
    first_name: str
    last_name: str
    locale: str


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    firebase_uid: str
    first_name: str
    last_name: str
    locale: str
