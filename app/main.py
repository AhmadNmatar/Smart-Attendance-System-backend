from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.config.dbsetup import engine
from app.route.person_router import person_router
from app.models.admintrator import Administrator
from app.models.person import Person
from app.models.embedding import Embedding
from app.models.attendance import Attendance
from app.models.status import Status

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title="Smart Attendance System API", lifespan=lifespan)

app.include_router(person_router)

