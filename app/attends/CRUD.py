from app.core.db.CRUD import ModelAccessor
from app.attends.model import Attends
from app.attends.schema import AttendCreate, AttendUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class AttendsAccessor(ModelAccessor[Attends, AttendCreate, AttendUpdate]):
    async def get_by_id(self, user_id: int, group_id: int, db: AsyncSession):
        attend = await db.execute(
            select(Attends).where(
                Attends.group_id == group_id, Attends.user_id == user_id
            )
        )
        return attend.scalars().first()


attends = AttendsAccessor(Attends)
