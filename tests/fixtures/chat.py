from typing import AsyncGenerator
from unittest.mock import patch

import pytest_asyncio

from app.chat.models import ChatSession
from app.chat.schemas import OpenAIMessage, OpenAIMessageRole
from app.chat.utils import get_chat_response
from app.tutor.models import Tutor
from app.user.models import User


@pytest_asyncio.fixture
async def test_chat_session(
    test_user: User,
    test_tutor: Tutor,
) -> AsyncGenerator[ChatSession, None]:
    """Create a new ChatSession object for testing."""

    chat_session = await ChatSession.create(
        user_id=test_user.id,
        tutor_id=test_tutor.id,
        message_history=[
            OpenAIMessage(
                role=OpenAIMessageRole.ASSISTANT,
                content="Hello",
                timestamp_ms=0,
                uuid='11111111-1111-4111-8111-111111111111',
            )
        ],
        max_tokens=10,
        max_messages=10,
    )
    yield chat_session


@pytest_asyncio.fixture
async def empty_test_chat_session(
    test_user: User,
    test_tutor: Tutor,
) -> AsyncGenerator[ChatSession, None]:
    """Create a new ChatSession object with an empty history for testing."""

    chat_session = await ChatSession.create(
        user_id=test_user.id,
        tutor_id=test_tutor.id,
        message_history=[],
        max_tokens=10,
        max_messages=10,
    )
    yield chat_session


@pytest_asyncio.fixture(autouse=True)
async def keep_it_short(request):
    if 'keep_it_short' in request.keywords:
        original_get_chat_response = get_chat_response

        async def side_effect(*args, **kwargs):
            # Modify kwargs here
            kwargs['max_tokens'] = 10
            # Then call the original function
            return await original_get_chat_response(*args, **kwargs)

        mock_get_chat_response = patch('app.chat.models.get_chat_response', new=side_effect)

        with mock_get_chat_response:
            yield
    else:
        yield
