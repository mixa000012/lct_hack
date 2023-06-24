from app.core.db.CRUD import ModelAccessor
from app.groups.model import Groups
from app.groups.schema import GroupCreate, GroupUpdate


class GroupAccessor(ModelAccessor[Groups, GroupCreate, GroupUpdate]):
    pass


group = GroupAccessor(Groups)
