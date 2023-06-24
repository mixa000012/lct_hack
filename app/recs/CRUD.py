from app.core.db.CRUD import ModelAccessor
from app.groups.model import Groups
from app.user.schema import UserCreate
from app.user.schema import UserUpdateData


class RecsAccessor(ModelAccessor[Groups, UserCreate, UserUpdateData]):
    pass


recs = RecsAccessor(Groups)
