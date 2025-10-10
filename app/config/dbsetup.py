from sqlmodel import SQLModel, create_engine, Session

from dotenv import load_dotenv
from fastapi import Depends
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session


