from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import Attendance, Status
from app.models import Staff
from app.config.dbsetup import get_session
from typing import Annotated
from datetime import date, time, datetime, timedelta

router = APIRouter(prefix="/attendance", tags=["Attendance"])
SessionDep = Annotated[Session, Depends(get_session)]  # check the use of this
@router.post("/")
def mark_attendance(record: Attendance, session: Session = Depends(get_session)):
    session.add(record)
    session.commit()
    session.refresh(record)
    return record

@router.get("/")
def get_attendance(session: Session = Depends(get_session)):
    return session.exec(select(Attendance)).all()

@router.get("/present/{target_date}")
def get_users_present_on_date(target_date: date, session: SessionDep):
    """
    Return all users who were marked 'Present' on the given date.
    """
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = start_datetime + timedelta(days=1)

    statement = (
        select(Staff)
        .join(Attendance)
        .join(Status)
        .where(
            Attendance.timestamp >= start_datetime,
            Attendance.timestamp < end_datetime,
            Status.status_type == "Present"
        )
    )

    users = session.exec(statement).all()

    if not users:
        raise HTTPException(status_code=404, detail="No users found for that date")

    return users