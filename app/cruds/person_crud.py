from sqlmodel import Session, select
from app.models.person import Person, PersonCreate, PersonPublic

def create_person(person_data: PersonCreate, session: Session) -> PersonPublic | None:
    try:
        db_person = Person.model_validate(person_data)
        session.add(db_person)
        session.commit()
        session.refresh(db_person)
        return PersonPublic.model_validate(db_person)
    except Exception as e:  
        session.rollback()
        return None
    

def get_person_by_pk(id: int, session: Session) -> PersonPublic | None:
    person = session.get(Person, id)
    if not person:
        return None  
    return PersonPublic.model_validate(person)

def get_person_by_embedding_id(embedding_id: int, session: Session) -> PersonPublic | None:
    statement = select(Person).where(Person.embedding_id == embedding_id)
    person = session.exec(statement).first()
    if not person:
        return None  
    return PersonPublic.model_validate(person)

def get_all(session: Session):
    return session.exec(select(Person)).all()