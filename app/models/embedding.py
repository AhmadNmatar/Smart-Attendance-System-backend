from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel

class Embedding(SQLModel, table=True):
    embedding_id: int | None = Field(default=None, primary_key=True)
    vector: bytes  # encrypted facial embedding

    Person: Optional["Person"] = Relationship(back_populates="embeddings")