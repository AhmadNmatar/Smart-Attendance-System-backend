from datetime import timedelta
import os
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.config.dbsetup import get_session, SessionDep
from app.models.administrator import AdministratorCreate, AdministratorPublic, Administrator, TokenResponse
from app.cruds.admin_crud import verify_admin, create_new_admin, get_admin_by_email
from app.services.auth import auth_dep, get_current_admin, create_access_token
from app.services.password_utils import get_password_hash

admin_router = APIRouter(prefix="/admin", tags=["Admin"])
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


@admin_router.post("/signup", response_model=AdministratorPublic)
def signup_admin(admin: AdministratorCreate, session: SessionDep):
    existing = get_admin_by_email(admin.email, session)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin already exists")
    admin.password = get_password_hash(admin.password)
    new_admin = create_new_admin(admin, session)
    if new_admin is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="failed to create")
    return new_admin


@admin_router.post("/login", response_model=TokenResponse)
def login(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        admin = verify_admin(form_data.username, form_data.password, session)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if admin is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": admin.email}, expires_delta=access_token_expires
    )
    return TokenResponse(access_token=access_token, token_type="bearer", admin=admin)
