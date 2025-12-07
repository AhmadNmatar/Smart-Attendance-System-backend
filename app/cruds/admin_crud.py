from typing import Optional
from sqlmodel import Session, select
from app.models.administrator import Administrator, AdministratorPublic, AdministratorCreate
from app.services.password_utils import get_password_hash, verify_password


def get_admin_by_email(email:str, session :Session) -> Optional[Administrator]:
    statement = select(Administrator).where(Administrator.email == email)
    result = session.exec(statement).first()
    if not result:
        return None
    return Administrator.model_validate(result)

def verify_admin(email: str, entered_password: str, session: Session) -> Optional[AdministratorPublic]:
    admin = get_admin_by_email(email, session)
    if not admin:
        return None

    stored_hash = admin.password
    if verify_password(entered_password, stored_hash):
        return AdministratorPublic.model_validate(admin)
    else:
        raise ValueError("Password is not correct")
    

def create_new_admin(admin: AdministratorCreate, session: Session) -> Optional[AdministratorPublic]:
    try:
      
        new_admin = Administrator(**admin.model_dump())
        session.add(new_admin)
        session.commit()
        session.refresh(new_admin)
        return AdministratorPublic.model_validate(new_admin)
    except Exception:
        session.rollback()
        return None