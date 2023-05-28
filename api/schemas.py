import re
from enum import Enum
from typing import List

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TokenData(BaseModel):
    access_token: str
    token_type: str


class UserUpdateData(BaseModel):
    sex: str | None
    address: str | None


class UserCreate(BaseModel):
    name: str
    birthday_date: str

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value


class UserShow(BaseModel):
    name: str
    user_id: str
    birthday_date: str


class UserShowAddress(UserShow):
    sex: str
    address: str
    created_at: str


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
    tags: List[str]
    address: str
    metro: str | None
    time: List[str] | str


class Group(GroupInDB):
    timeToWalk: int = Field(...)
