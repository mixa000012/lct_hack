import uuid
import re

from pydantic import BaseModel, HttpUrl, validator
from fastapi import HTTPException

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
    user_id: uuid.UUID
    birthday_date: str
