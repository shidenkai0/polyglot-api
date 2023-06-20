from unittest.mock import patch

import pytest_asyncio

from app.chat.models import ChatSession
from app.tutor.models import Tutor
from app.user.models import User


@pytest_asyncio.fixture
async def test_chat_session(test_user: User, test_tutor: Tutor, async_session) -> ChatSession:
    """Create a new ChatSession object for testing."""
    message_history = []
    chat_session = await ChatSession.create(
        user_id=test_user.id,
        tutor_id=test_tutor.id,
        message_history=message_history,
        max_tokens=10,
        max_messages=10,
    )
    yield chat_session
