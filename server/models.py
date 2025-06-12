from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, JSON
from .database.connection import Base

# --- SQLAlchemy Table Models ---

class DBContext(Base):
    __tablename__ = "contexts"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DBMemory(Base):
    __tablename__ = "memories"
    id = Column(String, primary_key=True, index=True)
    context_id = Column(String, index=True)
    content = Column(String)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

# --- Pydantic API Models ---

class Context(BaseModel):
    """
    Represents a logical partition for memories, like a user or a project.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the context.")
    name: Optional[str] = Field(None, description="A human-readable name for the context.")
    owner_id: Optional[str] = Field(None, description="The user or entity that owns this context.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of when the context was created.")

class Memory(BaseModel):
    """
    Represents the fundamental unit of data stored within a context.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the memory.")
    context_id: str = Field(..., description="The ID of the context this memory belongs to.")
    content: str = Field(..., description="The text or data of the memory.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="A simple key-value store for additional, filterable data.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of when the memory was created.")

    class Config:
        """Pydantic configuration."""
        # This allows the model to be created from ORM objects, which will be useful later.
        from_attributes = True

class SearchQuery(BaseModel):
    """
    Represents the input for a search request.
    """
    query: str
    context_id: str 