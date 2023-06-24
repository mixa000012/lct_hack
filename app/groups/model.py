from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from app.core.db.base_class import Base


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
    around_metros = Column(String)
    description = Column(String)
