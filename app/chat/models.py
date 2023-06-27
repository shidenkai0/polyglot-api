import uuid
from typing import List, Optional

from sqlalchemy import UUID, ForeignKey, Integer, select, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.chat.utils import get_chat_response
from app.database import (
    Base,
    DeleteMixin,
    ListPydanticType,
    TimestampMixin,
    async_session,
)
from app.tutor.models import Tutor
from app.user.models import User

from .schemas import MessageWrite, OpenAIMessage, OpenAIMessageRole

DEFAULT_MAX_TOKENS = 100
DEFAULT_MAX_MESSAGES = 100


class MessageHistoryTooLongError(Exception):
    """Raised when the message history of a chat session is too long."""

    pass


class ChatSession(Base, TimestampMixin, DeleteMixin):
    """
    Represents a chat session between a user and an AI tutor.

    Attributes:
        id (uuid.UUID): The unique identifier for the chat session.
        user_id (uuid.UUID): The unique identifier for the user associated with the chat session.
        user (User): The user associated with the chat session.
        message_history (list): The list of messages exchanged during the chat session.
        tutor_id (uuid.UUID): The unique identifier for the tutor associated with the chat session.
        tutor (Tutor): The tutor associated with the chat session.
    """

    __tablename__ = "chat_session"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(User.id), nullable=False)
    user: Mapped[User] = relationship("User", lazy="joined")
    message_history: Mapped[List[OpenAIMessage]] = mapped_column(
        ListPydanticType(OpenAIMessage), nullable=False, server_default=text("'[]'::jsonb"), default=[]
    )
    max_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=DEFAULT_MAX_TOKENS)
    max_messages: Mapped[int] = mapped_column(Integer, nullable=False, default=DEFAULT_MAX_MESSAGES)
    tutor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tutor.id"), nullable=False)
    tutor: Mapped[Tutor] = relationship("Tutor", lazy="joined")

    def __repr__(self) -> str:
        """
        Return a string representation of the ChatSession object.

        Returns:
            str: A string representation of the ChatSession object.
        """
        return f"<ChatSession {self.id} user_id={self.user} tutor_id={self.tutor_id}> message_history={self.message_history}>"

    @classmethod
    async def create(
        cls,
        user_id: Optional[uuid.UUID] = None,
        tutor_id: Optional[uuid.UUID] = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        max_messages: int = DEFAULT_MAX_MESSAGES,
        message_history: List[OpenAIMessage] = [],
        commit: bool = True,
    ) -> "ChatSession":
        """
        Create a new ChatSession object.

        Args:
            user_id (uuid.UUID): The unique identifier for the user associated with the chat session.
            tutor_id (uuid.UUID): The unique identifier for the tutor associated with the chat session.
            max_tokens (Optional[int], optional): The maximum number of tokens to generate for each response. Defaults to DEFAULT_MAX_TOKENS.
            max_messages (Optional[int], optional): The maximum number of messages to store in the chat history. Defaults to DEFAULT_MAX_MESSAGES.
            message_history (Optional[List[Message]], optional): The initial message history for the chat session. Defaults to an empty list.
            commit (bool, optional): Whether to commit the new chat session to the database. Defaults to True.

        Returns:
            ChatSession: The newly created ChatSession object.
        """

        if len(message_history) > max_messages:
            raise MessageHistoryTooLongError(f"Message history is too long. Max messages is {max_messages}.")
        chat_session = cls(
            user_id=user_id,
            tutor_id=tutor_id,
            max_tokens=max_tokens,
            max_messages=max_messages,
            message_history=message_history,
        )
        async with async_session() as session:
            if commit:
                session.add(chat_session)
                await session.commit()
                await session.refresh(chat_session)
            return chat_session

    @classmethod
    async def get(cls, chat_session_id: uuid.UUID) -> Optional["ChatSession"]:
        """
        Get a chat session by its unique identifier.

        Args:
            chat_session_id (uuid.UUID): The unique identifier for the chat session.

        Returns:
            ChatSession: The chat session with the given unique identifier.

        Raises:
            ChatSessionNotFoundError: Raised if no chat session with the given unique identifier exists.
        """
        query = cls.default_query().where(cls.id == chat_session_id)
        async with async_session() as session:
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def get_by_user_id(cls, user_id: uuid.UUID) -> List["ChatSession"]:
        """
        Get chat sessions by the user's unique identifier.
        """
        query = cls.default_query().where(cls.user_id == user_id)
        async with async_session() as session:
            result = await session.execute(query)
            return result.scalars().unique().all()  # TODO: check how this performs over time

    @classmethod
    async def get_by_id_user_id(cls, chat_session_id: uuid.UUID, user_id: uuid.UUID) -> Optional["ChatSession"]:
        """
        Get a chat session by its unique identifier and the user's unique identifier.

        Args:
            chat_session_id (uuid.UUID): The unique identifier for the chat session.
            user_id (uuid.UUID): The unique identifier for the user.

        Returns:
            ChatSession: The chat session with the given unique identifier and user's unique identifier.

        Raises:
            ChatSessionNotFoundError: Raised if no chat session with the given unique identifier and user's unique identifier exists.
        """
        query = cls.default_query().where(cls.id == chat_session_id, cls.user_id == user_id)
        async with async_session() as session:
            result = await session.execute(query)
            return result.scalars().first()

    async def get_response(self, message: MessageWrite, commit: bool = False) -> str:
        """
        Get a response from the AI tutor to the user's message.

        Args:
            message (MessageWrite): The user's message.
            commit (bool, optional): Whether to commit the new message to the database. Defaults to False.

        Returns:
            str: The tutor's response to the user's message.
        """
        system_message = OpenAIMessage(
            role=OpenAIMessageRole.SYSTEM, content=self.tutor.get_system_prompt(student_name=self.user.first_name)
        )

        user_message = OpenAIMessage(role=OpenAIMessageRole.USER, content=message.content, name=self.user.first_name)
        messages = [system_message] + self.message_history + [user_message]
        if len(messages) > self.max_messages:
            raise MessageHistoryTooLongError(f"Message history is too long. Max messages is {self.max_messages}.")
        ai_message = await get_chat_response(
            model=self.tutor.model, messages=messages, max_tokens=self.max_tokens, temperature=0.2
        )

        self.message_history = self.message_history + [user_message, ai_message]  # Always use copy-on-write
        if commit:
            async with async_session() as session:
                session.add(self)
                await session.commit()
        return ai_message.content

    async def get_conversation_opener(self, commit: bool = False) -> Optional[str]:
        """
        Get a conversation opener from the AI tutor.

        Args:
            commit (bool, optional): Whether to commit the new message to the database. Defaults to False.

        Returns:
            Optional[str]: The tutor's conversation opener.
        """
        system_message = OpenAIMessage(
            role=OpenAIMessageRole.SYSTEM, content=self.tutor.get_system_prompt(student_name=self.user.first_name)
        )

        ai_message = await get_chat_response(
            model=self.tutor.model, messages=[system_message], max_tokens=DEFAULT_MAX_TOKENS, temperature=0.2
        )
        self.message_history = self.message_history + [ai_message]  # Always use copy-on-write
        if commit:
            async with async_session() as session:
                session.add(self)
                await session.commit()
        return ai_message.content
