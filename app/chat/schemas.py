import json
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class MessageRole(Enum):
    """
    Role of a message in an OpenAI chat session.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class Message(BaseModel):
    """
    A chat message as defined in the OpenAI API (https://platform.openai.com/docs/api-reference/chat)
    """

    class Config:
        use_enum_values = True
        # Omit None values when getting dict representation of the object
        # https://pydantic-docs.helpmanual.io/usage/exporting_models/#exclude-none-values

    role: MessageRole
    content: Optional[str] = None
    name: Optional[str] = None
    function_call: Optional[dict] = None
