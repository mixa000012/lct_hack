from jose import jwt, JWTError
from starlette import status
import settings
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
from db.session import get_db
from fastapi.security import OAuth2PasswordBearer
from api.hashing import Hasher

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")


async def get_current_user_from_token(
        token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await db.execute(select(User).where(User.email == email))
    if user is None:
        raise credentials_exception
    return user


async def auth_user(email: str, password: str, db: AsyncSession) -> None | User:
    user = await db.execute(select(User).where(User.email == email))
    user = user.scalar()
    if not user:
        return
    if not Hasher.verify_password(password, user.hashed_password):
        return
    return user
