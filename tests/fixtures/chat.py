import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.models import ChatSession
from app.tutor.models import Tutor
from app.user.models import User


@pytest_asyncio.fixture
async def test_chat_session(async_session: AsyncSession, test_user: User, test_tutor: Tutor) -> ChatSession:
    """Create a new ChatSession object for testing."""
    message_history = []
    chat_session = ChatSession(
        user_id=test_user.id, tutor_id=test_tutor.id, message_history=message_history, max_tokens=20, max_messages=10
    )
    async_session.add(chat_session)
    await async_session.commit()
    await async_session.refresh(chat_session)
    yield chat_session
