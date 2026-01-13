"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from src.core.config import settings
from src.core.database import sync_engine
from src.api import auth, tasks, chat, conversations
from src.models import User, Task, Conversation, Message

# --- DATABASE TABLE CREATION ---
def create_db_and_tables():
    """Uses the sync engine to create tables safely on startup."""
    SQLModel.metadata.create_all(sync_engine)

# --- APP CONFIGURATION ---
app = FastAPI(
    title="Todo API",
    description="Full-Stack Todo Application API",
    version="1.0.0",
)

# --- STARTUP EVENT ---
# backend/src/main.py

@app.on_event("startup")
def on_startup():
    from src.core.database import sync_engine
    from sqlmodel import SQLModel
    # This reaches out to Neon and physically creates the 'user' and 'task' tables
    print("Initializing Neon Database...")
    SQLModel.metadata.create_all(sync_engine)
    print("Neon Database ready!")

# --- CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all domains (including your Vercel URL)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- BASE ROUTES ---
@app.get("/")
async def root():
    return {"status": "online", "message": "Backend is running"}

# --- ROUTER REGISTRATION ---
# Standard prefixes
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])

# Backup prefixes for frontend compatibility
app.include_router(auth.router, prefix="/api/auth", tags=["auth-backup"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks-backup"])