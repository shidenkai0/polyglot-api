import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.models import ChatSession
from app.chat.schemas import Message, MessageRole
from app.tutor.models import Tutor
from app.user.models import User


@pytest.mark.asyncio
async def test_chat_session_creation(async_session: AsyncSession, test_user: User, test_tutor: Tutor):
    """Test creating a new ChatSession object."""
    chat_session = ChatSession(user=test_user, tutor=test_tutor)
    async_session.add(chat_session)
    await async_session.commit()

    assert chat_session.id is not None


@pytest.mark.asyncio
async def test_chat_session_get_response(async_session: AsyncSession, test_chat_session: ChatSession):
    """Test getting a response from an AI tutor"""
    response = await test_chat_session.get_response("How do I use this feature?")
    print(response)
    assert response is not None


@pytest.mark.asyncio
async def test_chat_session_get_conversation_opener(
    async_session: AsyncSession, test_chat_session: ChatSession, capsys
):
    """Test getting a conversation opener from an AI tutor."""
    response = await test_chat_session.get_conversation_opener()
    print(response)
    assert response is not None
