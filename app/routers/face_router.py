from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List, Tuple
import numpy as np
import cv2
import time
import json
import asyncio
from sqlmodel import Session, select
from app.services.camera_servic import Camera
from app.services.face_service import InsightFaceEmbedder, calculate_embeddings_avg, cosine_similarity
from app.config.dbsetup import engine
from app.models.person import Person, PersonCreate
from app.models.embedding import Embedding
from app.models.attendance import Attendance
from app.cruds.embedding_crud import add_new_emb, get_all
from app.cruds.person_crud import create_person, get_person_by_embedding_id


router = APIRouter(prefix="/face", tags=["face"])

# --- app-scoped singletons (set on startup in main.py) ---
camera: Optional[Camera] = None
embedder: Optional[InsightFaceEmbedder] = None

def get_session():
    with Session(engine) as session:
        yield session

class EnrollReq(BaseModel):
    first_name: str
    last_name :str
    email: str
    image_path: List[str]

class RecognizeReq(BaseModel):
    image_path :str
    

class RecognizeResp(BaseModel):
    matched: bool
    person_id: Optional[int] = None
    person_name: Optional[str] = None
    score: float


@router.post("/enroll")
def enroll_face(req: EnrollReq, session: Session = Depends(get_session)):
    global embedder
    emb = embedder.get_face_embedding_image(req.image_path)
    if emb is None:
        raise HTTPException(status_code=400, detail="Unable to embed face")

    emb = emb.astype(np.float32).tobytes()

    # --- create person, then embedding linked to that person ---
    created_emb = add_new_emb(Embedding(vector=emb), session)

    person = create_person(
        PersonCreate(first_name=req.first_name, surname=req.last_name, email=req.email, embedding_id=created_emb),
        session
    )

    if person is None:
        raise HTTPException(status_code=500, detail="Failed to create person")

    print(person.person_id)

    return {
        "message": "Enrolled",
        "enrolled_embedding_id": created_emb,
        "enrolled person" : req.first_name
    }

@router.post("/recognize_image")
def recognize_faces(req : RecognizeReq, session: Session = Depends(get_session)):
    global embedder

    emb = embedder.get_face_embedding_image(req.image_path)
    
    if emb is None:
        raise HTTPException(status_code=400, detail="Unable to embed face")
    embeddings = get_all(session)
    if not embeddings:
        return {"name": None, "score": -1.0, "matched": False}
    matched_emb = None
    best_score = 0.0
    for e in embeddings:
        ref_emb = np.frombuffer(e.vector, dtype=np.float32)
        
        similarity, is_match = cosine_similarity(emb, ref_emb)
        
        if similarity > best_score:
            best_score = similarity
            matched_emb = e.embedding_id
    
    person = get_person_by_embedding_id(matched_emb, session)
    is_match = best_score > 0.65

    return {"name" : person.first_name, "score" : float(best_score), "matched" : bool(is_match)}


@router.post("/enroll_images")
def enroll_faces(req: EnrollReq, session: Session = Depends(get_session)):
    global embedder
    images = req.image_path
    embs = []
    for i in images:
        emb = embedder.get_face_embedding_image(i)
        embs.append(emb)
    avg_emb = calculate_embeddings_avg(embs)

    avg_emb = avg_emb.astype(np.float32).tobytes()

     # --- create person, then embedding linked to that person ---
    created_emb = add_new_emb(Embedding(vector=avg_emb), session)

    person = create_person(
        PersonCreate(first_name=req.first_name, surname=req.last_name, email=req.email, embedding_id=created_emb),
        session
    )

    if person is None:
        raise HTTPException(status_code=500, detail="Failed to create person")

    print(person.person_id)

    return {
        "message": "Enrolled",
        "enrolled_embedding_id": created_emb,
        "enrolled person" : req.first_name
    }





@router.websocket("/recognize_realtime")
async def recognize_realtime(websocket: WebSocket, session: Session = Depends(get_session)): 
    global camera, embedder 
    await websocket.accept() 
    try: 
        if camera is None or embedder is None: 
            await websocket.send_json({"error": "Vision pipeline not ready"}) 
            await websocket.close() 
            return 

        embeddings = get_all(session) 
        if not embeddings: 
            await websocket.send_json({"error": "No embeddings found"}) 
            await websocket.close() 
            return 
        while True: 
            frame = camera.get_frame() 
            if frame is None: 
                await asyncio.sleep(0.1) # Wait a bit if no frame continue 

            # Detect faces
            #rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = embedder.app.get(frame) 
            
            if not faces:
                await websocket.send_json({"faces": []}) 
                await asyncio.sleep(0.1) 
                continue 

            results = embedder.real_time_recognition(faces, embeddings, session, 0.65)
            await websocket.send_json({"faces": results}) 
            await asyncio.sleep(0.1) 
                     # Control frame rate 
    except WebSocketDisconnect: 
        pass 
    except Exception as e: 
        try: 
            await websocket.send_json({"error": str(e)}) 
        except: 
            pass 
        finally: 
            try: 
                await websocket.close() 
            except: 
                pass