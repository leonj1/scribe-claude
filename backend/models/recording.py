from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum, Integer, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from database import Base


class RecordingStatus(enum.Enum):
    active = "active"
    paused = "paused"
    ended = "ended"


class Recording(Base):
    __tablename__ = "recordings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(Enum(RecordingStatus), default=RecordingStatus.active, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    audio_file_path = Column(String(512), nullable=True)
    transcription_text = Column(Text, nullable=True)
    llm_provider = Column(String(50), default="requestyai", nullable=False)
    notes = Column(Text, nullable=True)  # Enhancement: allow user notes on recording

    # Relationships
    user = relationship("User", back_populates="recordings")
    chunks = relationship("RecordingChunk", back_populates="recording", cascade="all, delete-orphan", order_by="RecordingChunk.chunk_index")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "audio_file_path": self.audio_file_path,
            "transcription_text": self.transcription_text,
            "llm_provider": self.llm_provider,
            "notes": self.notes,
            "chunks_count": len(self.chunks) if self.chunks else 0,
        }


class RecordingChunk(Base):
    __tablename__ = "recording_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recording_id = Column(String(36), ForeignKey("recordings.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    audio_blob_path = Column(String(512), nullable=False)
    duration_seconds = Column(Float, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    recording = relationship("Recording", back_populates="chunks")

    def to_dict(self):
        return {
            "id": self.id,
            "recording_id": self.recording_id,
            "chunk_index": self.chunk_index,
            "audio_blob_path": self.audio_blob_path,
            "duration_seconds": self.duration_seconds,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }
