from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Annotated
from app.config.dbsetup import get_session
from app.models import Status, Attendance
from app.models import Embedding, Staff


router = APIRouter(prefix="/admin", tags=["Admin"])


SessionDep = Annotated[Session, Depends(get_session)]