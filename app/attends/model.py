from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from app.core.db.base_class import Base


class Attends(Base):
    __tablename__ = "attends"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer)
    user_id = Column(Integer)
    direction_2 = Column(String)
    direction_3 = Column(String)
    Offline = Column(Boolean)
    date = Column(DateTime)
    start = Column(String)
    end = Column(String)
    metro = Column(String)
    address = Column(String)
