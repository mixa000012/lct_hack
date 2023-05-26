import uuid
import re

from pydantic import BaseModel, HttpUrl, validator


class Values(BaseModel):
    commission: int
    kg_cost: int
    change: float


class Admins(BaseModel):
    user_id: int


class CreateAdmins(Admins):
    pass


class ValuesCreate(Values):
    pass


class OrderCreate(BaseModel):
    uuid = uuid.UUID
    user_id: int
    type: str
    link: HttpUrl
    size: str | None
    price: int
    raw_price: int
    fio: str
    address: str
    number: str

    @validator('number')
    def validate_phone_number(cls, v):
        if not re.match(r'^\+?1?\d{9,15}$', v):  # Simple regex for validation
            raise ValueError('Invalid phone number')
        return v


class PhoneNumber(BaseModel):
    number: str

    @validator('number')
    def validate_phone_number(cls, v):
        if not re.match(r'^\+?1?\d{9,15}$', v):  # Simple regex for validation
            raise ValueError('Invalid phone number')
        return v


class Url(BaseModel):
    link: HttpUrl
