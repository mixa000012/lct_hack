from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.auth import get_current_user_from_token
from app.attends.utils import get_id
from app.core.deps import get_db
from app.core import store
from app.groups.utils import get_coordinates
from app.attends.schema import AttendCreate
from app.user.schema import User
from app.attends.utils import get_date
from app.groups.utils import calculate_time_to_walk

attends_router = APIRouter()


@attends_router.post("/attends")
async def create_attend(
        group_id: int,
        current_user: User = Depends(get_current_user_from_token),
        db: AsyncSession = Depends(get_db),
):
    existing_attend = await store.attends.get_by_id(
        group_id=group_id, user_id=current_user.id, db=db
    )
    if existing_attend:
        raise HTTPException(status_code=400, detail="Attendance record already exists.")

    coordinates_user = await get_coordinates(current_user.address)

    group = await store.group.get(db, group_id)
    db_attends = AttendCreate(
        id=await get_id(),
        group_id=group.id,
        user_id=current_user.id,
        direction_2=group.direction_2,
        direction_3=group.direction_3,
        Offline=False if group.closest_metro == "Онлайн" else True,
        date=await get_date(),
        start=group.schedule_closed,
        end=str(
            await calculate_time_to_walk(group.coordinates_of_address, coordinates_user)
        )
        if group.coordinates_of_address
        else "0",
        metro=group.closest_metro,
        address=group.address,
    )
    attend = await store.attends.create(db=db, obj_in=db_attends)
    return attend
