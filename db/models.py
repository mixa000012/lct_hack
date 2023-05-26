from datetime import datetime

import uuid
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String, Float, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now())
    sex = Column(String)
    # user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    birthday_date = Column(String)
    address = Column(String)


class Groups(Base):
    __tablename__ = 'uniquegroups'
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
