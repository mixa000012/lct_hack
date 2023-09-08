from pydantic.main import BaseModel


class Attend(BaseModel):
    group_id: int
    user_id: int
    direction_2: str
    direction_3: str
    offline: bool
    start: str
    end: str
    metro: str
    address: str


class AttendCreate(Attend):
    pass


class AttendUpdate(BaseModel):
    pass
