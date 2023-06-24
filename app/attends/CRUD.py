from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.attends.model import Attends
from app.attends.schema import AttendCreate
from app.attends.schema import AttendUpdate
from app.core.db.CRUD import ModelAccessor


class AttendsAccessor(ModelAccessor[Attends, AttendCreate, AttendUpdate]):
    async def get_by_id(self, user_id: int, db: AsyncSession):
        attend = await db.execute(select(Attends).where(Attends.user_id == user_id))
        return attend.scalars().all()


attends = AttendsAccessor(Attends)
