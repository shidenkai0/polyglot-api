from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.models import ChatSession, MessageHistoryTooLongError
from app.chat.schemas import (
    ChatSessionCreate,
    MessageWrite,
    OpenAIMessage,
    OpenAIMessageRole,
)
from app.tutor.models import Tutor
from app.user.models import User


@pytest.mark.asyncio
async def test_chat_session_create(async_session: AsyncSession, test_user: User, test_tutor: Tutor):
    """Test creating a new ChatSession object."""
    message_history = []
    chat_session = await ChatSession.create(
        user_id=test_user.id,
        tutor_id=test_tutor.id,
        message_history=message_history,
        max_tokens=20,
        max_messages=10,
    )

    assert chat_session.id is not None


@pytest.mark.asyncio
async def test_chat_session_create_too_long_message_history(
    async_session: AsyncSession, test_user: User, test_tutor: Tutor
):
    """Test creating a new ChatSession object with a message history that is too long."""
    message_history = [OpenAIMessage(role=OpenAIMessageRole.USER, text="Hello")] * 11
    with pytest.raises(MessageHistoryTooLongError):
        await ChatSession.create(
            user_id=test_user.id,
            tutor_id=test_tutor.id,
            message_history=message_history,
            max_tokens=20,
            max_messages=10,
        )


@pytest.mark.asyncio
async def test_chat_session_get(async_session: AsyncSession, test_chat_session: ChatSession):
    """Test getting a ChatSession object."""
    chat_session = await ChatSession.get(test_chat_session.id)
    assert chat_session is not None


@pytest.mark.asyncio
async def test_chat_session_get_not_found(async_session: AsyncSession):
    """Test getting a ChatSession object that does not exist."""
    chat_session = await ChatSession.get(UUID(int=0))
    assert chat_session is None


@pytest.mark.asyncio
async def test_chat_session_get_by_user_id(async_session: AsyncSession, test_chat_session: ChatSession):
    """Test getting a list of ChatSession objects by user ID."""
    chat_sessions = await ChatSession.get_by_user_id(test_chat_session.user_id)
    assert chat_sessions is not None
    assert len(chat_sessions) == 1
    assert chat_sessions[0].id == test_chat_session.id
    assert chat_sessions[0].user.id == test_chat_session.user_id  # Test eager loading of user
    assert chat_sessions


@pytest.mark.asyncio
async def test_chat_session_get_by_id_user_id(async_session: AsyncSession, test_chat_session: ChatSession):
    """Test getting a ChatSession object by ID and user ID."""
    chat_session = await ChatSession.get_by_id_user_id(test_chat_session.id, test_chat_session.user_id)
    assert chat_session is not None
    assert chat_session.id == test_chat_session.id


@pytest.mark.asyncio
async def test_chat_session_get_by_id_user_id_not_found(async_session: AsyncSession, test_chat_session: ChatSession):
    """Test getting a ChatSession object by ID and user ID that does belong to the ChatSession."""
    chat_session = await ChatSession.get_by_id_user_id(test_chat_session.id, UUID(int=0))
    assert chat_session is None


@pytest.mark.asyncio
async def test_chat_session_get_response(async_session: AsyncSession, test_chat_session: ChatSession):
    """Test getting a response from an AI tutor."""
    user_message = MessageWrite(content="Hello")
    response = await test_chat_session.get_response(user_message, commit=True)
    assert response is not None
    assert test_chat_session.message_history == [
        OpenAIMessage(
            role=OpenAIMessageRole.USER, content=user_message.content, name=test_chat_session.user.first_name
        ),
        OpenAIMessage(role=OpenAIMessageRole.ASSISTANT, content=response),
    ]


@pytest.mark.asyncio
async def test_chat_session_get_response_too_long_message_history(
    async_session: AsyncSession, test_chat_session: ChatSession
):
    """Test getting a response from an AI tutor with a message history that is too long."""
    test_chat_session.message_history = [
        OpenAIMessage(role=OpenAIMessageRole.USER, content="Hello")
    ] * test_chat_session.max_messages
    with pytest.raises(MessageHistoryTooLongError):
        user_message = MessageWrite(content="Hello")
        await test_chat_session.get_response(user_message)


@pytest.mark.asyncio
async def test_chat_session_get_conversation_opener(async_session: AsyncSession, test_chat_session: ChatSession):
    """Test getting a conversation opener from an AI tutor."""
    response = await test_chat_session.get_conversation_opener(commit=True)
    assert response is not None