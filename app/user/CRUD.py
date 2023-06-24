from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.CRUD import ModelAccessor
from app.user.model import User
from app.user.schema import UserCreate
from app.user.schema import UserUpdateData


class UserAccessor(ModelAccessor[User, UserCreate, UserUpdateData]):
    async def get_by_name(self, name, birthday_date, db: AsyncSession):
        user = await db.execute(
            select(User).where(
                User.name == str(name), User.birthday_date == birthday_date
            )
        )

        user = user.scalars().first()
        return user


user = UserAccessor(User)
