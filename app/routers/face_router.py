from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List, Tuple, Annotated
import numpy as np
import asyncio
import cv2
import subprocess, sys
from datetime import date, datetime
from sqlmodel import Session, select
from app.services.camera_servic import Camera
from app.services.face_service import InsightFaceEmbedder, calculate_embeddings_avg, cosine_similarity
from app.config.dbsetup import engine
from app.models.person import Person, PersonCreate
from app.models.embedding import Embedding
from app.models.attendance import AttendanceCreate
from app.cruds.embedding_crud import add_new_emb, get_all
from app.cruds.person_crud import create_person, get_person_by_embedding_id
from app.cruds.attendance_crud import add_attendance
from app.utils.auth import get_current_admin
from app.models.administrator import Administrator
from app.config.dbsetup import SessionDep
from pathlib import Path


current_admin_dep = Annotated[Administrator, Depends(get_current_admin)] 



router = APIRouter(prefix="/face", tags=["face"])

# --- app-scoped singletons (set on startup in main.py) ---
camera: Optional[Camera] = None
embedder: Optional[InsightFaceEmbedder] = None


class EnrollReq(BaseModel):
    first_name: str
    last_name :str
   # image_path: List[str]

class RecognizeReq(BaseModel):
    image_path :str
    

class RecognizeResp(BaseModel):
    matched: bool
    person_id: Optional[int] = None
    person_name: Optional[str] = None
    score: float


@router.post("/enroll")
def enroll_face(req: EnrollReq, session: SessionDep):
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
def recognize_faces(req : RecognizeReq, session: SessionDep):
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
def enroll_faces(req: EnrollReq, session: SessionDep):
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
async def recognize_realtime(websocket: WebSocket, session: SessionDep): 
    global embedder, camera
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
            person_id = results[0]['person_id']
            added_attendence = add_attendance(AttendanceCreate(person_id=person_id, status_id=1), session)


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


############## enroll via camera ##########



@router.post("/enroll_camera")
def enroll_camera(req : EnrollReq, session: SessionDep):
    global embedder
    if embedder is None:
        raise HTTPException(status_code=503, detail="Vision pipeline not ready")

    out_dir = Path("/tmp/enroll_images")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) Launch helper process that owns the GUI window and saves 5 frames
    cmd = [sys.executable, "-m", "app.services.enrollment_camera", str(out_dir), "0", "15000"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to launch capture helper: {e}")

    if result.returncode == 2:
        raise HTTPException(status_code=500, detail=f"Cannot open camera. {result.stderr or result.stdout}")
    if result.returncode == 3:
        raise HTTPException(status_code=400, detail=f"No frames saved (cancelled or timeout). {result.stderr or result.stdout}")
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Capture failed (code {result.returncode}). {result.stderr or result.stdout}")

    # 2) For each saved image, compute an embedding
    image_paths = sorted(out_dir.glob("*.png"))
    if not image_paths:
        raise HTTPException(status_code=500, detail="No images found after capture")

    embs = []

    for p in image_paths:
        emb = embedder.get_face_embedding_image(str(p))
        embs.append(emb)

    avg_emb = calculate_embeddings_avg(embs)
    if not embs:
        raise HTTPException(status_code=400, detail="No face embeddings could be computed from captured images")

    avg = avg_emb.astype(np.float32).tobytes()

     # --- create person, then embedding linked to that person ---
    created_emb = add_new_emb(Embedding(vector=avg), session)

    person = create_person(PersonCreate(first_name=req.first_name, surname=req.last_name, embedding_id=created_emb),session)

    if person is None:
        raise HTTPException(status_code=500, detail="Failed to create person")

    #print(person.person_id)
    for p in image_paths: 
        try: p.unlink()
        except: pass

    return {
        "message": "Embeddings created successfully",
        "num_embeddings": len(embs),        # images where no face was found or read failed
        "mean_embedding": avg_emb.tolist()   # 512-d average (handy for saving as the enrolled template)
    }