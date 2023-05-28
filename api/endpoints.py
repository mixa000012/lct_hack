import ast
from datetime import datetime

import openrouteservice
from fastapi import APIRouter
from fastapi import Depends
from openrouteservice.distance_matrix import distance_matrix
from openrouteservice.geocode import pelias_autocomplete
from openrouteservice.geocode import pelias_reverse, pelias_search
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.user import get_id
from api.actions.auth import get_current_user_from_token
from api.schemas import Group
from api.schemas import GroupInDB
from db.models import Groups
from db.models import User
from db.session import get_db
from geocoding.get_coords import get_metro
from ml.new_users import get_new_resc
from ml.script import get_recs
from db.models import Attends
from api.schemas import AttendShow
from ml.script import get_final_groups

order_router = APIRouter()

recs_router = APIRouter()

routes_router = APIRouter()

groups_router = APIRouter()

client = openrouteservice.Client(
    key="5b3ce3597851110001cf6248d849a8330bbd463fb95a896f83abd13f"
)  # Specify your personal API key
api_key = "5b3ce3597851110001cf6248d4e646702ef148e5a55e272b239c23cb"


async def calculate_time_to_walk(coordinate_place, address):
    routes = pelias_search(client, address, country="RUS")
    final_coords = routes.get("features")[0].get("geometry").get("coordinates")[::-1]
    coordinates_user = (final_coords[0], final_coords[1])
    coordinates = ast.literal_eval(coordinate_place)
    coord = (coordinates_user, coordinates)
    try:
        routes = distance_matrix(client, coord, profile="foot-walking")
    except:
        return 1000
    time = routes.get("durations")[0][1]
    if time:
        return int(time) / 60
    else:
        return 480


async def get_group_from_db(group_id: int, session: AsyncSession) -> Groups:
    result = await session.execute(select(Groups).where(Groups.id == group_id))
    group_in_db = result.scalar_one_or_none()
    return group_in_db


@routes_router.post("/groups")
async def read_group(
        group_id: list[int], db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token)) -> list[Group]:
    groups = []

    for i in group_id:
        group = await get_group_from_db(i, db)
        group_in_db = GroupInDB(
            id=i,
            name=group.direction_3,
            type=group.direction_1,
            address=group.address,
            metro=group.closest_metro,
            time=group.schedule_active
            if len(group.schedule_active) > 0
            else group.schedule_closed,
        )
        if group.closest_metro == "Онлайн":
            group = Group(**group_in_db.dict(), timeToWalk=0)
            groups.append(group)
        else:
            group = Group(
                **group_in_db.dict(),
                # timeToWalk=1000
                timeToWalk=await calculate_time_to_walk(
                    group.coordinates_of_address, current_user.address
                )
            )
            groups.append(group)
    return groups


@routes_router.post("/get_time")
async def get_time(coordinates: str) -> dict:
    coordinates = ast.literal_eval(coordinates)
    routes = distance_matrix(client, coordinates, profile="foot-walking")
    return routes


@routes_router.get("/suggest")
async def suggest(query: str) -> list[str]:
    results = []
    try:
        routes = pelias_autocomplete(client, query, country="RUS", layers=["address"])
        for i in range(10):
            result = routes.get("features")[i].get("properties").get("name")
            results.append(result)
    except:
        return results

    return results


@routes_router.get("/address")
async def get_address(coordinates: str) -> dict:
    coordinates = ast.literal_eval(coordinates)
    coordinates = (coordinates[1], coordinates[0])
    routes = pelias_reverse(client, coordinates, country="RUS")
    return routes


@recs_router.get("/")
async def give_recs(current_user: User = Depends(get_current_user_from_token)) -> list[int]:
    result = await get_recs(int(current_user.id))
    return result


@recs_router.post("/new")
async def give_recs_for_new_users(
        current_user: User = Depends(get_current_user_from_token),
):
    now_interests = ast.literal_eval(current_user.survey_result)
    metro = get_metro(current_user.address)

    result = get_new_resc(now_interests, current_user.sex, current_user.birthday_date)
    result = await get_final_groups(chat_id=int(result), metro_human=metro)
    return result


@recs_router.get('/is_exist')
async def is_exist_recs(current_user: User = Depends(get_current_user_from_token)) -> bool:
    try:
        await get_recs(int(current_user.id))
        return True
    except KeyError:
        return False


@groups_router.get('/group')
async def get_group(group_name: str, current_user: User = Depends(get_current_user_from_token),
                    db: AsyncSession = Depends(get_db)) -> list[Group]:
    groups = []
    result = await db.execute(select(Groups).where(Groups.direction_3 == group_name))
    result = result.scalars().all()[::6]
    for group in result:
        group_in_db = GroupInDB(
            id=group.id,
            name=group.direction_3,
            type=group.direction_1,
            address=group.address,
            metro=group.closest_metro,
            time=group.schedule_active
            if len(group.schedule_active) > 0
            else group.schedule_closed,
        )
        if group.closest_metro == "Онлайн":
            group = Group(**group_in_db.dict(), timeToWalk=0)
            groups.append(group)
        else:
            group = Group(
                **group_in_db.dict(),
                # timeToWalk=1000
                timeToWalk=await calculate_time_to_walk(
                    group.coordinates_of_address, current_user.address
                )
            )
            groups.append(group)
    return groups


@groups_router.post("/attends/")
async def create_attend(group_id: int, current_user: User = Depends(get_current_user_from_token),
                        db: AsyncSession = Depends(get_db)):
    group = await get_group_from_db(group_id=group_id, session=db)
    db_attends = Attends(
        id=await get_id(),
        group_id=group.id,
        user_id=current_user.id,
        direction_2=group.direction_2,
        direction_3=group.direction_3,
        Offline=False if group.closest_metro == 'Онлайн' else True,
        date=datetime.now(),
        start=group.schedule_active,
        end=group.schedule_active
    )
    db.add(db_attends)
    await db.commit()
    await db.refresh(db_attends)
    return AttendShow(
        id=db_attends.id,
        group_id=db_attends.id,
        user_id=db_attends.user_id,
        direction_2=db_attends.direction_2,
        direction_3=db_attends.direction_3,
        Offline=db_attends.Offline,
        date=db_attends.date,
        start=db_attends.start,
        end=db_attends.end
    )
