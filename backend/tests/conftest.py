import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models.user import User
from models.recording import Recording, RecordingChunk


@pytest.fixture
def test_db():
    """Create a test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def sample_user(test_db):
    """Create a sample user for testing"""
    user = User(
        google_id="test_google_id_123",
        email="test@example.com",
        display_name="Test User",
        avatar_url="https://example.com/avatar.jpg"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def sample_recording(test_db, sample_user):
    """Create a sample recording for testing"""
    recording = Recording(
        user_id=sample_user.id
    )
    test_db.add(recording)
    test_db.commit()
    test_db.refresh(recording)
    return recording
