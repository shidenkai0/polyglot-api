from fastapi import APIRouter
from app.user.models import User
from app.user.schemas import UserCreate, UserRead, UserUpdate
from app.config import settings
from app.user.auth import (
    auth_backend,
    current_active_user,
    fastapi_users,
    google_oauth_client,
)

router = APIRouter(
    responses={404: {"description": "Not found"}},
)

router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="",
    tags=["users"],
)
router.include_router(
    fastapi_users.get_oauth_router(google_oauth_client, auth_backend, settings.APP_SECRET),
    prefix="/auth/google",
    tags=["auth"],
)
