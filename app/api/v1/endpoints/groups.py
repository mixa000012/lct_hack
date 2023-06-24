from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import store
from app.core.deps import get_db
from app.groups.model import Groups
from app.groups.schema import Group
from app.groups.utils import create_group_in_db
from app.groups.utils import create_group_with_time_to_walk
from app.groups.utils import get_coordinates
from app.user.auth import get_current_user_from_token
from app.user.model import User

groups_router = APIRouter()


@groups_router.post("/all")
async def read_group(
    group_id: list[int],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
) -> list[Group]:
    groups = []
    user_address = current_user.address
    coordinates_user = await get_coordinates(user_address)

    for group_id in group_id:
        group = await store.group.get(db, group_id)
        group_in_db = await create_group_in_db(group)
        group = await create_group_with_time_to_walk(
            group_in_db,
            group.coordinates_of_address,
            coordinates_user,
            group.closest_metro,
        )
        groups.append(group)
    groups = sorted(groups, key=lambda x: (x.timeToWalk == 0, x.timeToWalk))
    return groups


@groups_router.post("/group")
async def get_group(
    group_name: str,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
) -> list[Group]:
    groups = []
    user_address = current_user.address
    coordinates_user = await get_coordinates(user_address)
    group_name = group_name.capitalize()

    result = await db.execute(select(Groups).where(Groups.direction_3 == group_name))
    result = result.scalars().all()[:12]

    for group in result:
        group_in_db = await create_group_in_db(group)
        group = await create_group_with_time_to_walk(
            group_in_db,
            group.coordinates_of_address,
            coordinates_user,
            group.closest_metro,
        )
        groups.append(group)

    return groups
