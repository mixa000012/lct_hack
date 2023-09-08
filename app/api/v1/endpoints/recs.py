import ast

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import store
from app.core.deps import get_db
from app.user.auth import get_current_user_from_token
from app.user.model import User
from geocoding.get_coords import get_metro
from ml.new_users import get_new_resc

# from ml.script import get_final_groups
# from ml.script import get_recs

recs_router = APIRouter()


@recs_router.get("/")
async def give_recs(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db),
    is_new: bool = False,
) -> list[int]:
    if current_user.ml_result:
        result = current_user.ml_result
        return ast.literal_eval(result)

    if is_new or current_user.survey_result:
        if current_user.survey_result is None:
            raise HTTPException(status_code=400, detail="No survey results")
        now_interests = ast.literal_eval(current_user.survey_result)
        metro = get_metro(current_user.address)
        if metro == "далековато":
            metro = "Ленинский проспект"

        result = get_new_resc(
            now_interests, current_user.sex, current_user.birthday_date
        )
        result = await get_final_groups(chat_id=int(result), metro_human=metro)  # noqa
    else:
        result = await get_recs(int(current_user.id), N=12, new_user=False)  # noqa

    await store.recs.update(
        db=db, db_obj=current_user, obj_in={"ml_result": str(result)}
    )

    return result


@recs_router.get("/is_recs_exist")
async def is_recs_exist(
    current_user: User = Depends(get_current_user_from_token),
) -> bool:
    if current_user.survey_result:
        return True
    try:
        await get_recs(int(current_user.id), N=10, new_user=False)  # noqa
        return True
    except KeyError:
        return False
