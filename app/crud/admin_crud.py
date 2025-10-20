from typing import Optional
from sqlmodel import Session, select
from app.models.admintrator import Administrator, AdministratorPublic, AdministratorCreate
import bcrypt


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
    entered_bytes = entered_password.encode("utf-8")
    stored_bytes = stored_hash.encode("utf-8")

    if bcrypt.checkpw(entered_bytes, stored_bytes):
        return AdministratorPublic.model_validate(admin)
    else:
        raise ValueError("Password is not correct")
    

def create_admin(admin: AdministratorCreate, session: Session) -> Optional[AdministratorPublic]:
    try:
        password_bytes = admin.password.encode("utf-8")
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

        new_admin = Administrator(
            first_name=admin.first_name,
            surname=admin.surname,
            email=admin.email,
            password=hashed_password
        )

        session.add(new_admin)
        session.commit()
        session.refresh(new_admin)
        return AdministratorPublic.model_validate(new_admin)
    except Exception:
        session.rollback()
        return None