import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from api.auth import router as auth_router
from api.todos import router as todos_router
from routers.chat import router as chat_router
from database import engine
from models import User
from models.conversation import Conversation, Message
from db.models import Task
from sqlmodel import SQLModel
import traceback

app = FastAPI(title="Todo API with AI Chat Agent", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hackathon-ii-phase-iii-nine.vercel.app/",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router)
app.include_router(todos_router)
app.include_router(chat_router)  # AI Chat Agent routes

@app.on_event("startup")
def on_startup():
    try:
        SQLModel.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        traceback.print_exc()
        raise

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
    return {"message": "Todo API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)