from datetime import datetime
from random import randint

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, default=randint(100000000, 900000000))
    name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now())
    sex = Column(String)
    # user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    birthday_date = Column(String)
    address = Column(String)


class Groups(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    direction_1 = Column(String)
    direction_2 = Column(String)
    direction_3 = Column(String)
    address = Column(String)
    okrug = Column(String)
    district = Column(String)
    schedule_active = Column(String)
    schedule_closed = Column(String)
    schedule_planned = Column(String)
    closest_metro = Column(String)
    coordinates_of_address = Column(String)


class UniqueGroups(Base):
    __tablename__ = "uniquegroups"
    id = Column(Integer, primary_key=True, index=True)
    direction_1 = Column(String)
    direction_2 = Column(String)
    direction_3 = Column(String)
    address = Column(String)
    okrug = Column(String)
    district = Column(String)
    schedule_active = Column(String)
    schedule_closed = Column(String)
    schedule_planned = Column(String)
    closest_smetro = Column(String)
    coordinates_of_address = Column(String)
