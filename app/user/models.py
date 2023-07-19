import uuid
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, async_session


class User(Base, TimestampMixin):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    firebase_uid: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    language: Mapped[str] = mapped_column(String(5), nullable=False, default="en")
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<User {self.id} {self.firebase_uid} {self.email}>"

    @classmethod
    async def create(
        cls,
        email: str,
        firebase_uid: str,
        name: str,
        language: str,
        is_superuser: bool,
        commit: bool = True,
    ) -> "User":
        user = cls(
            email=email,
            firebase_uid=firebase_uid,
            name=name,
            language=language,
            is_superuser=is_superuser,
        )
        if commit:
            async with async_session() as session:
                session.add(user)
                await session.commit()
                await session.refresh(user)
        return user

    @classmethod
    async def get_by_firebase_uid(cls, firebase_uid: str) -> Optional["User"]:
        query = sa.select(cls).where(cls.firebase_uid == firebase_uid)
        async with async_session() as session:
            result = await session.execute(query)
            return result.scalars().first()
