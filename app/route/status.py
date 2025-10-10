from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Annotated
from app.config.dbsetup import get_session
from app.models import Status

router = APIRouter(prefix="/attendance", tags=["Attendance"])

SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/")
def add_status(status : Status, session: Session = Depends(get_session)):
    session.add(status)
    session.commit()
    session.refresh(status)
    return status

@router.get("/")
def get_status( session: Session = Depends(get_session)):
   return session.exec(select(Status)).all()

