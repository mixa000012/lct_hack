import ast
from datetime import datetime
from math import atan2
from math import cos
from math import radians
from math import sin
from math import sqrt

import openrouteservice
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from openrouteservice.geocode import pelias_autocomplete
from openrouteservice.geocode import pelias_reverse
from openrouteservice.geocode import pelias_search
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.auth import get_current_user_from_token
from api.schemas import AttendShow
from api.schemas import Group
from api.schemas import GroupInDB
from api.user import get_id
from db.models import Attends
from db.models import Groups
from db.models import User
from db.session import get_db
from geocoding.get_coords import get_metro
from ml.new_users import get_new_resc
from ml.script import get_final_groups
from ml.script import get_recs

order_router = APIRouter()

recs_router = APIRouter()

routes_router = APIRouter()

groups_router = APIRouter()

client = openrouteservice.Client(
    key="5b3ce3597851110001cf6248d849a8330bbd463fb95a896f83abd13f"
)  # Specify your personal API key













async def get_date():
    return datetime.now()


async def check_attend(group_id: int, user_id: int, db):
    stmt = select(Attends).where(
        Attends.group_id == group_id, Attends.user_id == user_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()





@groups_router.delete("/attends/{id}")
async def delete_attends(
        id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),
):
    db_attends = await db.execute(
        select(Attends).where(Attends.id == id, Attends.user_id == current_user.id)
    )
    db_attends = db_attends.scalar()
    if not db_attends:
        raise HTTPException(status_code=404, detail="Attends not found")
    await db.delete(db_attends)
    await db.commit()
    return {"detail": "Deleted successfully"}


@groups_router.get("/attends_user")
async def get_attends_by_id(
        current_user: User = Depends(get_current_user_from_token),
        db: AsyncSession = Depends(get_db),
) -> list[AttendShow]:
    attends = await db.execute(
        select(Attends).where(Attends.user_id == current_user.id)
    )
    attends = attends.scalars().all()
    attends_show = []
    if len(attends) > 0:
        for i in attends:
            attend = AttendShow(
                id=i.id,
                group_id=i.group_id,
                user_id=i.user_id,
                direction_2=i.direction_2,
                direction_3=i.direction_3,
                Offline=i.Offline,
                date=i.date,
                start=i.start,
                end=i.end,
                metro=i.metro,
                address=i.address,
            )
            attends_show.append(attend)
    else:
        raise HTTPException(status_code=404, detail="Attends not found")

    if not attends:
        raise HTTPException(status_code=404, detail="Attends not found")
    return attends_show
