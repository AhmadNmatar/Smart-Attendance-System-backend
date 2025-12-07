import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.config.dbsetup import engine
from app.routers.admin_router import admin_router
from app.routers.person_router import person_router
from app.routers.status_router import status_router
from app.routers.attendance_router import router as attendance_router
from app.services.face_service import InsightFaceEmbedder
from app.routers import attendance_router as attendance_module
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    attendance_module.embedder = InsightFaceEmbedder()
    try:
        yield
    except asyncio.CancelledError:
        pass
    finally:
       pass


app = FastAPI(title="Smart Attendance System API", lifespan=lifespan)

origins = [ "http://127.0.0.1:5000",
    "http://localhost:5000",]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,          
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(person_router)
app.include_router(status_router)
app.include_router(admin_router)
app.include_router(attendance_router)
