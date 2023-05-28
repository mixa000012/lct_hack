import ast

import openrouteservice
from fastapi import APIRouter
from fastapi import Depends
from openrouteservice.distance_matrix import distance_matrix
from openrouteservice.geocode import pelias_autocomplete
from openrouteservice.geocode import pelias_reverse, pelias_search
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.auth import get_current_user_from_token
from api.schemas import Group
from api.schemas import GroupInDB
from db.models import Groups
from db.models import User
from db.session import get_db
from geocoding.get_coords import get_metro
from ml.new_users import get_new_resc
from ml.script import get_recs

order_router = APIRouter()

recs_router = APIRouter()

routes_router = APIRouter()

client = openrouteservice.Client(
    key="5b3ce3597851110001cf6248d849a8330bbd463fb95a896f83abd13f"
)  # Specify your personal API key
api_key = "5b3ce3597851110001cf6248d4e646702ef148e5a55e272b239c23cb"


async def calculate_time_to_walk(coordinate_place, coordinate_user):
    coordinates = ast.literal_eval(coordinate_place)
    coord = (coordinate_user, coordinates)
    print(coord)
    try:
        routes = distance_matrix(client, coord, profile="foot-walking")
    except:
        return 1000
    print(coord)
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
    routes = pelias_search(client, current_user.address, country="RUS")
    final_coords = routes.get("features")[0].get("geometry").get("coordinates")[::-1]
    coordinates_user = (final_coords[0], final_coords[1])
    for i in group_id:
        group = await get_group_from_db(i, db)
        group_in_db = GroupInDB(
            id=i,
            name=group.direction_3,
            type=group.direction_1,
            address=group.address,
            tags=["tag1", "tag2", "tag3"],
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
                    group.coordinates_of_address, coordinates_user
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
    routes = pelias_autocomplete(client, query, country="RUS", layers=["address"])
    for i in range(10):
        result = routes.get("features")[i].get("properties").get("name")
        results.append(result)

    return results


@routes_router.get("/address")
async def get_address(coordinates: str):
    coordinates = ast.literal_eval(coordinates)
    coordinates = (coordinates[1], coordinates[0])
    routes = pelias_reverse(client, coordinates, country="RUS")
    return routes


@recs_router.get("/")
async def give_recs(current_user: User = Depends(get_current_user_from_token)) -> list[int]:
    result = await get_recs(int(current_user.id))
    return result


@recs_router.post("new")
async def give_recs_for_new_users(
        now_interests: list[int],
        current_user: User = Depends(get_current_user_from_token),
):
    metro = get_metro(current_user.address)
    result = get_new_resc(now_interests, current_user.sex, current_user.birthday_date)
    return result


@recs_router.get('/is_exist')
async def is_exist_recs(current_user: User = Depends(get_current_user_from_token)) -> bool:
    try:
        await get_recs(int(current_user.id))
        return True
    except KeyError:
        return False

# @admin_router.get('/all')
# async def get_all_admins(db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Admins))
#     admins = result.scalars().all()
#     user_ids = [value.user_id for value in admins]
#     return user_ids
#
#
# @admin_router.post('/add_admin')
# async def add_admin(user_id: int, db: AsyncSession = Depends(get_db)) -> CreateAdmins:
#     new_admin = Admins(
#         user_id=user_id)
#     db.add(new_admin)
#     await db.commit()
#     await db.refresh(new_admin)
#     return CreateAdmins(user_id=user_id)
#
#
# @values_router.get("/all")
# async def read_values(db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Values))
#     return result.scalars().all()
#
#
# VALID_UPDATE_FIELDS = {"commission", "kg_cost", "change"}
#
#
# @values_router.put("/update_value/{field}")
# async def update_value(value: int,
#                        field: str = Path(..., description="Field to update", in_=["commission", "kg_cost", "change"]),
#                        db: AsyncSession = Depends(get_db)):
#     if field not in VALID_UPDATE_FIELDS:
#         raise HTTPException(status_code=400, detail="Invalid field")
#
#     await db.execute(update(Values).where(Values.id == 1).values({field: value}))
#     await db.commit()
#     result = await db.execute(select(Values))
#     return result.scalar_one()
#
#
# @order_router.post("/create_order")
# async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
#     db_order = Orders(**order.dict())
#     db.add(db_order)
#     try:
#         await db.commit()
#     except IntegrityError:
#         raise HTTPException(status_code=400, detail="Order already exists")
#     await db.refresh(db_order)
#     return db_order
#
#
# @order_router.get('/all')
# async def get_all_orders(db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Orders).where(Orders.in_process == False))
#     return result.scalars().all()
#
#
# @order_router.get('/all_in_process')
# async def get_all_orders(db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Orders).where(Orders.in_process == True))
#     return result.scalars().all()
#
#
# @order_router.put('/accept_order')
# async def accept_order(uuid: UUID, db: AsyncSession = Depends(get_db)):
#     db_order = await db.execute(select(Orders).where(Orders.uuid == uuid))
#     db_order = db_order.scalar_one()
#     db_order.in_process = True
#     await db.commit()
#     return db_order
