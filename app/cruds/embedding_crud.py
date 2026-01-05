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

def get_all_embeddings(session: Session) -> Optional[List[Embedding]]:
    statement = select(Embedding)
    embeddings = session.exec(statement).all()
    if not embeddings:
        return None
    return embeddings

