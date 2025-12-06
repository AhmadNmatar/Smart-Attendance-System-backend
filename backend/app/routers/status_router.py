from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Annotated
from app.config.dbsetup import get_session, SessionDep
from app.cruds.status_crud import get_status_id, add_new_status
from app.models.status import Status
from app.services.auth import get_current_admin
from app.models.administrator import Administrator

status_router = APIRouter(prefix="/status", tags=["Status"])


current_admin_dep = Annotated[Administrator, Depends(get_current_admin)]

@status_router.post("/", response_model= Status)
def add_status(status_name : str, session : SessionDep, current_user:current_admin_dep) -> Status:
    new_status = add_new_status(status_name, session)
    if not new_status:
        raise HTTPException(status_code=400, detail="status creation failed")
    return new_status

