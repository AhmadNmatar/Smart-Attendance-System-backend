from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Annotated
from app.config.dbsetup import get_session
from app.models import Embedding, Staff
from app.models import Status, Attendance


router = APIRouter(prefix="/embedding", tags=["Embedding"])


SessionDep = Annotated[Session, Depends(get_session)]