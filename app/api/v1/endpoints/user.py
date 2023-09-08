from random import randint

from fastapi import Body
from fastapi import Depends
from fastapi import HTTPException
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.user import service
from app.user.auth import get_current_user_from_token
from app.user.schema import TokenData
from app.user.schema import User
from app.user.schema import UserCreate
from app.user.schema import UserUpdateData
from app.user.service import UserAlreadyExist
from app.user.service import UserDoesntExist


router = APIRouter()


async def get_id():
    return randint(100000000, 900000000)


@router.post("/token")
async def login_for_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> TokenData:
    try:
        access_token = await service.login_for_token(form_data, db)
    except UserDoesntExist:
        raise HTTPException(
            status_code=401, detail="There is no user in database with this fio"
        )
    return TokenData(access_token=access_token, token_type="bearer")


@router.post("/users")
async def create_user(obj: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    try:
        user = await service.create_user(obj, db)
    except UserAlreadyExist:
        raise HTTPException(status_code=409, detail="User already exists")
    return user


@router.put("/users")
async def update_user(
    current_user: User = Depends(get_current_user_from_token),
    update_data: UserUpdateData = Body(...),
    db: AsyncSession = Depends(get_db),
) -> User:
    updated_user = await service.update_user(current_user, update_data, db)
    return updated_user
