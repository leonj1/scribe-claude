from typing import Protocol, List, Optional
from models.user import User
from models.recording import Recording, RecordingChunk


class UserRepository(Protocol):
    """Interface for User repository operations"""

    def create_user(
        self,
        google_id: str,
        email: str,
        display_name: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> User:
        """Create a new user"""
        ...

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        ...

    def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID"""
        ...

    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user information"""
        ...


class RecordingRepository(Protocol):
    """Interface for Recording repository operations"""

    def create_recording(self, user_id: str) -> Recording:
        """Create a new recording session"""
        ...

    def get_recording(self, recording_id: str) -> Optional[Recording]:
        """Get recording by ID"""
        ...

    def list_recordings(self, user_id: str) -> List[Recording]:
        """List all recordings for a user"""
        ...

    def add_chunk(
        self,
        recording_id: str,
        chunk_path: str,
        chunk_index: int,
        duration_seconds: Optional[float] = None
    ) -> RecordingChunk:
        """Add an audio chunk to a recording"""
        ...

    def get_chunks(self, recording_id: str) -> List[RecordingChunk]:
        """Get all chunks for a recording"""
        ...

    def mark_paused(self, recording_id: str) -> Optional[Recording]:
        """Mark recording as paused"""
        ...

    def mark_ended(
        self,
        recording_id: str,
        full_audio_path: str,
        transcription: str
    ) -> Optional[Recording]:
        """Mark recording as ended with transcription"""
        ...

    def update_recording(self, recording_id: str, **kwargs) -> Optional[Recording]:
        """Update recording fields"""
        ...
