from typing import List, Optional
from sqlalchemy.orm import Session
from models.recording import Recording, RecordingChunk, RecordingStatus


class MySQLRecordingRepository:
    """MySQL implementation of RecordingRepository"""

    def __init__(self, db: Session):
        self.db = db

    def create_recording(self, user_id: str) -> Recording:
        """Create a new recording session"""
        recording = Recording(
            user_id=user_id,
            status=RecordingStatus.active
        )
        self.db.add(recording)
        self.db.commit()
        self.db.refresh(recording)
        return recording

    def get_recording(self, recording_id: str) -> Optional[Recording]:
        """Get recording by ID"""
        return self.db.query(Recording).filter(Recording.id == recording_id).first()

    def list_recordings(self, user_id: str) -> List[Recording]:
        """List all recordings for a user"""
        return (
            self.db.query(Recording)
            .filter(Recording.user_id == user_id)
            .order_by(Recording.created_at.desc())
            .all()
        )

    def add_chunk(
        self,
        recording_id: str,
        chunk_path: str,
        chunk_index: int,
        duration_seconds: Optional[float] = None
    ) -> RecordingChunk:
        """Add an audio chunk to a recording"""
        chunk = RecordingChunk(
            recording_id=recording_id,
            chunk_index=chunk_index,
            audio_blob_path=chunk_path,
            duration_seconds=duration_seconds
        )
        self.db.add(chunk)
        self.db.commit()
        self.db.refresh(chunk)
        return chunk

    def get_chunks(self, recording_id: str) -> List[RecordingChunk]:
        """Get all chunks for a recording, ordered by chunk_index"""
        return (
            self.db.query(RecordingChunk)
            .filter(RecordingChunk.recording_id == recording_id)
            .order_by(RecordingChunk.chunk_index)
            .all()
        )

    def mark_paused(self, recording_id: str) -> Optional[Recording]:
        """Mark recording as paused"""
        recording = self.get_recording(recording_id)
        if not recording:
            return None

        recording.status = RecordingStatus.paused
        self.db.commit()
        self.db.refresh(recording)
        return recording

    def mark_ended(
        self,
        recording_id: str,
        full_audio_path: str,
        transcription: str
    ) -> Optional[Recording]:
        """Mark recording as ended with transcription"""
        recording = self.get_recording(recording_id)
        if not recording:
            return None

        recording.status = RecordingStatus.ended
        recording.audio_file_path = full_audio_path
        recording.transcription_text = transcription
        self.db.commit()
        self.db.refresh(recording)
        return recording

    def update_recording(self, recording_id: str, **kwargs) -> Optional[Recording]:
        """Update recording fields"""
        recording = self.get_recording(recording_id)
        if not recording:
            return None

        for key, value in kwargs.items():
            if hasattr(recording, key):
                # Handle enum conversion for status
                if key == "status" and isinstance(value, str):
                    value = RecordingStatus(value)
                setattr(recording, key, value)

        self.db.commit()
        self.db.refresh(recording)
        return recording
