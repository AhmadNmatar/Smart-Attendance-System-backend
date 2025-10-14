from datetime import date, time, datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship




class AdministratorBase(SQLModel):
    first_name: str
    surname: str
    email: str


class Administrator(SQLModel, table=True):
    admin_id: int | None = Field(default=None, primary_key=True)
    first_name: str
    surname: str
    password_hash: str  # always hashed
    email: str = Field(index=True)

class AdministratorDTO(SQLModel):
    first_name: str
    surname: str
    email: str
