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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


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
        uuid: str = payload.get("sub")
        if uuid is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await db.execute(select(User).where(User.uuid == uuid))
    user = user.scalar()
    if user is None:
        raise credentials_exception
    return user.uuid


async def auth_user(name: str, birthday_date: str, db: AsyncSession) -> None | User:
    user = await db.execute(select(User).where(User.name == name, User.birthday_date == birthday_date))
    user = user.scalar()
    if not user:
        return
    return user
