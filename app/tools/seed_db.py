import asyncio
import uuid
from datetime import datetime

import firebase_admin
from firebase_admin import auth, credentials

from app.chat.models import ChatSession
from app.chat.schemas import OpenAIMessage, OpenAIMessageRole
from app.config import settings
from app.tutor.models import ModelName, Tutor
from app.user.models import User

cred = credentials.Certificate(settings.FIREBASE_KEY_FILE)
firebase_admin.initialize_app(cred)


async def create_user(email: str, firebase_uid: str, name: str, language: str, is_superuser: bool) -> User:
    user = await User.create(
        email=email, firebase_uid=firebase_uid, name=name, language=language, is_superuser=is_superuser
    )
    return user


async def create_tutor(
    name: str, avatar_url: str, language: str, model: ModelName, visible: bool = True, personality_prompt: str = ""
) -> Tutor:
    tutor = await Tutor.create(
        name=name,
        avatar_url=avatar_url,
        language=language,
        model=model,
        visible=visible,
        personality_prompt=personality_prompt,
    )
    return tutor


async def create_chat_session(user_id: uuid.UUID, tutor_id: uuid.UUID) -> ChatSession:
    message_history = [
        OpenAIMessage(
            role=OpenAIMessageRole.ASSISTANT,
            content="Hello",
            timestamp_ms=(datetime.now().timestamp() - 120) * 1e3,
            uuid=str(uuid.uuid4()),
        ),
        OpenAIMessage(
            role=OpenAIMessageRole.USER,
            content="Hello",
            timestamp_ms=(datetime.now().timestamp() - 60) * 1e3,
            uuid=str(uuid.uuid4()),
        ),
        OpenAIMessage(
            role=OpenAIMessageRole.ASSISTANT,
            content="How can I assist you today?",
            timestamp_ms=(datetime.now().timestamp() - 55) * 1e3,
            uuid=str(uuid.uuid4()),
        ),
        OpenAIMessage(
            role=OpenAIMessageRole.USER,
            content="I would like to practice my language skills",
            timestamp_ms=(datetime.now().timestamp() - 5) * 1e3,
            uuid=str(uuid.uuid4()),
        ),
        OpenAIMessage(
            role=OpenAIMessageRole.ASSISTANT,
            content="Absolutely, we can start by discussing a variety of topics",
            timestamp_ms=datetime.now().timestamp() * 1e3,
            uuid=str(uuid.uuid4()),
        ),
    ]

    chat_session = await ChatSession.create(
        user_id=user_id, tutor_id=tutor_id, message_history=message_history, max_tokens=500, max_messages=100
    )
    return chat_session


async def seed_db():
    # Create user in firebase
    firebase_user = auth.create_user(email="testuser@example.com", password="stpzga8n", email_verified=True)

    # Create user in DB
    user = await create_user(
        email="testuser@example.com",
        firebase_uid=firebase_user.uid,
        name="Testuser",
        language="en",
        is_superuser=False,
    )

    # Create tutors
    tutors = []
    for i in range(2):
        tutors.append(
            await create_tutor(
                name=f"Frenchie {i+1}",
                avatar_url="https://cdn-icons-png.flaticon.com/512/168/168726.png",
                language="french",
                model=ModelName.GPT3_5_TURBO,
            )
        )

        tutors.append(
            await create_tutor(
                name=f"Englie {i+1}",
                avatar_url="https://cdn-icons-png.flaticon.com/512/168/168726.png",
                language="english",
                model=ModelName.GPT3_5_TURBO,
            )
        )

    # Create chat sessions
    for tutor in tutors:
        await create_chat_session(user.id, tutor.id)


asyncio.run(seed_db())
