from fastapi import FastAPI
from sqlmodel import SQLModel
from app.config.dbsetup import engine
#from .routes import users, attendance

app = FastAPI(title="Smart Attendance System API")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)