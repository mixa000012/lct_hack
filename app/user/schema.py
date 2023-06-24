from enum import Enum

from pydantic.main import BaseModel


class UserBase(BaseModel):
    name: str | int
    birthday_date: str


class UserCreate(UserBase):
    pass


class Sex(str, Enum):
    male = "Мужчина"
    female = "Женщина"


class UserUpdateData(BaseModel):
    sex: Sex | None
    address: str | None
    survey_result: str | None


class UserInDBBase(UserBase):
    id: int | None = None
    sex: Sex | None
    address: str | None
    survey_result: str | None

    class Config:
        orm_mode = True


class User(UserInDBBase):
    class Config:
        fields = {}


class UserShow(UserBase):
    user_id: str


class UserShowAddress(UserBase):
    created_at: str
