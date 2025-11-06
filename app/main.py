import asyncio
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
from app.routers.face_router import router as face_router
from app.services.camera_servic import Camera
from app.services.face_service import InsightFaceEmbedder
from app.routers import face_router as face_module


@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB
    SQLModel.metadata.create_all(engine)
    # Vision init
    face_module.camera = Camera(index=0)
    face_module.embedder = InsightFaceEmbedder()
    try:
        yield
    except asyncio.CancelledError:
        # Suppress CancelledError during shutdown
        pass
    finally:
        # cleanup
        if face_module.camera:
            face_module.camera.release()


app = FastAPI(title="Smart Attendance System API", lifespan=lifespan)

app.include_router(person_router)
app.include_router(status_router)
app.include_router(admin_router)
app.include_router(face_router)
