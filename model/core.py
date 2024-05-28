from sqlalchemy import Column, Integer
from sqlalchemy.types import DateTime

from .database import Base

import datetime


class Timestamp(Base):
    __tablename__ = 'timestamps'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
