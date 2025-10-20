from ast import List
from datetime import date, datetime, time, timedelta
from fastapi import HTTPException
from pyparsing import Optional
from sqlmodel import Session, select
from app.models.attendance import Attendance, AttendanceCreate, AttendanceDTO
from app.models.person import Person
from app.models.status import Status
from sqlalchemy.orm import selectinload

def get_attendances(session: Session) -> list[AttendanceDTO] | None:
    statement = (
        select(Attendance)
        .options(selectinload(Attendance.Person), selectinload(Attendance.status))
    )

    attendances = session.exec(statement).all()

    if not attendances:
        return None

    return [
        AttendanceDTO(
            attendance_id=a.attendance_id,
            date=a.date,
            time=a.time,
            first_name=a.Person.first_name,
            surname=a.Person.surname,
            email=a.Person.email,
            status_type=a.status.status_type
        )
        for a in attendances
    ]


# method to get all users present on given date
def get_attendances_present_between(session: Session, start_date: date, end_date: date) -> Optional[list[AttendanceDTO]]:
    statement = (
        select(Attendance)
        .where(
            Attendance.date >= start_date,
            Attendance.date < end_date
        )
        .options(
            selectinload(Attendance.Person),
            selectinload(Attendance.status) 
        )
    )

    attendances = session.exec(statement).all()

    present_attendances = [
        a for a in attendances
        if a.status and a.status.status_type.lower() == "present"
    ]

    if not present_attendances:
        return None

    return [ AttendanceDTO(
            attendance_id=a.attendance_id,
            date=a.date,
            time=a.time,
            first_name=a.Person.first_name,
            surname=a.Person.surname,
            email=a.Person.email,
            status_type=a.status.status_type
            )
        for a in present_attendances
    ]

def get_attendance_by_pk(id: int, session: Session) -> Optional[AttendanceDTO]:
    statement = (
        select(Attendance)
        .where(Attendance.attendance_id == id)
        .options(
            selectinload(Attendance.person),
            selectinload(Attendance.status)
        )
    )
    result = session.exec(statement).first()
    if not result:
        return None

    return AttendanceDTO(
        attendance_id=result.attendance_id,
        date=result.date,
        time=result.time,
        first_name=result.person.first_name,
        surname=result.person.surname,
        email=result.person.email,
        status_type=result.status.status_type
    )

  
def mark_attendance(attendance: AttendanceCreate, session: Session) -> Optional[AttendanceDTO]:
    try:
        db_attendance = Attendance.model_validate(attendance)  
        session.add(db_attendance)
        session.commit()
        session.refresh(db_attendance)

        return get_attendance_by_pk(db_attendance.attendance_id, session)

    except Exception:
        session.rollback()
        return None

