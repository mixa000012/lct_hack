from datetime import datetime

from pydantic.main import BaseModel


class Attend(BaseModel):
    id: int
    group_id: int
    user_id: int
    direction_2: str
    direction_3: str
    Offline: bool
    date: datetime
    start: str
    end: str
    metro: str
    address: str


class AttendCreate(Attend):
    pass


class AttendUpdate(BaseModel):
    pass
