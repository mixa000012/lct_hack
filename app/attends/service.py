from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.attends.schema import AttendCreate
from app.core import store
from app.core.deps import get_db
from app.user.auth import get_current_user_from_token
from app.user.schema import User


class AttendAlreadyExists(Exception):
    pass


class AttendsDoesntExist(Exception):
    pass


class WrondUser(Exception):
    pass


async def get_by_id(groud_id: int, user_id: int, db: AsyncSession):
    return await store.attends.get_by_id(groud_id, user_id, db)


async def create_attend(
    group_id: int,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    existing_attend = await store.attends.get_by_id(
        group_id=group_id, user_id=current_user.id, db=db
    )
    if existing_attend:
        raise AttendAlreadyExists
    # coordinates_user = await get_coordinates(current_user.address)
    group = await store.group.get(db, group_id)
    db_attends = AttendCreate(
        group_id=group.id,
        user_id=current_user.id,
        direction_2=group.direction_2,
        direction_3=group.direction_3,
        offline=group.closest_metro == "Онлайн",
        start=group.schedule_closed,
        end="10",
        metro=group.closest_metro,
        address=group.address,
    )

    attend = await store.attends.create(db=db, obj_in=db_attends)
    return attend


async def delete_attends(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    attend = await store.attends.get(db, id)
    if not attend:
        raise AttendsDoesntExist
    if attend.user_id == current_user.id:
        db_attends = await store.attends.remove(db=db, id=id)
    else:
        raise WrondUser
    return db_attends


async def get_attends_by_id(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    attends = await store.attends.get_by_id_multi(db=db, user_id=current_user.id)
    if not attends:
        raise AttendsDoesntExist
    return attends
