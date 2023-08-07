from datetime import datetime
from unittest.mock import patch
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.models import ChatSession, MessageHistoryTooLongError
from app.chat.schemas import MessageWrite, OpenAIMessage, OpenAIMessageRole
from app.tutor.models import Tutor
from app.user.models import User


@pytest.mark.asyncio
async def test_chat_session_create(test_user: User, test_tutor: Tutor):
    """Test creating a new ChatSession object."""
    chat_session = await ChatSession.create(
        user_id=test_user.id,
        tutor_id=test_tutor.id,
        message_history=[],
        max_tokens=20,
        max_messages=10,
    )

    assert chat_session.id is not None


@pytest.mark.asyncio
async def test_chat_session_create_too_long_message_history(test_user: User, test_tutor: Tutor):
    """Test creating a new ChatSession object with a message history that is too long."""
    message_history = [OpenAIMessage(role=OpenAIMessageRole.USER, content="Hello")] * 11
    with pytest.raises(MessageHistoryTooLongError):
        await ChatSession.create(
            user_id=test_user.id,
            tutor_id=test_tutor.id,
            message_history=message_history,
            max_tokens=20,
            max_messages=10,
        )


@pytest.mark.asyncio
async def test_chat_session_get(test_chat_session: ChatSession):
    """Test getting a ChatSession object."""
    chat_session = await ChatSession.get(test_chat_session.id)
    assert chat_session is not None


@pytest.mark.asyncio
async def test_chat_session_get_excludes_soft_deleted(test_chat_session: ChatSession):
    """Test that get doesn't return soft-deleted ChatSession objects."""
    await ChatSession.delete(test_chat_session.id, soft=True)
    chat_session = await ChatSession.get(test_chat_session.id)
    assert chat_session is None


@pytest.mark.asyncio
async def test_chat_session_delete(async_session: AsyncSession, test_chat_session: ChatSession):
    """Test deleting a ChatSession object."""
    await ChatSession.delete(test_chat_session.id, soft=False)
    chat_session = await async_session.get(ChatSession, test_chat_session.id)
    assert chat_session is None


@pytest.mark.asyncio
async def test_chat_session_soft_delete(async_session: AsyncSession, test_chat_session: ChatSession):
    """Test soft deleting a ChatSession object."""
    await ChatSession.delete(test_chat_session.id, soft=True)
    chat_session = await async_session.get(ChatSession, test_chat_session.id)
    assert chat_session is not None
    assert chat_session.is_deleted


@pytest.mark.asyncio
async def test_chat_session_get_not_found():
    """Test getting a ChatSession object that does not exist."""
    chat_session = await ChatSession.get(UUID(int=0))
    assert chat_session is None


@pytest.mark.asyncio
async def test_chat_session_get_by_user_id(test_chat_session: ChatSession):
    """Test getting a list of ChatSession objects by user ID."""
    chat_sessions = await ChatSession.get_by_user_id(test_chat_session.user_id)
    assert chat_sessions is not None
    assert len(chat_sessions) == 1
    assert chat_sessions[0].id == test_chat_session.id
    assert chat_sessions[0].user.id == test_chat_session.user_id  # Test eager loading of user
    assert chat_sessions


@pytest.mark.asyncio
async def test_chat_session_get_by_user_id_excludes_soft_deleted(test_chat_session: ChatSession):
    """Test that get_by_user_id doesn't return soft-deleted ChatSession objects."""
    await ChatSession.delete(test_chat_session.id, soft=True)
    chat_sessions = await ChatSession.get_by_user_id(test_chat_session.user_id)
    assert all(not session.is_deleted for session in chat_sessions)


@pytest.mark.asyncio
async def test_chat_session_get_by_id_user_id(test_chat_session: ChatSession):
    """Test getting a ChatSession object by ID and user ID."""
    chat_session = await ChatSession.get_by_id_user_id(test_chat_session.id, test_chat_session.user_id)
    assert chat_session is not None
    assert chat_session.id == test_chat_session.id


@pytest.mark.asyncio
async def test_chat_session_get_by_id_user_id_excludes_soft_deleted(test_chat_session: ChatSession):
    """Test that get_by_id_user_id doesn't return a soft-deleted ChatSession object."""
    await ChatSession.delete(test_chat_session.id, soft=True)
    chat_session = await ChatSession.get_by_id_user_id(test_chat_session.id, test_chat_session.user_id)
    assert chat_session is None


@pytest.mark.asyncio
async def test_chat_session_get_by_id_user_id_not_found(test_chat_session: ChatSession):
    """Test getting a ChatSession object by ID and user ID that does belong to the ChatSession."""
    chat_session = await ChatSession.get_by_id_user_id(test_chat_session.id, UUID(int=0))
    assert chat_session is None


@pytest.mark.asyncio
@pytest.mark.keep_it_short
async def test_chat_session_get_response(test_chat_session: ChatSession):
    """Test getting a response from an AI tutor."""
    initial_message_history = test_chat_session.message_history
    user_message = MessageWrite(content="Hello")
    with patch('app.chat.models.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime.fromtimestamp(0)
        response = await test_chat_session.get_response(user_message, commit=True)
    assert response is not None
    chat_session = await ChatSession.get(test_chat_session.id)
    assert chat_session is not None
    assert chat_session.message_history == initial_message_history + [
        OpenAIMessage(
            role=OpenAIMessageRole.USER, content=user_message.content, name=test_chat_session.user.name, timestamp_ms=0
        ),
        response,
    ]


@pytest.mark.asyncio
@pytest.mark.keep_it_short
async def test_chat_session_get_response_too_long_message_history(test_chat_session: ChatSession):
    """Test getting a response from an AI tutor with a message history that is too long."""
    test_chat_session.message_history = [
        OpenAIMessage(role=OpenAIMessageRole.USER, content="Hello")
    ] * test_chat_session.max_messages
    with pytest.raises(MessageHistoryTooLongError):
        user_message = MessageWrite(content="Hello")
        await test_chat_session.get_response(user_message)


@pytest.mark.asyncio
@pytest.mark.keep_it_short
async def test_chat_session_get_conversation_opener(empty_test_chat_session: ChatSession):
    """Test getting a conversation opener from an AI tutor."""
    response = await empty_test_chat_session.get_conversation_opener(commit=True)
    assert response is not None
    chat_session = await ChatSession.get(empty_test_chat_session.id)
    assert chat_session is not None
    assert len(chat_session.message_history) == 1
