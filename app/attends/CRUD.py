from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.attends.model import Attends
from app.attends.schema import AttendCreate
from app.attends.schema import AttendUpdate
from app.core.db.CRUD import ModelAccessor


class AttendsAccessor(ModelAccessor[Attends, AttendCreate, AttendUpdate]):
    async def get_by_id(self, user_id: int, db: AsyncSession, group_id: int):
        attend = await db.execute(select(Attends).where(Attends.user_id == user_id, Attends.group_id == group_id))
        return attend.scalars().all()

    async def get_by_id_multi(self, user_id: int, db: AsyncSession):
        attend = await db.execute(select(Attends).where(Attends.user_id == user_id))
        return [x.__dict__ for x in attend.scalars().all()]


attends = AttendsAccessor(Attends)
