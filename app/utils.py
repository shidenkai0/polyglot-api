from typing import List

from openai import ChatCompletion

from app.chat.schemas import OpenAIMessage


async def get_chat_response(model: str, messages: List[OpenAIMessage], **kwargs) -> OpenAIMessage:
    """
    Send a list of messages to the OpenAI Chat Completion API and return the response.

    Args:
        model (str): The ID of the OpenAI model to use for generating the response.
        messages (List[Message]): A list of messages to send to the chatbot API.
        **kwargs: Additional keyword arguments to pass to the OpenAI API.

    Returns:
        Message: The response message from the Chat Completion API.
    """
    message_dicts = [message.dict(exclude_none=True) for message in messages]
    response = await ChatCompletion.acreate(
        model=model,
        messages=message_dicts,
        **kwargs,
    )
    ai_message = OpenAIMessage.parse_obj(response.choices[0].message)
    return ai_message