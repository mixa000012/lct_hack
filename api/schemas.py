import re
from enum import Enum
from typing import List

from pydantic import BaseModel
from pydantic import Field

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TokenData(BaseModel):
    access_token: str
    token_type: str






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
