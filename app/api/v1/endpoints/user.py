import datetime
from datetime import timedelta
from random import randint

from fastapi import Body
from fastapi import Depends
from fastapi import HTTPException
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from app.core import store
from app.core.deps import get_db
from app.user.auth import auth_user
from app.user.auth import get_current_user_from_token
from app.user.schema import TokenData
from app.user.schema import User
from app.user.schema import UserCreate
from app.user.schema import UserUpdateData
from security import create_access_token

router = APIRouter()


async def get_id():
    return randint(100000000, 900000000)


async def validate_date(date_text):
    try:
        datetime.date.fromisoformat(date_text)
        return
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Incorrect data format, should be YYYY-MM-DD"
        )


@router.post("/token")
async def login_for_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> TokenData:
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
    return TokenData(access_token=access_token, token_type="bearer")


@router.post("/create_user")
async def create_user(obj: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    await validate_date(obj.birthday_date)
    user = await store.user.get_by_name(obj.name, obj.birthday_date, db)
    if user:
        raise HTTPException(status_code=409, detail="User already exists")
    user = await store.user.create(
        db,
        obj_in=UserCreate(
            name=obj.name,
            birthday_date=obj.birthday_date,
        ),
    )
    return user


@router.put("/update_user")
async def update_user(
    current_user: User = Depends(get_current_user_from_token),
    update_data: UserUpdateData = Body(...),
    db: AsyncSession = Depends(get_db),
) -> User:
    updated_user = await store.user.update(
        db=db,
        db_obj=current_user,
        obj_in=update_data,
    )

    return updated_user
