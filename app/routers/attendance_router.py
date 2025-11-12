from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Annotated, Optional
from app.config.dbsetup import SessionDep
from app.cruds.attendance_crud import get_attendances
from app.models.attendance import  AttendanceDTO
from app.utils.auth import get_current_admin
from app.models.administrator import Administrator

current_admin_dep = Annotated[Administrator, Depends(get_current_admin)] 
attendance_router = APIRouter(prefix="/attendance", tags=["Attendance"])


@attendance_router.get("/records", response_model=List[AttendanceDTO])
def fetch_all_attendances(session : SessionDep, current_user: current_admin_dep) -> List[AttendanceDTO]:
    attendances = get_attendances(session)
    if not attendances:
        raise HTTPException(404, "No attendance recods found")
    return attendances


 

