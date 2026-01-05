from fastapi import APIRouter, HTTPException, Depends, Request, status
from pydantic import BaseModel
from typing import Optional, List, Annotated
import cv2, subprocess, sys, numpy as np, os, time # psutil
from app.services.face_service import InsightFaceEmbedder, calculate_embeddings_avg, cosine_similarity
from app.config.dbsetup import engine
from app.models.person import PersonCreate
from app.models.embedding import Embedding
from app.models.attendance import AttendanceCreate
from app.cruds.embedding_crud import add_new_emb, get_all_embeddings
from app.cruds.person_crud import create_person, get_person_by_embedding_id, get_all
from app.cruds.attendance_crud import add_attendance
from app.services.auth import get_current_admin
from app.models.administrator import Administrator
from app.config.dbsetup import SessionDep
from pathlib import Path
from app.services.face_service import InsightFaceEmbedder, calculate_embeddings_avg, cosine_similarity
from app.cruds.attendance_crud import get_attendances
from app.models.attendance import  AttendanceDTO


current_admin_dep = Annotated[Administrator, Depends(get_current_admin)] 



router = APIRouter(prefix="/attendance", tags=["attendance"])

embedder: Optional[InsightFaceEmbedder] = None


class EnrollReq(BaseModel):
    first_name: str
    last_name :str

class RecognizeReq(BaseModel):
    image_path :str
    

class RecognizeResp(BaseModel):
    matched: bool
    person_id: Optional[int] = None
    person_name: Optional[str] = None
    score: float

seen_today = set()

@router.get("/records", response_model=List[AttendanceDTO])
def fetch_all_attendances(session : SessionDep, current_user: current_admin_dep) -> List[AttendanceDTO]:
    attendances = get_attendances(session)
    if not attendances:
        raise HTTPException(404, "No attendance recods found")
    return attendances


@router.post("/enroll")
def enroll_face(req: EnrollReq, session: SessionDep, current_user: current_admin_dep):
    global embedder
    print(req.image_path)
    emb = embedder.get_face_embedding_image(req.image_path)
    if emb is None:
        raise HTTPException(status_code=400, detail="Unable to embed face")

    emb = emb.astype(np.float32).tobytes()

    created_emb = add_new_emb(Embedding(vector=emb), session)
    
    person = create_person(
        PersonCreate(first_name=req.first_name, last_name=req.last_name, embedding_id=created_emb),
        session
    )
    if person is None:
        raise HTTPException(status_code=500, detail="Failed to create person")

    

    return {
        "message": "Enrolled",
        "enrolled_embedding_id": created_emb,
        "enrolled person" : req.first_name
    }

@router.post("/recognize_user")
def recognize_user(req : RecognizeReq, session: SessionDep, current_user: current_admin_dep):
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
def enroll_faces(req: EnrollReq, session: SessionDep, current_user: current_admin_dep):
    global embedder
    images = req.image_path
    embs = []
    for i in images:
        emb = embedder.get_face_embedding_image(i)
        embs.append(emb)
    avg_emb = calculate_embeddings_avg(embs)

    avg_emb = avg_emb.astype(np.float32).tobytes()

    created_emb = add_new_emb(Embedding(vector=avg_emb), session)

    person = create_person(
        PersonCreate(first_name=req.first_name, last_name=req.last_name, email=req.email, embedding_id=created_emb),
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


@router.post("/enroll_camera")
def enroll_camera(req : EnrollReq, session: SessionDep, current_user: current_admin_dep):
    global embedder
    if embedder is None:
        raise HTTPException(status_code=503, detail="Vision pipeline not ready")

    out_dir = Path(os.getcwd()) / "enroll_images"
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [sys.executable, "-m", "app.services.enrollment_service", str(out_dir), "0", "15000"]
    try:
       subprocess.run(cmd, capture_output=True, text=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to launch capture helper: {e}")


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

    created_emb = add_new_emb(Embedding(vector=avg), session)

    person = create_person(PersonCreate(first_name=req.first_name, last_name=req.last_name, embedding_id=created_emb),session)

    if person is None:
        raise HTTPException(status_code=500, detail="Failed to create person")

    for p in image_paths: 
        try: p.unlink()
        except: pass

    return {
        "message": "Embeddings created successfully",
    }



@router.post("/take_attendance")
async def take_attendace(request: Request, session: SessionDep, current_user: current_admin_dep):
    global embedder
    if embedder is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vision pipeline not ready",
        )
    try:
        raw_bytes: bytes = await request.body()
        if not raw_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty frame",
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to read request body",
        )
    
    nparr = np.frombuffer(raw_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image data",
        )

    
    THRESHOLD = 0.65
    start_time = time.time()
    embeddings = get_all_embeddings(session)
    if not embeddings:
        return {"No embeddings found in db"}

    faces = embedder.app.get(frame)

    if len(faces) < 1:
        print("no face detected")
        return {"no faces": {}, "attendance": {}}
    if len(faces) > 1:
        print("Warning: Multiple faces detected. Using first detected face")

    results = embedder.find_match(face=faces[0], embeddings=embeddings, session=session, threshold=THRESHOLD)


    created = {}

    if not results[0]["matched"]:
        return {"faces": results, "attendance": []}
    
    person_id = results[0]["person_id"]
    if person_id not in seen_today:
        created = add_attendance(
            AttendanceCreate(person_id=results[0]["person_id"], status_id=1),
            session,
        )
        seen_today.add(person_id)
        print(f"{{score: {results[0]['score']},\n name: {results[0]['first_name']},\n age: {faces[0]['age']},\n gender: {faces[0]['gender']},\n threshold: {THRESHOLD:.2f} }}")
        return {"faces": results, "attendance": created, "created": created}

        

    return {"faces": results, "attendance": {}, "created": created}


@router.get("/absent")
def mark_user_absent(session: SessionDep, current_user: current_admin_dep):
    users = get_all(session)
    absent_users = []
    for user in users:
       if user.person_id not in seen_today:
            absent =  add_attendance(
            AttendanceCreate(person_id=user.person_id, status_id=2),
            session,
            )
            absent_users.append(absent)
    
    return {"attendance": absent_users}

