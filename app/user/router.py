from fastapi import APIRouter, Depends, HTTPException

from app.user.models import User
from app.user.schemas import UserCreate, UserRead

router = APIRouter(
    responses={404: {"description": "Not found"}},
    tags=["users"],
)


@router.post("")
async def create_user(user: UserCreate):
    db_user = User.get_by_firebase_uid(user.firebase_uid)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    db_user = await User.create(**user.dict())

    return UserRead(
        id=db_user.id,
        email=db_user.email,
        firebase_uid=db_user.firebase_uid,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        locale=db_user.locale,
    )
