from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.deps import get_db
from app.user.model import User
from utils import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/token")


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
        id: int = int(payload.get("sub"))
        if id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await db.execute(select(User).where(User.id == id))
    user = user.scalar()
    if user is None:
        raise credentials_exception
    return user


async def auth_user(name: str, birthday_date: str, db: AsyncSession) -> None | User:
    user = await db.execute(
        select(User).where(User.name == name, User.birthday_date == birthday_date)
    )
    user = user.scalar()
    if not user:
        return
    return user
