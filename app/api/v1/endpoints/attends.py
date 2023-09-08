from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.attends import service
from app.attends.service import AttendAlreadyExists
from app.attends.service import AttendsDoesntExist
from app.attends.service import WrondUser
from app.core.deps import get_db
from app.user.auth import get_current_user_from_token
from app.user.schema import User

attends_router = APIRouter()


# todo Проблемы с отображение
@attends_router.post("/attends")
async def create_attend(
    group_id: int,
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    try:
        attend = await service.create_attend(group_id, current_user, db)
    except AttendAlreadyExists:
        raise HTTPException(status_code=409, detail="Attend already exist")
    return attend


@attends_router.delete("/attends/{id}")
async def delete_attends(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    try:
        attend = await service.delete_attends(id, db, current_user)
    except AttendsDoesntExist:
        raise HTTPException(status_code=404, detail="Attends not found")
    except WrondUser:
        raise HTTPException(
            status_code=409, detail="You are not the owner of the attend!"
        )
    return {"detail": attend}


@attends_router.get("/attends")
async def get_attends_by_id(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
):
    try:
        attends = await service.get_attends_by_id(current_user, db)
    except AttendsDoesntExist:
        raise HTTPException(status_code=404, detail="Attends not found")
    return attends
