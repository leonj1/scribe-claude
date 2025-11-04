import pytest
from repositories.user_repository import MySQLUserRepository
from repositories.recording_repository import MySQLRecordingRepository
from models.recording import RecordingStatus


class TestUserRepository:
    """Unit tests for UserRepository"""

    def test_create_user(self, test_db):
        """Test creating a new user"""
        repo = MySQLUserRepository(test_db)
        user = repo.create_user(
            google_id="google_123",
            email="test@example.com",
            display_name="Test User",
            avatar_url="https://example.com/avatar.jpg"
        )

        assert user.id is not None
        assert user.google_id == "google_123"
        assert user.email == "test@example.com"
        assert user.display_name == "Test User"

    def test_get_user_by_id(self, test_db, sample_user):
        """Test retrieving user by ID"""
        repo = MySQLUserRepository(test_db)
        user = repo.get_user_by_id(sample_user.id)

        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email

    def test_get_user_by_google_id(self, test_db, sample_user):
        """Test retrieving user by Google ID"""
        repo = MySQLUserRepository(test_db)
        user = repo.get_user_by_google_id(sample_user.google_id)

        assert user is not None
        assert user.google_id == sample_user.google_id

    def test_update_user(self, test_db, sample_user):
        """Test updating user information"""
        repo = MySQLUserRepository(test_db)
        updated_user = repo.update_user(
            sample_user.id,
            display_name="Updated Name"
        )

        assert updated_user is not None
        assert updated_user.display_name == "Updated Name"


class TestRecordingRepository:
    """Unit tests for RecordingRepository"""

    def test_create_recording(self, test_db, sample_user):
        """Test creating a new recording"""
        repo = MySQLRecordingRepository(test_db)
        recording = repo.create_recording(user_id=sample_user.id)

        assert recording.id is not None
        assert recording.user_id == sample_user.id
        assert recording.status == RecordingStatus.active

    def test_get_recording(self, test_db, sample_recording):
        """Test retrieving a recording by ID"""
        repo = MySQLRecordingRepository(test_db)
        recording = repo.get_recording(sample_recording.id)

        assert recording is not None
        assert recording.id == sample_recording.id

    def test_list_recordings(self, test_db, sample_user, sample_recording):
        """Test listing user's recordings"""
        repo = MySQLRecordingRepository(test_db)
        recordings = repo.list_recordings(sample_user.id)

        assert len(recordings) > 0
        assert recordings[0].user_id == sample_user.id

    def test_add_chunk(self, test_db, sample_recording):
        """Test adding an audio chunk"""
        repo = MySQLRecordingRepository(test_db)
        chunk = repo.add_chunk(
            recording_id=sample_recording.id,
            chunk_path="/path/to/chunk.webm",
            chunk_index=0,
            duration_seconds=10.5
        )

        assert chunk.id is not None
        assert chunk.recording_id == sample_recording.id
        assert chunk.chunk_index == 0
        assert chunk.duration_seconds == 10.5

    def test_mark_paused(self, test_db, sample_recording):
        """Test marking recording as paused"""
        repo = MySQLRecordingRepository(test_db)
        recording = repo.mark_paused(sample_recording.id)

        assert recording is not None
        assert recording.status == RecordingStatus.paused

    def test_mark_ended(self, test_db, sample_recording):
        """Test marking recording as ended with transcription"""
        repo = MySQLRecordingRepository(test_db)
        recording = repo.mark_ended(
            recording_id=sample_recording.id,
            full_audio_path="/path/to/full.wav",
            transcription="Test transcription text"
        )

        assert recording is not None
        assert recording.status == RecordingStatus.ended
        assert recording.audio_file_path == "/path/to/full.wav"
        assert recording.transcription_text == "Test transcription text"

    def test_get_chunks(self, test_db, sample_recording):
        """Test retrieving chunks for a recording"""
        repo = MySQLRecordingRepository(test_db)

        # Add multiple chunks
        repo.add_chunk(sample_recording.id, "/path/chunk_0.webm", 0)
        repo.add_chunk(sample_recording.id, "/path/chunk_1.webm", 1)
        repo.add_chunk(sample_recording.id, "/path/chunk_2.webm", 2)

        chunks = repo.get_chunks(sample_recording.id)

        assert len(chunks) == 3
        assert chunks[0].chunk_index == 0
        assert chunks[1].chunk_index == 1
        assert chunks[2].chunk_index == 2
