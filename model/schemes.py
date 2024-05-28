from pydantic import BaseModel
from datetime import datetime


class TimestampBase(BaseModel):
    timestamp: datetime

    class Config:
        from_attributes = True


class Timestamp(TimestampBase):
    id: int
