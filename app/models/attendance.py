from datetime import date, time, datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel

class AttendanceDTO(SQLModel):
    attendance_id: int
    date: date
    time: time
    first_name: str
    surname: str
    email: str
    status_type: str


class AttendanceBase(SQLModel):
    date: date
    time: time

class Attendance(SQLModel, table=True):
    attendance_id: int | None = Field(default=None, primary_key=True)
    person_id: int = Field(foreign_key="person.person_id")
    status_id: int = Field(foreign_key="status.status_id")

    Person: Optional["Person"] = Relationship(back_populates="attendances")
    status: Optional["Status"] = Relationship(back_populates="attendances")

class AttendanceCreate(AttendanceBase):
    person_id: int
    status_id: int