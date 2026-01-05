import cv2
import numpy as np
from insightface.app import FaceAnalysis
from app.cruds.person_crud import get_person_by_embedding_id
import onnxruntime as ort

model_name = "buffalo_l"
class InsightFaceEmbedder:
    def __init__(self):
        available = ort.get_available_providers()

        providers = ['CPUExecutionProvider']  

        if 'CoreMLExecutionProvider' in available:
            providers = ['CoreMLExecutionProvider']

        self.app = FaceAnalysis(name=model_name, providers=providers)
        ctx_id = 0 
        self.app.prepare(ctx_id=ctx_id, det_size=(640, 640))

    def get_face_embedding_image(self, image_path : str):
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        faces = self.app.get(img)
        
        if len(faces) < 1:
            raise ValueError("No faces detected in the image")
        if len(faces) > 1:
            print("Warning: Multiple faces detected. Using first detected face")
        return faces[0].embedding.astype(np.float32)
    

    def recoginze_face_image(self, image_path, embedding):
        emb1 = self.get_face_embedding_image(image_path)
        res = self.compare_faces(emb1, embedding)
        print(res)
        return res
    
    def find_match(self, face, embeddings, session, threshold: float):
        results = [] 

        emb = face.embedding 
        best_score = 0.0 
        best_person = None 
        emb_id = 0
        for e in embeddings:
            ref_emb = np.frombuffer(e.vector, dtype=np.float32)
            similarity = cosine_similarity(emb, ref_emb) 
            if similarity > best_score: 
                best_score = similarity 
                emb_id = e.embedding_id
                bbox = face.bbox.astype(int).tolist()
        
        matched = best_score > threshold
         
        best_person = get_person_by_embedding_id(emb_id, session) 
        if matched:
            result = { "bbox": bbox,
            "matched": matched,
            "person_id" : best_person.person_id,
            "first_name": best_person.first_name,
            "last_name" : best_person.last_name,
            "gussed" : "",
            "score": float(best_score) }
        else:
            result = { "bbox": bbox,
            "matched": False,
            "name" : "Unkown",
            "gussed" : best_person.first_name,
            "score": float(best_score) }
            
        results.append(result) 

        return results
    
def calculate_embeddings_avg(embs: list[np.ndarray]) -> np.ndarray:
    if not embs:
        raise ValueError("The list of embeddings is empty.")
    normalized_embs = [e / (np.linalg.norm(e) + 1e-8) for e in embs]
    avg_emb = np.mean(np.vstack(normalized_embs), axis=0)
    avg_emb = avg_emb / (np.linalg.norm(avg_emb) + 1e-8)

    return avg_emb


def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray):
    denom = (np.linalg.norm(emb1) * np.linalg.norm(emb2)) + 1e-8
    similarity = float(np.dot(emb1, emb2) / denom)
    return similarity