from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.models import ChatSession
from app.chat.schemas import ChatSessionRead, MessageRead, MessageRole, MessageWrite
from app.database import get_session
from app.tutor.models import Tutor
from app.user.auth import authenticate_user
from app.user.models import User

router = APIRouter(
    responses={404: {"description": "Not found"}},
    tags=["chat"],
)

CHAT_SESSION_NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")

ActiveVerifiedUser = Annotated[User, Depends(authenticate_user)]


@router.get("/chats")
async def get_chat_sessions(user: ActiveVerifiedUser) -> List[ChatSessionRead]:
    """
    Get all chat sessions for the current user.
    """
    chat_sessions = await ChatSession.get_by_user_id(user_id=user.id)
    return [
        ChatSessionRead(
            id=chat_session.id,
            user_id=chat_session.user_id,
            tutor_id=chat_session.tutor_id,
            message_history=[MessageRead.from_openai_message(message) for message in chat_session.message_history],
        )
        for chat_session in chat_sessions
    ]


@router.get("/chat/{chat_id}")
async def get_chat_session(chat_id: UUID, user: ActiveVerifiedUser) -> ChatSessionRead:
    """
    Get a chat session by ID.
    """
    chat_session = await ChatSession.get(chat_id)
    if chat_session is None:
        raise CHAT_SESSION_NOT_FOUND
    if chat_session.user_id != user.id:
        raise CHAT_SESSION_NOT_FOUND
    return ChatSessionRead(
        id=chat_session.id,
        user_id=chat_session.user_id,
        tutor_id=chat_session.tutor_id,
        message_history=[MessageRead.from_openai_message(message) for message in chat_session.message_history],
    )


@router.get("/chat")
async def start_chat_session(user: ActiveVerifiedUser, tutor_id: UUID) -> ChatSessionRead:
    """
    Start a new chat session.
    """
    tutor = await Tutor.get(tutor_id)
    if tutor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tutor not found")
    if not tutor.visible:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tutor not found")
    chat_session = await ChatSession.create(user_id=user.id, tutor_id=tutor.id)
    await chat_session.get_conversation_opener(commit=True)

    return ChatSessionRead(
        id=chat_session.id,
        user_id=chat_session.user_id,
        tutor_id=chat_session.tutor_id,
        message_history=[MessageRead.from_openai_message(message) for message in chat_session.message_history],
    )


@router.post("/chat/{chat_id}")
async def post_chat_message(chat_id: UUID, message: MessageWrite, user: ActiveVerifiedUser) -> MessageRead:
    """
    Post a message to a chat session.
    """
    chat_session = await ChatSession.get_by_id_user_id(chat_session_id=chat_id, user_id=user.id)
    if chat_session is None:
        raise CHAT_SESSION_NOT_FOUND
    response = await chat_session.get_response(
        message=message,
        commit=True,
    )
    return MessageRead(
        role=MessageRole.TUTOR,
        content=response,
    )


@router.delete("/chat/{chat_id}")
async def delete_chat_session(chat_id: UUID, user: ActiveVerifiedUser) -> Response:
    """
    Delete a chat session.
    """
    chat_session = await ChatSession.get_by_id_user_id(chat_session_id=chat_id, user_id=user.id)
    if chat_session is None:
        raise CHAT_SESSION_NOT_FOUND
    await ChatSession.delete(chat_session.id)

    return Response(status_code=204)
