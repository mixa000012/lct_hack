from datetime import datetime
from random import randint
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from app.core.db.base_class import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, default=randint(100000000, 900000000))
    name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now())
    sex = Column(String)
    # user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    birthday_date = Column(String)
    address = Column(String)
    survey_result = Column(String)
    ml_result = Column(String)
