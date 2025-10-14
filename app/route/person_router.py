from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Annotated
from app.config.dbsetup import get_session
from app.crud.person_crud import create_person, get_person_by_pk
from app.models.person import PersonPublic, PersonCreate


person_router = APIRouter(prefix="/person", tags=["Person"])


SessionDep = Annotated[Session, Depends(get_session)]

@person_router.post("/", response_model=PersonPublic)
def create_new_person(person: PersonCreate, session: SessionDep)-> PersonPublic:
    result = create_person(person, session)
    if result is None:
        raise HTTPException(status_code=400, detail="Person creation failed")
    return result

@person_router.get("/", response_model=PersonPublic)
def get_person_by_id(id: int, session: SessionDep) -> PersonPublic:
    person = get_person_by_pk(id, session)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person
