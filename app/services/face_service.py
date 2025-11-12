import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
from insightface.app import FaceAnalysis
from app.cruds.person_crud import get_person_by_embedding_id

# Quick Haar for coarse detection (fast). You can skip and just use FaceAnalysis on full frame if you prefer.

model_name = "buffalo_l"
class InsightFaceEmbedder:
    def __init__(self):
        self.app = FaceAnalysis(name=model_name, providers=['CPUExecutionProvider'])
        ctx_id = 1
        self.app.prepare(ctx_id=ctx_id, det_size=(640, 640))

    def get_face_embedding_image(self, image_path : str):
        img = cv2.imread(image_path)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        faces = self.app.get(rgb)
        
        if len(faces) < 1:
            raise ValueError("No faces detected in the image")
        if len(faces) > 1:
            print("Warning: Multiple faces detected. Using first detected face")
        print(faces[0].embedding)
        return faces[0].embedding.astype(np.float32)
    

    def recoginze_face_image(self, image_path, embedding):
        emb1 = self.get_face_embedding_image(image_path)
        res = self.compare_faces(emb1, embedding)
        print(res)
        return res
    
    def real_time_recognition(self, faces, embeddings, session, threshold: float = 0.65):
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
                similarity, is_match = cosine_similarity(emb, ref_emb) 
                if similarity > best_score: 
                    best_score = similarity 
            
                    best_person = get_person_by_embedding_id(e.embedding_id, session) 
                    bbox = face.bbox.astype(int).tolist() 
            matched = best_score > threshold
            result = { "bbox": bbox,
            "matched": matched,
                "person_name": best_person.first_name,
                "person_id" : best_person.person_id,
                "score": float(best_score) }
                
            results.append(result) 

        return results
    
def calculate_embeddings_avg(embs: list[np.ndarray]) -> np.ndarray:
    if not embs:
        raise ValueError("The list of embeddings is empty.")
    emb_matrix = np.vstack(embs)
    avg_emb = np.mean(emb_matrix, axis=0)
    avg_emb = avg_emb / (np.linalg.norm(avg_emb) + 1e-8)
    return avg_emb


def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray, threshold: float = 0.65 ):
    denom = (np.linalg.norm(emb1) * np.linalg.norm(emb2)) + 1e-8
    similarity = float(np.dot(emb1, emb2) / denom)
    return similarity, similarity > threshold