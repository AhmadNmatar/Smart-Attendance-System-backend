from sqlmodel import Session, select
from app.models.status import Status


def get_status_id(status : str, session : Session) -> int | None:
    statement = select(Status).where(Status.status_type == status)
    status = session.exec(statement).first()
    if not status:
        return None
    return status.status_id

def add_new_status(status: str, session: Session) -> Status | None:
    try:
        new_status = Status(status_type=status)
        session.add(new_status)
        session.commit()
        session.refresh(new_status)
        return new_status
    except Exception:
        session.rollback()
        return None