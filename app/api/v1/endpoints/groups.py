from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.groups import service
from app.groups.schema import Group
from app.user.auth import get_current_user_from_token
from app.user.model import User

groups_router = APIRouter()


@groups_router.post("/all")
async def read_group(
    group_id: list[int],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
) -> list[Group]:
    groups = service.read_group(group_id, db, current_user)
    return await groups


@groups_router.post("/group")
async def get_group(
    group_name: str,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
) -> list[Group]:
    groups = await service.get_group(group_name, current_user, db)
    return groups
