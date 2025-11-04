from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from database import init_db
from routers import auth, recordings
from config import settings

# Create FastAPI app
app = FastAPI(
    title="Audio Transcription Service",
    description="Healthcare audio transcription platform with LLM-powered transcription",
    version="1.0.0"
)

# Add session middleware for OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(recordings.router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    # Initialize database tables
    init_db()

    # Create audio storage directory
    os.makedirs(settings.AUDIO_STORAGE_PATH, exist_ok=True)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Audio Transcription Service API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
