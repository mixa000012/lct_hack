from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path
import openrouteservice
import ast

from openrouteservice.distance_matrix import distance_matrix

from db.session import get_db

order_router = APIRouter()

values_router = APIRouter()

routes_router = APIRouter()

client = openrouteservice.Client(
    key='5b3ce3597851110001cf6248d849a8330bbd463fb95a896f83abd13f')  # Specify your personal API key


@routes_router.post('/get_time')
async def get_time(coordinates: str) -> dict:
    coordinates = ast.literal_eval(coordinates)
    routes = distance_matrix(client, coordinates, profile='foot-walking')
    return routes

#
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
