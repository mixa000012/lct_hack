import re
from enum import Enum
from typing import List

from pydantic import BaseModel
from pydantic import Field

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TokenData(BaseModel):
    access_token: str
    token_type: str


class UserUpdateData(BaseModel):
    sex: str | None
    address: str | None
    survey_result: str | None


class UserCreate(BaseModel):
    name: str | int
    birthday_date: str


class UserShow(BaseModel):
    name: str
    user_id: str
    birthday_date: str


class UserShowAddress(UserShow):
    sex: str
    address: str
    created_at: str
    survey_result: str


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


class Group(GroupInDB):
    timeToWalk: int = Field(...)


class AttendShow(BaseModel):
    id: int
    group_id: int
    user_id: int
    direction_2: str
    direction_3: str
    Offline: bool
    date: str
    start: str
    end: str
    metro: str
    address: str
