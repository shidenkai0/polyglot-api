from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class OpenAIMessageRole(str, Enum):
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
    content: Optional[str] = None
    name: Optional[str] = None
    function_call: Optional[dict] = None


class MessageRole(Enum):
    """Role of a message in a language tutoring session."""

    TUTOR = "tutor"
    USER = "user"


class MessageBase(BaseModel):
    content: str = ""


class MessageRead(MessageBase):
    """
    A message as returned by the Polyglot API.

    Attributes:
    -----------
    role : ReadMessageRole
        The role of the message in the chat session.
    content : str
        The content of the message.
    """

    role: MessageRole

    class Config:
        use_enum_values = True


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

    class Config:
        orm_mode = True


class ChatSessionCreate(ChatSessionBase):
    pass
