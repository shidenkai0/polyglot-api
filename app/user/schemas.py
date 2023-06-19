import uuid
from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    first_name: str
    last_name: str
    locale: str


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    last_name: str
    locale: Optional[str] = "en_US"


class UserUpdate(schemas.BaseUserUpdate):
    first_name: Optional[str]
    last_name: Optional[str]
    locale: Optional[str]
