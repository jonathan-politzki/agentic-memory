from fastapi import FastAPI, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from . import models
from .database.connection import engine, get_db
from .models import Context, Memory, SearchQuery

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on startup
    print("INFO:     Application startup complete. Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    print("INFO:     Database tables created.")
    yield
    # This code runs on shutdown
    print("INFO:     Application shutdown.")

app = FastAPI(
    title="Agentic Memory API",
    description="An API for a robust, developer-first Agentic Memory service.",
    version="1.0.0",
    lifespan=lifespan
)

@app.post("/contexts", response_model=Context, status_code=201)
def create_context(context_input: Context, db: Session = Depends(get_db)):
    """
    Creates a new context (e.g., for a new user or project).
    """
    db_context = db.query(models.DBContext).filter(models.DBContext.id == context_input.id).first()
    if db_context:
        raise HTTPException(status_code=409, detail="Context with this ID already exists.")
    
    new_context = models.DBContext(**context_input.model_dump())
    db.add(new_context)
    db.commit()
    db.refresh(new_context)
    return new_context

@app.post("/memories", response_model=Memory, status_code=201)
def add_memory(memory_input: Memory, db: Session = Depends(get_db)):
    """
    Adds a new memory to a specific context.
    """
    db_context = db.query(models.DBContext).filter(models.DBContext.id == memory_input.context_id).first()
    if not db_context:
        raise HTTPException(status_code=404, detail=f"Context with ID '{memory_input.context_id}' not found.")
    
    # Manually map the 'metadata' from the input to the 'data' field in the DB model
    memory_data = memory_input.model_dump()
    memory_data['data'] = memory_data.pop('metadata')
    
    new_memory = models.DBMemory(**memory_data)
    db.add(new_memory)
    db.commit()
    db.refresh(new_memory)
    return new_memory

@app.post("/search", response_model=List[Memory])
def search_memories(search_input: SearchQuery, db: Session = Depends(get_db)):
    """
    Searches for memories within a specific context.
    (Currently a simple text search, to be replaced with vector search)
    """
    db_context = db.query(models.DBContext).filter(models.DBContext.id == search_input.context_id).first()
    if not db_context:
        raise HTTPException(status_code=404, detail=f"Context with ID '{search_input.context_id}' not found.")

    query_text = search_input.query.lower()
    
    # Simple, case-insensitive text search for now
    results = db.query(models.DBMemory).filter(
        models.DBMemory.context_id == search_input.context_id,
        models.DBMemory.content.ilike(f"%{query_text}%")
    ).all()
    
    return results

@app.get("/")
def read_root():
    """
    A simple endpoint to confirm the server is running.
    """
    return {"message": "Welcome to the Agentic Memory API!"} 