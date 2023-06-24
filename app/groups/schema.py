from enum import Enum
from typing import List

from pydantic import Field
from pydantic.main import BaseModel


class GroupType(str, Enum):
    Game = "Game"
    Education = "Education"
    Singing = "Singing"
    Painting = "Painting"
    Intellectual = "Intellectual"
    Theatre = "Theatre"
    SilverUni = "SilverUni"
    Trainings = "Trainings"
    Dancing = "Dancing"
    Creativity = "Creativity"
    Physical = "Physical"


class GroupInDB(BaseModel):
    id: int
    name: str
    type: GroupType | str
    address: str
    metro: str | None
    time: List[str] | str
    description: str

    class Config:
        orm_mode = True


class Group(GroupInDB):
    timeToWalk: int = Field(...)


class GroupCreate(BaseModel):
    pass


class GroupUpdate(BaseModel):
    pass


# class UserBase(BaseModel):
#     name: str | int
#     birthday_date: str
#
#
# class UserCreate(UserBase):
#     pass
#
#
# class Sex(str, Enum):
#     male = "Мужчина"
#     female = "Женщина"
#
#
# class UserUpdateData(BaseModel):
#     sex: Sex | None
#     address: str | None
#     survey_result: str | None
#
#
# class UserInDBBase(UserBase):
#     id: int | None = None
#     sex: Sex | None
#     address: str | None
#     survey_result: str | None
#
#     class Config:
#         orm_mode = True
#
#
# class User(UserInDBBase):
#     class Config:
#         fields = {}
#
#
# class UserShow(UserBase):
#     user_id: str
#
#
# class UserShowAddress(UserBase):
#     created_at: str
