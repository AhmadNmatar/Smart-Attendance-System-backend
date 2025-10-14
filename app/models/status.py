
from typing import List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel

class Status(SQLModel, table=True):
    status_id: int | None = Field(default=None, primary_key=True)
    status_type: str  #'present', 'absent'

    attendances: List["Attendance"] = Relationship(back_populates="status")