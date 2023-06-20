import json
from typing import AsyncGenerator, List

import sqlalchemy as sa
from pydantic import parse_obj_as
from pydantic.json import pydantic_encoder
from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config import settings


def json_serializer(*args, **kwargs) -> str:
    return json.dumps(*args, default=pydantic_encoder, **kwargs)


engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
    json_serializer=json_serializer,  # TODO: check the performance impact
)

_async_session = async_sessionmaker(engine, expire_on_commit=False, autocommit=False, autoflush=False)


def async_session() -> AsyncSession:
    return _async_session()


POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_k",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)

Base = declarative_base(metadata=metadata)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Return an asynchronous generator that yields a new SQLAlchemy async session object for each iteration.
    Used as a dependency in FastAPI endpoints.

    Yields:
        AsyncSession: A new SQLAlchemy session object.

    """
    async with async_session() as session:
        yield session


# Pydantic SQLAlchemy Type Decorators


class PydanticType(sa.types.TypeDecorator):
    """
    A custom SQLAlchemy type decorator that allows for seamless integration between Pydantic models and SQLAlchemy's JSONB type.

    Args:
        sa.types.TypeDecorator: The base class for custom SQLAlchemy type decorators.

    Attributes:
        impl: The underlying SQLAlchemy type to be used for the column.
        pydantic_type: The Pydantic model to be used for serialization and deserialization.

    Methods:
        load_dialect_impl: Returns the appropriate SQLAlchemy type based on the database dialect.
        process_bind_param: Converts the Pydantic model to a dictionary for storage in the database.
        process_result_value: Converts the dictionary retrieved from the database to a Pydantic model.

    """

    impl = JSONB

    def __init__(self, pydantic_type):
        super().__init__()
        self.pydantic_type = pydantic_type

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(JSONB())

    def process_bind_param(self, value, _):
        return value.dict() if value else None
        # Consider using jsonable_encoder from FastAPI instead of dict()

    def process_result_value(self, value, _):
        return parse_obj_as(self.pydantic_type, value) if value is not None else None


class ListPydanticType(sa.types.TypeDecorator):
    """
    A custom SQLAlchemy type decorator that allows for seamless integration between lists of Pydantic models and SQLAlchemy's JSONB type.

    Args:
        sa.types.TypeDecorator: The base class for custom SQLAlchemy type decorators.

    Attributes:
        impl: The underlying SQLAlchemy type to be used for the column.
        pydantic_type: The Pydantic model to be used for serialization and deserialization.

    Methods:
        load_dialect_impl: Returns the appropriate SQLAlchemy type based on the database dialect.
        process_bind_param: Converts the Pydantic model to a dictionary for storage in the database.
        process_result_value: Converts the dictionary retrieved from the database to a Pydantic model.

    """

    impl = JSONB

    def __init__(self, pydantic_type):
        super().__init__()
        self.pydantic_type = pydantic_type

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(JSONB())

    def process_bind_param(self, value, _):
        if value is None:
            return None
        return [item.dict() for item in value]

    def process_result_value(self, value, _):
        if value is None:
            return None
        return parse_obj_as(List[self.pydantic_type], value)
