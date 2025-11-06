   

 # Open camera preview window

"""
    cap = cv2.VideoCapture(0)  # Assuming camera index 0, adjust if needed
    if not cap.isOpened():
        raise HTTPException(status_code=503, detail="Cannot open camera for preview")

    print("Camera preview opened. Press SPACE to capture, ESC to cancel.")

    captured_frame = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Enrollment Preview - Press SPACE to capture, ESC to cancel", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 32:  # SPACE key
            captured_frame = frame.copy()
            break
        elif key == 27:  # ESC key
            break

    cap.release()
    cv2.destroyAllWindows()

    if captured_frame is None:
        raise HTTPException(status_code=400, detail="Capture cancelled or failed")

    frame = captured_frame
"""

#################################################
"""
haar = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def detect_faces_haar(bgr_img: np.ndarray) -> List[Tuple[int,int,int,int]]:
    gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
    faces = haar.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
    return [(x, y, w, h) for (x, y, w, h) in faces]

def crop_face(bgr_img: np.ndarray, box: Tuple[int,int,int,int], expand: float = 0.15) -> np.ndarray:
    h, w = bgr_img.shape[:2]
    x, y, bw, bh = box
    cx, cy = x + bw/2, y + bh/2
    side = int(max(bw, bh) * (1 + expand))
    nx = int(max(0, cx - side/2))
    ny = int(max(0, cy - side/2))
    ex = int(min(w, nx + side))
    ey = int(min(h, ny + side))
    return bgr_img[ny:ey, nx:ex]
"""
######## from enroll func ############
"""    data = np.frombuffer(file.file.read(), np.uint8)
    frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="Cannot decode image")
    boxes = detect_faces_haar(frame)
    if not boxes:
        raise HTTPException(status_code=400, detail="No face detected")
    x, y, w, h = max(boxes, key=lambda b: b[2]*b[3])
    crop = crop_face(frame, (x, y, w, h))
"""
######### from real time recog in face router:
"""

            # Detect faces
            faces = embedder.app.get(frame)
            if not faces:
                await websocket.send_json({"faces": []})
                await asyncio.sleep(0.1)
                continue

            results = []
            for face in faces:
                emb = face.embedding
                if emb is None:
                    continue

                # Compare against all stored embeddings
                best_score = 0.0
                best_person = None
                for e in embeddings:
                    ref_emb = np.frombuffer(e.vector, dtype=np.float32)
                    similarity, is_match = compare_faces(emb, ref_emb)
                    if similarity > best_score:
                        best_score = similarity
                        best_person = get_person_by_embedding_id(e.embedding_id, session)

                bbox = face.bbox.astype(int).tolist()
                result = {
                    "bbox": bbox,
                    "matched": bool(best_person is not None and best_score > 0.65),  # threshold
                    "person_name": best_person.first_name if best_person else None,
                    "score": float(best_score)
                }
                results.append(result)


"""

### real time recog endpoit 
"""
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
            faces = embedder.app.get(frame) 
            
            if not faces:
                await websocket.send_json({"faces": []}) 
                await asyncio.sleep(0.1) 
                continue 
            
            results = [] 
            for face in faces: 
                emb = face.embedding 
                if emb is None: 
                    continue 
                # Compare against all stored embeddings 
                
                best_score = 0.0 
                best_person = None 
                for e in embeddings: 
                    ref_emb = np.frombuffer(e.vector, dtype=np.float32)
                    similarity, is_match = compare_faces(emb, ref_emb) 
                
                    if similarity > best_score: 
                        best_score = similarity 
                
                    best_person = get_person_by_embedding_id(e.embedding_id, session) 
                    bbox = face.bbox.astype(int).tolist() 
                    result = { "bbox": bbox, 
                    "matched": bool(best_person is not None and best_score > 0.65),
                        # threshold 
                        "person_name": best_person.first_name if best_person else None, 
                        "score": float(best_score) } 
                    
                    results.append(result) 
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
                                

"""

## optimized version of real time recog endpoit
# 
"""
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

""" 