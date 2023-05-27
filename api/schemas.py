import uuid
import re
from typing import List
from pydantic import Field
from pydantic import BaseModel, HttpUrl, validator
from fastapi import HTTPException
from enum import Enum

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class UserCreate(BaseModel):
    name: str
    birthday_date: str

    @validator('name')
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value


class UserShow(BaseModel):
    name: str
    user_id: int
    birthday_date: str


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
