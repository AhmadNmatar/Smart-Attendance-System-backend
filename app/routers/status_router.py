from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Annotated
from app.config.dbsetup import get_session
from app.crud.status_crud import get_status_id, add_new_status
from app.models.status import Status

status_router = APIRouter(prefix="/status", tags=["Status"])


SessionDep = Annotated[Session, Depends(get_session)]

@status_router.post("/", response_model= Status)
def add_status(status_name : str, session : SessionDep) -> Status:
    new_status = add_new_status(status_name, session)
    if not new_status:
        raise HTTPException(status_code=400, detail="status creation failed")
    return new_status

def fetch_status_id(status_type: str, session : SessionDep) -> int:
    status_id = get_status_id(status_type, session)
    if not status_id:
        raise HTTPException(status_code = 404, detail= "status not found")
    return status_id