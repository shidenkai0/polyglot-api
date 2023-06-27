import uuid
from enum import StrEnum
from typing import List, Optional

from sqlalchemy import Boolean, String, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, async_session

SYSTEM_TEMPLATE_STRING = """You are a friendly language tutor named {name} who can help a student named {student_name} improve their conversational skills in {language}.
The student is a non-native speaker who is learning {language} as a second language.
You open the conversation by greeting the student and introducing yourself, then talk about a variety of topics and ask conversational questions to keep the conversation going.
You hold conversations with the student about various topics, to help them improve their conversational skills.
"""


class ModelName(StrEnum):
    GPT4 = "gpt-4-0613"
    GPT3_5_TURBO = "gpt-3.5-turbo-0613"


class Tutor(Base, TimestampMixin):
    """
    Represents an AI language tutor.

    Attributes:
        id (uuid.UUID): The unique identifier for the tutor.
        display_name (str): The name of the tutor as displayed to users.
        visible (bool): Whether the tutor is visible to users.
        system_prompt (str): The system prompt for the tutor.
        language (str): The language of the tutor.
    """

    __tablename__ = "tutor"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False, default="")
    visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    language: Mapped[str] = mapped_column(String, nullable=False, default="english")
    system_prompt: Mapped[str] = mapped_column(String, nullable=False, default=SYSTEM_TEMPLATE_STRING)
    personality_prompt: Mapped[str] = mapped_column(String, nullable=False, default="")
    model: Mapped[ModelName] = mapped_column(String, nullable=False, default=ModelName.GPT3_5_TURBO)

    def __repr__(self) -> str:
        """
        Return a string representation of the Tutor object.

        Returns:
            str: A string representation of the Tutor object.
        """
        return f"<Tutor {self.id} name={self.name} visible={self.visible} language={self.language}>"

    @classmethod
    async def create(
        cls,
        name: str,
        language: str,
        visible: bool = True,
        model: ModelName = ModelName.GPT3_5_TURBO,
        commit: bool = True,
    ) -> "Tutor":
        """
        Create a new Tutor object.

        Args:
            name (str): The name of the tutor.
            language (str): The language of the tutor.
            visible (bool): Whether the tutor is visible to users.
            model (ModelName): The model to use for the tutor.
            commit (bool): Whether to commit the new Tutor object to the database.

        Returns:
            Tutor: The newly created Tutor object.
        """
        tutor = cls(name=name, language=language, visible=visible, model=model)
        async with async_session() as session:
            if commit:
                session.add(tutor)
                await session.commit()
                await session.refresh(tutor)
            return tutor

    async def update(self, name: Optional[str] = None, language: Optional[str] = None, visible: Optional[bool] = None):
        """
        Update the Tutor object.

        Args:
            name (Optional[str]): The name of the tutor.
            language (Optional[str]): The language of the tutor.
            visible (Optional[bool]): Whether the tutor is visible to users.
        """
        if name:
            self.name = name
        if language:
            self.language = language
        if visible is not None:
            self.visible = visible

        async with async_session() as session:
            session.add(self)
            await session.commit()
            await session.refresh(self)

    @classmethod
    async def get(cls, id: uuid.UUID) -> "Tutor":
        """
        Get a Tutor object by id.

        Args:
            id (uuid.UUID): The id of the Tutor object.

        Returns:
            Tutor: The Tutor object.
        """
        async with async_session() as session:
            tutor = await session.get(cls, id)
            return tutor

    @classmethod
    async def delete(cls, chat_session_id: uuid.UUID) -> None:
        """
        Delete a Tutor object by id.

        Args:
            id (uuid.UUID): The id of the Tutor object.
        """
        async with async_session() as session:
            tutor = await session.get(cls, chat_session_id)
            await session.delete(tutor)
            await session.commit()

    @classmethod
    async def get_visible(cls) -> List["Tutor"]:
        """
        Get a list of visible Tutor objects.

        Returns:
            List[Tutor]: A list of visible Tutor objects.
        """
        query = select(cls).where(cls.visible == True)
        async with async_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_all(cls) -> List["Tutor"]:
        """
        Get a list of all Tutor objects.

        Returns:
            List[Tutor]: A list of all Tutor objects.
        """
        query = select(cls)
        async with async_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    def get_system_prompt(self, student_name: str) -> str:
        """
        Get the system prompt for the tutor.

        Args:
            student_name (str): The name of the student.

        Returns:
            str: The system prompt for the tutor, with placeholders for the tutor's name, language, and the student's name.
        """

        system_prompt = self.system_prompt + self.personality_prompt

        return system_prompt.format(
            name=self.name,
            language=self.language,
            student_name=student_name,
        )
