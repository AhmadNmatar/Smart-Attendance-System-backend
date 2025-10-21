from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.config.dbsetup import get_session
from app.models.admintrator import AdministratorCreate, AdministratorPublic, Administrator
from app.crud.admin_crud import verify_admin, create_new_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

SessionDep = Annotated[Session, Depends(get_session)]
@router.post("/signup", response_model=AdministratorPublic)
def signup_admin(admin: AdministratorCreate, session: SessionDep):
    res = Administrator.model_validate(admin)
    existing = verify_admin(res.email, res.password, session)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin already exists")

    new_admin = create_new_admin(admin, session)
    if not new_admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="failed to create")
    return new_admin


@router.post("/login", response_model=AdministratorPublic)
def login_admin(email: str, password: str, session: SessionDep):
    admin = verify_admin(email, password, session)
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return admin
