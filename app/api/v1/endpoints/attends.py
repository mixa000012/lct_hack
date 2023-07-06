from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.attends.schema import Attend
from app.attends.schema import AttendCreate
from app.attends.utils import get_id, get_date
from app.core import store
from app.core.deps import get_db
from app.groups.utils import calculate_time_to_walk
from app.groups.utils import get_coordinates
from app.user.auth import get_current_user_from_token
from app.user.schema import User

attends_router = APIRouter()


@attends_router.post("/attends")
async def create_attend(
        group_id: int,
        current_user: User = Depends(get_current_user_from_token),
        db: AsyncSession = Depends(get_db),
) -> Attend:
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
        start=group.schedule_closed,
        end=str(
            await calculate_time_to_walk(group.coordinates_of_address, coordinates_user)
        )
        if group.coordinates_of_address
        else "0",
        metro=group.closest_metro,
        address=group.address,
        date=await get_date()
    )
    attend = await store.attends.create(db=db, obj_in=db_attends)
    return attend.__dict__

@attends_router.delete("/attends/{id}")
async def delete_attends(
        id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),
):
    db_attends = await store.attends.remove(db=db, id=id)
    if not db_attends:
        raise HTTPException(status_code=404, detail="Attends not found")

    return {"detail": db_attends}


@attends_router.get("/attends_user")
async def get_attends_by_id(
        current_user: User = Depends(get_current_user_from_token),
        db: AsyncSession = Depends(get_db),
) -> list[Attend]:
    attends = await store.attends.get_by_id_multi(db=db, user_id=current_user.id)
    if not attends:
        raise HTTPException(status_code=404, detail="Attends not found")
    return attends
