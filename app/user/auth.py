from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth

from app.user.models import User

security = HTTPBearer()


async def authenticate_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> User:
    id_token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(id_token)
        firebase_uid = decoded_token['uid']
        email_verified = decoded_token['email_verified']
        if not email_verified:
            raise HTTPException(status_code=403, detail="Email not verified")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    user = await User.get_by_firebase_uid(firebase_uid)
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    return user


async def authenticate_superuser(user: Annotated[User, Depends(authenticate_user)]) -> User:
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized",
        )
    return user


ActiveVerifiedUser = Annotated[User, Depends(authenticate_user)]
SuperUser = Annotated[User, Depends(authenticate_superuser)]
