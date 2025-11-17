from sqlmodel import SQLModel, create_engine, Session
from typing import Annotated
from dotenv import load_dotenv
from fastapi import Depends
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]