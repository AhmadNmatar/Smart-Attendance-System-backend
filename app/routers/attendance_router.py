from ast import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Annotated, Optional
from app.config.dbsetup import get_session, SessionDep
from app.cruds.attendance_crud import get_attendances, get_attendance_by_pk, get_attendances_present_between, add_attendance
from app.models.attendance import Attendance, AttendanceCreate, AttendanceDTO



attendance_router = APIRouter(prefix="/attendance", tags=["Attendance"])

@attendance_router.get("/", response_model=AttendanceDTO)
def fetch_all_attendances(session : SessionDep) -> Optional[AttendanceDTO]:
    attendances = get_attendances(session)
    if not attendances:
        raise HTTPException(404, "No attendance recods found")
    return attendances


 

