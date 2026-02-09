"""
Standalone Chat Agent Server - Phase III Implementation

This is a separate FastAPI server for the AI Chat Agent functionality.
Run this independently from your main backend server.

Usage:
    python backend/chat_server.py
    OR
    uvicorn backend.chat_server:app --reload --port 8002
"""
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
import traceback

from routers.chat import router as chat_router
from database import engine
from models.conversation import Conversation, Message
from sqlmodel import SQLModel

app = FastAPI(
    title="AI Chat Agent API - Phase III",
    version="1.0.0",
    description="Conversational AI agent for task management"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hackathon-ii-phase-ii-todo.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include chat router
app.include_router(chat_router)

@app.on_event("startup")
def on_startup():
    """Create conversation tables on startup."""
    try:
        # Only create conversation-related tables
        Conversation.metadata.create_all(bind=engine)
        Message.metadata.create_all(bind=engine)
        print("✓ Chat Agent database tables created successfully!")
    except Exception as e:
        print(f"✗ Error creating database tables: {e}")
        traceback.print_exc()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"Validation error: {exc}")
    traceback.print_exc()
    return PlainTextResponse(str(exc), status_code=422)

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    print(f"General error: {exc}")
    traceback.print_exc()
    return PlainTextResponse(f"Internal server error: {str(exc)}", status_code=500)

@app.get("/")
def read_root():
    """Root endpoint for chat agent server."""
    return {
        "service": "AI Chat Agent - Phase III",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "chat": "POST /api/{user_id}/chat",
            "health": "GET /health"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "chat-agent",
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🤖 AI Chat Agent Server - Phase III")
    print("="*60)
    print("Starting on: http://localhost:8002")
    print("Chat endpoint: POST /api/{user_id}/chat")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8002)
