from datetime import timedelta

from fastapi import Depends
from fastapi import HTTPException
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from api.actions.auth import auth_user
from api.actions.auth import get_current_user_from_token
from api.schemas import UserCreate
from api.schemas import UserShow
from db.models import User
from db.session import get_db
from security import create_access_token

user_router = APIRouter()


@user_router.post("/create_user")
async def create_user(obj: UserCreate, db: AsyncSession = Depends(get_db)) -> UserShow:
    user = await db.execute(
        select(User).where(
            User.name == obj.name, User.birthday_date == obj.birthday_date
        )
    )
    user = user.scalars().first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = User(
        name=obj.name,
        birthday_date=obj.birthday_date,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserShow(
        name=new_user.name, user_id=new_user.id, birthday_date=new_user.birthday_date
    )


@user_router.post("/token")
async def login_for_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> dict:
    user = await auth_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=401, detail="There is no user in database with this fio"
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.get("/login")
async def ping(current_user: User = Depends(get_current_user_from_token)):
    return {"success": True, "user": current_user}
