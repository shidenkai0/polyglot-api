import uuid
from typing import List, Optional

from sqlalchemy import UUID, ForeignKey, Integer
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, get_session
from app.tutor.models import Tutor
from app.user.models import User
from app.utils import get_chat_response

from .schemas import Message, MessageRole

DEFAULT_MAX_TOKENS = 200
DEFAULT_MAX_MESSAGES = 100


class MessageHistoryTooLongError(Exception):
    """Raised when the message history of a chat session is too long."""

    pass


class ChatSession(Base):
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
    user: Mapped[User] = relationship("User", lazy="joined", back_populates="chat_sessions")
    message_history: Mapped[List[Message]] = mapped_column(MutableList.as_mutable(JSONB), nullable=False, default=[])
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
        user_id: uuid.UUID,
        tutor_id: uuid.UUID,
        max_tokens: Optional[int] = DEFAULT_MAX_TOKENS,
        max_messages: Optional[int] = DEFAULT_MAX_MESSAGES,
        message_history: Optional[List[Message]] = [],
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
        async for session in get_session():
            chat_session = cls(
                user_id=user_id,
                tutor_id=tutor_id,
                max_tokens=max_tokens,
                max_messages=max_messages,
                message_history=message_history,
            )
            session.add(chat_session)
            if commit:
                await session.commit()
                await session.refresh(chat_session)
            return chat_session

    async def get_response(self, user_input: str, commit: bool = False) -> str:
        """
        Get a response from the AI tutor to the user's message.

        Args:
            user_input (str): The user's input.

        Returns:
            str: The tutor's response to the user's message.
        """
        system_message = Message(
            role=MessageRole.SYSTEM, content=self.tutor.get_system_prompt(student_name=self.user.first_name)
        )

        user_message = Message(role=MessageRole.USER, content=user_input, name=self.user.first_name)
        messages = [system_message] + self.message_history + [user_message]
        if len(messages) > self.max_messages:
            raise MessageHistoryTooLongError(f"Message history is too long. Max messages is {self.max_messages}.")
        ai_message = await get_chat_response(
            model=self.tutor.model, messages=messages, max_tokens=self.max_tokens, temperature=0.2
        )

        self.message_history.extend([user_message, ai_message])

        return ai_message.content

    async def get_conversation_opener(self) -> Optional[str]:
        """
        Get a conversation opener from the AI tutor.

        Returns:
            Optional[str]: The tutor's conversation opener.
        """
        system_message = Message(
            role=MessageRole.SYSTEM, content=self.tutor.get_system_prompt(student_name=self.user.first_name)
        )

        ai_message = await get_chat_response(
            model=self.tutor.model, messages=[system_message], max_tokens=DEFAULT_MAX_TOKENS, temperature=0.2
        )

        self.message_history.append(ai_message)
        return ai_message.content
