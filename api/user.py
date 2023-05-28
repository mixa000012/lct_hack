from datetime import timedelta

from fastapi import Depends
from fastapi import HTTPException
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.schemas import TokenData
import settings
from api.actions.auth import auth_user
from api.actions.auth import get_current_user_from_token
from api.schemas import UserCreate
from api.schemas import UserShow
from db.models import User
from db.session import get_db
from security import create_access_token
from api.schemas import UserUpdateData
from fastapi import Body
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from db.models import User
from api.schemas import UserShowAddress

user_router = APIRouter()


# Retrieve the updated user from the database    return result.scalar_one()

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
) -> TokenData:
    """
       This endpoint is responsible for user authentication and token generation.

       Parameters:
       - form_data (OAuth2PasswordRequestForm): A form request object which includes
         the username and password for user authentication. This is required.
       - db (AsyncSession): A database session which is used for querying the database.
         This is required.

       Returns:
       - dict: A dictionary with the access token and token type.

       Errors:
       - HTTPException: 401 error if there is no user in the database with the
         supplied username.
       """
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
    return TokenData(
        access_token=access_token,
        token_type='bearer'
    )


@user_router.get("/login")
async def ping(current_user: User = Depends(get_current_user_from_token)):
    return {"success": True, "user": current_user}


@user_router.put("/update_user")
async def update_user(
        current_user: User = Depends(get_current_user_from_token),
        update_data: UserUpdateData = Body(...), db: AsyncSession = Depends(get_db)
) -> UserShowAddress:
    """
    This endpoint allows the update of the user's information.

    Parameters:
    - current_user (User): The current user extracted from the authentication token.
    - update_data (UserUpdateData): The updated information for the user.

    Returns:
    - dict: A dictionary containing a success status and the updated user information.
    """
    # The below assumes that you have a function to update the user in your database
    stmt = (
        update(User).
        where(User.id == current_user.id).
        values(sex=update_data.sex, address=update_data.address)
    )

    # Execute the update statement
    await db.execute(stmt)

    # Commit the changes
    await db.commit()

    # Retrieve the updated user from the database
    result = await db.execute(select(User).where(User.id == current_user.id))
    updated_user = result.scalar_one()

    return UserShowAddress(
        sex=updated_user.sex,
        birthday_date=updated_user.birthday_date,
        name=updated_user.name,
        user_id=updated_user.id,
        address=updated_user.address,
        created_at=updated_user.created_at
    )
