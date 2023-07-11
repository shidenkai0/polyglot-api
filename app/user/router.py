from fastapi import APIRouter, HTTPException
from firebase_admin import auth
from firebase_admin.auth import (
    ExpiredIdTokenError,
    InvalidIdTokenError,
    RevokedIdTokenError,
)

from app.user.models import User
from app.user.schemas import UserCreate, UserRead

router = APIRouter(
    responses={404: {"description": "Not found"}},
    tags=["users"],
)


@router.post("")
async def create_user(user: UserCreate):
    try:
        decoded_token = auth.verify_id_token(user.firebase_id_token)
    except (ValueError, InvalidIdTokenError, ExpiredIdTokenError, RevokedIdTokenError):
        raise HTTPException(status_code=401, detail="Unauthorized")

    firebase_uid = decoded_token['uid']

    db_user = await User.get_by_firebase_uid(firebase_uid)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")

    db_user = await User.create(
        email=user.email,
        firebase_uid=firebase_uid,
        first_name=user.first_name,
        last_name=user.last_name,
        locale=user.locale,
        is_superuser=False,
    )

    return UserRead(
        id=db_user.id,
        email=db_user.email,
        firebase_uid=firebase_uid,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        locale=db_user.locale,
    )
