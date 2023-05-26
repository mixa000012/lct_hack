from datetime import timedelta
import settings
from security import create_access_token
from fastapi import Depends
from fastapi import HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from api.schemas import UserCreate
from api.schemas import UserShow

from db.models import User
from db.session import get_db
from api.hashing import Hasher
from api.actions.auth import auth_user

user_router = APIRouter()


@user_router.post("/create_user")
async def create_user(
        obj: UserCreate, db: AsyncSession = Depends(get_db)
) -> UserShow:
    new_task = User(
        email=obj.email,
        name=obj.name,
        hashed_password=Hasher.get_hashed_password(obj.password)
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return UserShow(
        name=new_task.name,
        user_id=new_task.user_id,
        email=new_task.email
    )


@user_router.post("/token")
async def login_for_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await auth_user(form_data.username, form_data.password, db)
    print(user.hashed_password)
    if not user:
        raise HTTPException(status_code=401, detail='There is no user in database with this email')
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
    access_token = create_access_token(
        data={"sub": user.email, "other_custom_data": [1, 2, 3, 4]},
        expires_delta=access_token_expires,
    )
    return {'access_token': access_token, 'token_type': 'bearer'}
