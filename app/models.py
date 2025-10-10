from datetime import date, time, datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


# ======================== Staff =================================
class StaffBase(SQLModel):
    first_name: str
    surname: str

class Staff(StaffBase, table=True):
    staff_id: Optional[int] = Field(default=None, primary_key=True)
    email: Optional[str] = None

    embeddings: Optional["Embedding"] = Relationship(back_populates="staff", uselist=False)
    attendances: List["Attendance"] = Relationship(back_populates="staff")


class StaffPublic(StaffBase):
    email: str

class StaffCreate(StaffBase):
    email: str



# =========================== Embedding ================================


class Embedding(SQLModel, table=True):
    embedding_id: Optional[int] = Field(default=None, primary_key=True)
    staff_id: int = Field(foreign_key="staff.staff_id", unique=True)
    vector: bytes  # encrypted facial embedding

    staff: Optional[Staff] = Relationship(back_populates="embeddings")



# ============================= Status ===============================

class Status(SQLModel, table=True):
    status_id: Optional[int] = Field(default=None, primary_key=True)
    status_type: str  #'present', 'absent'

    attendances: List["Attendance"] = Relationship(back_populates="status")

# ========================= Attendacne ===================================


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
    attendance_id: Optional[int] = Field(default=None, primary_key=True)
    staff_id: int = Field(foreign_key="staff.staff_id")
    status_id: int = Field(foreign_key="status.status_id")

    staff: Optional[Staff] = Relationship(back_populates="attendances")
    status: Optional[Status] = Relationship(back_populates="attendances")

class AttendanceCreat(AttendanceBase):
    staff_id : int 
    status_id : int    


# ================= Adminstrator ==========================

class AdmistratorBase(SQLModel):
    first_name: str
    surname: str
    email: str


class Adminstrator(SQLModel, table=True):
    admin_id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    surname: str
    password_hash: str  # always hashed
    email: str

class AdminstratorDTO(SQLModel):
    first_name: str
    surname: str
    email: str