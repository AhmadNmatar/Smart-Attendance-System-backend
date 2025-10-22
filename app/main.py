from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.config.dbsetup import engine
from app.routers.admin_router import admin_router
from app.routers.person_router import person_router
from app.routers.status_router import status_router
from app.models.administrator import Administrator
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
app.include_router(status_router)
app.include_router(admin_router)

