from enum import StrEnum
from typing import List, Optional
from uuid import UUID

from pydantic import UUID4, BaseModel

from app.tutor.schemas import TutorRead


class OpenAIMessageRole(StrEnum):
    """Role of a message in an OpenAI chat session."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class OpenAIMessage(BaseModel):
    """
    A chat message as defined in the OpenAI API (https://platform.openai.com/docs/api-reference/chat).

    Attributes:
    -----------
    role : MessageRole
        The role of the message in the chat session.
    content : Optional[str]
        The content of the message.
    name : Optional[str]
        The name of the message.
    function_call : Optional[dict]
        The function call of the message.
    """

    class Config:
        use_enum_values = True
        # Omit None values when getting dict representation of the object
        # https://pydantic-docs.helpmanual.io/usage/exporting_models/#exclude-none-values

    role: OpenAIMessageRole
    content: str = ""
    name: Optional[str] = None
    uuid: Optional[str] = None
    timestamp_ms: Optional[int] = None
    function_call: Optional[dict] = None


class MessageRole(StrEnum):
    """Role of a message in a language tutoring session."""

    TUTOR = "tutor"
    USER = "user"


class MessageBase(BaseModel):
    content: str = ""


internal_to_external_role = {
    OpenAIMessageRole.ASSISTANT: MessageRole.TUTOR,
    OpenAIMessageRole.USER: MessageRole.USER,
}


class MessageRead(MessageBase):
    role: MessageRole
    timestamp_ms: int
    uuid: UUID4

    class Config:
        use_enum_values = True

    @classmethod
    def from_openai_message(cls, openai_message: OpenAIMessage) -> "MessageRead":
        """
        Convert an OpenAI message to a message for the language tutoring session.

        Args:
            openai_message (OpenAIMessage): The OpenAI message.

        Returns:
            MessageRead: The message for the language tutoring session.
        """
        return cls(
            role=internal_to_external_role[openai_message.role],
            content=openai_message.content,
            uuid=openai_message.uuid,
            timestamp_ms=openai_message.timestamp_ms,
        )


class MessageWrite(MessageBase):
    """
    A message as written by the user in a language tutoring session.

    Attributes:
    -----------
    content : str
        The content of the message.
    """

    pass


class ChatSessionBase(BaseModel):
    user_id: UUID
    tutor_id: UUID


class ChatSessionRead(ChatSessionBase):
    id: UUID
    message_history: List[MessageRead]
    tutor: TutorRead


class ChatSessionCreate(ChatSessionBase):
    pass
