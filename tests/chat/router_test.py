import httpx
import pytest

from app.chat.models import ChatSession
from app.chat.router import CHAT_SESSION_NOT_FOUND
from app.chat.schemas import MessageRole


@pytest.mark.asyncio
async def test_get_chat_sessions(test_chat_session: ChatSession, authenticated_client_user: httpx.AsyncClient):
    """Test getting a list of ChatSession objects by user ID."""
    response = await authenticated_client_user.get("/chats")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0] == {
        "id": str(test_chat_session.id),
        "user_id": str(test_chat_session.user_id),
        "tutor_id": str(test_chat_session.tutor_id),
        "message_history": [{'content': 'Hello', 'role': MessageRole.TUTOR}],
    }


@pytest.mark.asyncio
async def test_get_chat_session(test_chat_session: ChatSession, authenticated_client_user: httpx.AsyncClient):
    """Test getting a ChatSession object."""
    response = await authenticated_client_user.get(f"/chat/{test_chat_session.id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": str(test_chat_session.id),
        "user_id": str(test_chat_session.user_id),
        "tutor_id": str(test_chat_session.tutor_id),
        "message_history": [{'content': 'Hello', 'role': MessageRole.TUTOR}],
    }


@pytest.mark.asyncio
async def test_get_chat_session_not_found(authenticated_client_user: httpx.AsyncClient):
    """Test getting a ChatSession object that does not exist."""
    response = await authenticated_client_user.get("/chat/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json() == {"detail": CHAT_SESSION_NOT_FOUND.detail}


@pytest.mark.asyncio
@pytest.mark.keep_it_short
async def test_start_chat_session(authenticated_client_user: httpx.AsyncClient, test_user, test_tutor):
    """Test starting a new chat session."""
    response = await authenticated_client_user.get(f"/chat?tutor_id={test_tutor.id}")
    assert response.status_code == 200
    chat_session = await ChatSession.get(response.json()["id"])
    assert chat_session is not None
    assert response.json().keys() == {"id", "user_id", "tutor_id", "message_history"}
    assert response.json()["user_id"] == str(test_user.id)
    assert response.json()["tutor_id"] == str(test_tutor.id)
    assert len(response.json()["message_history"]) == 1
    assert response.json()["message_history"][0]["role"] == MessageRole.TUTOR
    assert response.json()["message_history"][0]["content"] == chat_session.message_history[0].content


@pytest.mark.asyncio
async def test_start_chat_session_tutor_not_found(authenticated_client_user: httpx.AsyncClient):
    """Test starting a new chat session with a tutor that does not exist."""
    response = await authenticated_client_user.get("/chat?tutor_id=00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json() == {"detail": "Tutor not found"}


@pytest.mark.asyncio
async def test_start_chat_session_tutor_not_visible(authenticated_client_user: httpx.AsyncClient, test_tutor):
    """Test starting a new chat session with a tutor that is not visible."""
    await test_tutor.update(visible=False)
    response = await authenticated_client_user.get(f"/chat?tutor_id={test_tutor.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.keep_it_short
async def test_post_chat_message(test_chat_session: ChatSession, authenticated_client_user: httpx.AsyncClient):
    """Test posting a new chat message."""
    initial_message_history_length = len(test_chat_session.message_history)
    response = await authenticated_client_user.post(
        f"/chat/{test_chat_session.id}",
        json={"content": "Hello, world!"},
    )
    assert response.status_code == 200
    chat_session = await ChatSession.get(test_chat_session.id)
    assert chat_session is not None
    assert len(chat_session.message_history) == initial_message_history_length + 2  # user message + tutor response
    assert response.json()["role"] == MessageRole.TUTOR
    assert response.json()["content"] == chat_session.message_history[-1].content


@pytest.mark.asyncio
async def test_delete_chat_session(test_chat_session: ChatSession, authenticated_client_user: httpx.AsyncClient):
    """Test deleting a chat session."""
    response = await authenticated_client_user.delete(f"/chat/{test_chat_session.id}")
    assert response.status_code == 204
    chat_session = await ChatSession.get(test_chat_session.id)
    assert chat_session is None


@pytest.mark.asyncio
async def test_delete_chat_session_not_found(authenticated_client_user: httpx.AsyncClient):
    """Test deleting a chat session that does not exist."""
    response = await authenticated_client_user.delete("/chat/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json() == {"detail": CHAT_SESSION_NOT_FOUND.detail}
