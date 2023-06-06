import ast
from datetime import datetime

import openrouteservice
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from openrouteservice.distance_matrix import distance_matrix
from openrouteservice.geocode import pelias_autocomplete
from openrouteservice.geocode import pelias_reverse
from openrouteservice.geocode import pelias_search
from sqlalchemy import select
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


async def calculate_time_to_walk(coordinate_place, address):
    """
    Asynchronously calculates the estimated time in minutes to walk from a given address to a place specified
    by its coordinates. Utilizes the OpenRouteService's distance matrix API.

    Parameters:
    ------------
    coordinate_place: str
        String of coordinates (latitude, longitude) of the target place.

    address: str
        User's current location address.

    Returns:
    ------------
    float
        Estimated walking time from current location to the place. Defaults to 480 minutes if unable to calculate,
        or 1000 minutes if an API call error occurs.
    """
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


@groups_router.post("/groups")
async def read_group(
    group_id: list[int],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
) -> list[Group]:
    """
    Asynchronously retrieves a list of Group objects specified by their IDs. The returned Group objects also include
    an estimate of the walking time from the user's current location to each group's location.

    Parameters:
    ------------
    group_id: list[int]
        A list of integer identifiers for the groups to be retrieved.

    db: AsyncSession
        An asynchronous SQLAlchemy session for database operations. Injected by FastAPI's dependency injection system.

    current_user: User
        The User object representing the current user. Injected by FastAPI's dependency injection system.

    Returns:
    ------------
    list[Group]
        A list of Group objects corresponding to the provided IDs.
    """
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
    """
    Asynchronously retrieves a list of suggested addresses based on the input query. This utilizes the
    OpenRouteService's Pelias Autocomplete API to provide address suggestions.

    Parameters:
    ------------
    query: str
        A string input that is used to suggest addresses.

    Returns:
    ------------
    list[str]
        A list of suggested addresses, up to 10, based on the input query. If an error occurs, it returns an empty list.
    """
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
    """
    Asynchronously retrieves the address corresponding to the provided coordinates. This uses the OpenRouteService's
    Pelias Reverse Geocoding API to obtain the address.

    Parameters:
    ------------
    coordinates: str
        A string representation of the coordinates (longitude, latitude) for which the address is to be retrieved.

    Returns:
    ------------
    dict
        A dictionary containing the address information corresponding to the provided coordinates.
    """
    coordinates = ast.literal_eval(coordinates)
    coordinates = (coordinates[1], coordinates[0])
    routes = pelias_reverse(client, coordinates, country="RUS")
    return routes


@recs_router.get("/")
async def give_recs(
    current_user: User = Depends(get_current_user_from_token),
) -> list[int]:
    """
    Asynchronously generates recommendations for the current user based on their user data.
    It utilizes a machine learning function `get_recs` to produce the recommendations.

    Parameters:
    ------------
    current_user: User
        The User object representing the current user. Injected by FastAPI's dependency injection system.

    Returns:
    ------------
    list[int]
        A list of integer identifiers for the recommended groups.
    """
    result = await get_recs(int(current_user.id), N=12)
    return result


@recs_router.post("/new")
async def give_recs_for_new_users(
    current_user: User = Depends(get_current_user_from_token),
) -> list[int]:
    """
    Asynchronously generates recommendations for new users based on their survey results and other data.
    Utilizes a machine learning function `get_new_recs` for generating the recommendations.

    Parameters:
    ------------
    current_user: User
        The User object representing the current user. Injected by FastAPI's dependency injection system.

    Returns:
    ------------
    list[int]
        A list of integer identifiers for the recommended groups.
    """
    now_interests = ast.literal_eval(current_user.survey_result)
    metro = get_metro(current_user.address)
    if metro == "далековато":
        metro = "Ленинский проспект"

    result = get_new_resc(now_interests, current_user.sex, current_user.birthday_date)
    result = await get_final_groups(chat_id=int(result), metro_human=metro)
    return result


@recs_router.get("/is_exist")
async def is_exist_recs(
    current_user: User = Depends(get_current_user_from_token),
) -> bool:
    """
    Asynchronously checks if the current user has any recommendations available.

    Parameters:
    ------------
    current_user: User
        The User object representing the current user. Injected by FastAPI's dependency injection system.

    Returns:
    ------------
    bool
        Returns True if recommendations for the current user exist; otherwise, it returns False.
    """
    try:
        await get_recs(int(current_user.id), N=10)
        return True
    except KeyError:
        return False


@groups_router.get("/group")
async def get_group(
    group_name: str,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
) -> list[Group]:
    """
    Asynchronously retrieves a list of Group objects that match the provided group name. It also includes
    an estimated walking time from the current user's location to each group's location.

    Parameters:
    ------------
    group_name: str
        Name of the group to be retrieved.

    current_user: User
        The User object representing the current user. Injected by FastAPI's dependency injection system.

    db: AsyncSession
        An asynchronous SQLAlchemy session for database operations. Injected by FastAPI's dependency injection system.

    Returns:
    ------------
    list[Group]
        A list of Group objects corresponding to the provided group name.
    """
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


async def get_date():
    return datetime.now()


async def check_attend(group_id: int, user_id: int, db):
    stmt = select(Attends).where(
        Attends.group_id == group_id, Attends.user_id == user_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@groups_router.post("/attends")
async def create_attend(
    group_id: int,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Asynchronously creates an attendance record for the current user for a specified group.

    Parameters:
    ------------
    group_id: int
        Identifier of the group for which the attendance is to be recorded.

    current_user: User
        The User object representing the current user. Injected by FastAPI's dependency injection system.

    db: AsyncSession
        An asynchronous SQLAlchemy session for database operations. Injected by FastAPI's dependency injection system.

    Returns:
    ------------
    AttendShow
        The newly created attendance record, represented as an AttendShow object.
    """
    existing_attend = await check_attend(
        group_id=group_id, user_id=current_user.id, db=db
    )
    if existing_attend:
        raise HTTPException(status_code=400, detail="Attendance record already exists.")
    group = await get_group_from_db(group_id=group_id, session=db)
    db_attends = Attends(
        id=await get_id(),
        group_id=group.id,
        user_id=current_user.id,
        direction_2=group.direction_2,
        direction_3=group.direction_3,
        Offline=False if group.closest_metro == "Онлайн" else True,
        date=await get_date(),
        start=group.schedule_active,
        end=group.schedule_active,
        metro=group.closest_metro,
        address=group.address,
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
        end=db_attends.end,
        metro=group.closest_metro,
        address=group.address,
    )


@groups_router.delete("/attends/{id}")
async def delete_attends(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """
    Asynchronously deletes an attendance record specified by its identifier.
    The operation is only allowed if the current user is the owner of the record.

    Parameters:
    ------------
    id: int
        Identifier of the attendance record to be deleted.

    db: AsyncSession
        An asynchronous SQLAlchemy session for database operations. Injected by FastAPI's dependency injection system.

    current_user: User
        The User object representing the current user. Injected by FastAPI's dependency injection system.

    Returns:
    ------------
    dict
        A dictionary containing a message indicating the success of the deletion operation.
    """
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
