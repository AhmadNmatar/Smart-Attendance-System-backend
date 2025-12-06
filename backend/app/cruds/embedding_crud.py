from __future__ import annotations

from typing import Optional, Sequence, List
from sqlmodel import Session, select
from app.models.embedding import Embedding
import numpy as np

# The below methods does not do any form of enc/dec

#this method should return the primary key of the created recored
def add_new_emb(embedding : Embedding, session : Session) -> int | None :
    emb = Embedding.model_validate(embedding)
    session.add(emb)
    session.commit()
    session.refresh(emb)

    if not emb:
        return None
    return emb.embedding_id


# get all embeddings

def get_all(session: Session) -> Optional[List[Embedding]]:
    statement = select(Embedding)
    embeddings = session.exec(statement).all()
    if not embeddings:
        return None
    return embeddings



# cosine similarity: (A · B) / (||A|| * ||B||)
def cosine_similarity(vec1: Sequence[float], vec2: Sequence[float]) -> float:
    v1 = np.array(vec1, dtype=float)
    v2 = np.array(vec2, dtype=float)

    # Avoid division by zero
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)

    if norm_v1 == 0.0 or norm_v2 == 0.0:
        return 0.0

    similarity = np.dot(v1, v2) / (norm_v1 * norm_v2)
    return float(similarity)

# what may be need to fix here is:
# 1. define a threshold, now we take the one that higher than -1
# 2. try another approach to define the similarity between embeddings