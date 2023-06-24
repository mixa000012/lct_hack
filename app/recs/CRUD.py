from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db.CRUD import ModelAccessor
from app.groups.model import Groups
from app.user.schema import UserCreate, UserUpdateData


class RecsAccessor(ModelAccessor[Groups, UserCreate, UserUpdateData]):
    pass


recs = RecsAccessor(Groups)
