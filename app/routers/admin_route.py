from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.config.dbsetup import get_session
from app.models.admintrator import AdministratorCreate, AdministratorPublic
from app.crud import admin as crud_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

SessionDep = Annotated[Session, Depends(get_session)]
@router.post("/signup", response_model=AdministratorPublic)
def signup_admin(admin: AdministratorCreate, session: SessionDep):
    existing = crud_admin.verify_admin(admin.email, admin.password, session)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin already exists")

    new_admin = crud_admin.create_admin(admin, session)
    return new_admin


@router.post("/login", response_model=AdministratorPublic)
def login_admin(email: str, password: str, session: SessionDep):
    admin = crud_admin.verify_admin(email, password, session)
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return admin
