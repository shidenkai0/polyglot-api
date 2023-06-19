import uuid
from enum import Enum

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, async_session

SYSTEM_TEMPLATE_STRING = """You are a friendly language tutor named {name} who can help a student named {student_name} improve their conversational skills in {language}.
The student is a non-native speaker who is learning {language} as a second language.
You open the conversation by greeting the student and introducing yourself, then talk about a variety of topics and ask conversational questions to keep the conversation going.
You hold conversations with the student about various topics, to help them improve their conversational skills.
"""


class ModelName(str, Enum):
    GPT4 = "gpt-4-0613"
    GPT3_5_TURBO = "gpt-3.5-turbo-0613"


class Tutor(Base):
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
        cls, name: str, language: str, visible: bool = True, model: ModelName = ModelName.GPT3_5_TURBO
    ) -> "Tutor":
        """
        Create a new Tutor object.

        Args:
            name (str): The name of the tutor.
            language (str): The language of the tutor.
            visible (bool): Whether the tutor is visible to users.

        Returns:
            Tutor: The newly created Tutor object.
        """
        async with async_session() as session:
            tutor = cls(name=name, language=language, visible=visible, model=model)
            session.add(tutor)
            await session.commit()
            await session.refresh(tutor)
            return tutor

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
