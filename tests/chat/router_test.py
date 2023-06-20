import httpx
import pytest

from app.chat.models import ChatSession
from app.chat.router import CHAT_SESSION_NOT_FOUND


@pytest.mark.asyncio
async def test_get_chat_sessions(test_chat_session: ChatSession, authenticated_client: httpx.AsyncClient):
    """Test getting a list of ChatSession objects by user ID."""
    response = await authenticated_client.get("/chats")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0] == {
        "id": str(test_chat_session.id),
        "user_id": str(test_chat_session.user_id),
        "tutor_id": str(test_chat_session.tutor_id),
        "message_history": [],
    }


@pytest.mark.asyncio
async def test_get_chat_session(test_chat_session: ChatSession, authenticated_client: httpx.AsyncClient):
    """Test getting a ChatSession object."""
    response = await authenticated_client.get(f"/chat/{test_chat_session.id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": str(test_chat_session.id),
        "user_id": str(test_chat_session.user_id),
        "tutor_id": str(test_chat_session.tutor_id),
        "message_history": [],
    }


@pytest.mark.asyncio
async def test_get_chat_session_not_found(authenticated_client: httpx.AsyncClient):
    """Test getting a ChatSession object that does not exist."""
    response = await authenticated_client.get("/chat/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json() == {"detail": CHAT_SESSION_NOT_FOUND.detail}


@pytest.mark.asyncio
async def test_start_chat_session(authenticated_client: httpx.AsyncClient, test_user, test_tutor):
    """Test starting a new chat session."""
    response = await authenticated_client.get(f"/chat?tutor_id={test_tutor.id}")
    assert response.status_code == 200
    chat_session = await ChatSession.get(response.json()["id"])
    assert chat_session.user_id == test_user.id
    assert chat_session.tutor_id == test_tutor.id
    opener = await chat_session.get_conversation_opener()
    assert opener == test_user
    assert response.json() == {
        "id": str(chat_session.id),
        "user_id": str(test_user.id),
        "tutor_id": str(test_tutor.id),
        "message_history": [],
    }


@pytest.mark.asyncio
async def test_start_chat_session_tutor_not_found(authenticated_client: httpx.AsyncClient):
    """Test starting a new chat session with a tutor that does not exist."""
    response = await authenticated_client.get("/chat?tutor_id=00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json() == {"detail": "Tutor not found"}


@pytest.mark.asyncio
async def test_start_chat_session_tutor_not_visible(authenticated_client: httpx.AsyncClient, test_tutor):
    """Test starting a new chat session with a tutor that is not visible."""
    response = await authenticated_client.get(f"/chat?tutor_id={test_tutor.id}")
    assert response.status_code == 404
