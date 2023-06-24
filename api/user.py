# import datetime
# from datetime import timedelta
# from random import randint
#
# from fastapi import Body
# from fastapi import Depends
# from fastapi import HTTPException
# from fastapi.routing import APIRouter
# from fastapi.security import OAuth2PasswordRequestForm
# from sqlalchemy import update
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
#
# import settings
# from api.actions.auth import auth_user
# from api.actions.auth import get_current_user_from_token
# from api.schemas import TokenData
# # from api.schemas import UserCreate
# # from api.schemas import UserShow
# # from api.schemas import UserShowAddress
# # from api.schemas import UserUpdateData
# from db.models import User
# from db.session import get_db
# from security import create_access_token
#
# user_router = APIRouter()
#
#
# # Retrieve the updated user from the database    return result.scalar_one()
# async def get_id():
#     return randint(100000000, 900000000)
#

#
#
# @user_router.post("/create_user")
# async def create_user(obj: UserCreate, db: AsyncSession = Depends(get_db)) -> UserShow:
#     user = await db.execute(
#         select(User).where(
#             User.name == str(obj.name), User.birthday_date == obj.birthday_date
#         )
#     )
#     user = user.scalars().first()
#     if user:
#         raise HTTPException(status_code=409, detail="User already exists")
#     await validate_date(obj.birthday_date)
#     new_user = User(
#         id=await get_id(),
#         name=str(obj.name),
#         birthday_date=obj.birthday_date,
#     )
#     db.add(new_user)
#     await db.commit()
#     await db.refresh(new_user)
#     return UserShow(
#         name=new_user.name, user_id=new_user.id, birthday_date=new_user.birthday_date
#     )
#
#
# @user_router.post("/token")
# async def login_for_token(
#         form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
# ) -> TokenData:
#     user = await auth_user(form_data.username, form_data.password, db)
#     if not user:
#         raise HTTPException(
#             status_code=401, detail="There is no user in database with this fio"
#         )
#     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
#     access_token = create_access_token(
#         data={"sub": str(user.id)},
#         expires_delta=access_token_expires,
#     )
#     return TokenData(access_token=access_token, token_type="bearer")
#
#
# @user_router.get("/login")
# async def ping(current_user: User = Depends(get_current_user_from_token)):
#     return {"success": True, "user": current_user}
#
#
# @user_router.put("/update_user")
# async def update_user(
#         current_user: User = Depends(get_current_user_from_token),
#         update_data: UserUpdateData = Body(...),
#         db: AsyncSession = Depends(get_db),
# ) -> UserShowAddress:
#
#     # The below assumes that you have a function to update the user in your database
#     if update_data.sex not in ['Мужчина', 'Женщина']:
#         raise HTTPException(
#             status_code=400, detail="Wrong gender!"
#         )
#     stmt = (
#         update(User)
#         .where(User.id == current_user.id)
#         .values(
#             sex=update_data.sex,
#             address=update_data.address,
#             survey_result=update_data.survey_result,
#         )
#     )
#
#     # Execute the update statement
#     await db.execute(stmt)
#
#     # Commit the changes
#     await db.commit()
#
#     # Retrieve the updated user from the database
#     result = await db.execute(select(User).where(User.id == current_user.id))
#     updated_user = result.scalar_one()
#
#     return UserShowAddress(
#         sex=updated_user.sex,
#         birthday_date=updated_user.birthday_date,
#         name=updated_user.name,
#         user_id=updated_user.id,
#         address=updated_user.address,
#         created_at=updated_user.created_at,
#         survey_result=updated_user.survey_result,
#     )
