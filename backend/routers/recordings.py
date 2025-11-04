from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from database import get_db
from models.user import User
from models.recording import Recording
from repositories.recording_repository import MySQLRecordingRepository
from middleware.auth import get_current_user
from llm.requestyai_provider import RequestYaiProvider
from utils.audio_utils import assemble_audio_chunks, get_audio_duration
from utils.encryption_utils import encryption_service
from config import settings


router = APIRouter(prefix="/recordings", tags=["recordings"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_recording(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new recording session

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Created recording object
    """
    recording_repo = MySQLRecordingRepository(db)
    recording = recording_repo.create_recording(user_id=current_user.id)

    # Create storage directory for this recording's chunks
    recording_dir = os.path.join(settings.AUDIO_STORAGE_PATH, recording.id)
    os.makedirs(recording_dir, exist_ok=True)

    return recording.to_dict()


@router.post("/{recording_id}/chunks", status_code=status.HTTP_201_CREATED)
async def upload_chunk(
    recording_id: str,
    chunk_index: int = Form(...),
    audio_chunk: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload an audio chunk for a recording

    Args:
        recording_id: ID of the recording
        chunk_index: Sequential index of this chunk
        audio_chunk: Audio file chunk
        current_user: Authenticated user
        db: Database session

    Returns:
        Created chunk object
    """
    recording_repo = MySQLRecordingRepository(db)
    recording = recording_repo.get_recording(recording_id)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload chunks to this recording"
        )

    # Save chunk to disk
    recording_dir = os.path.join(settings.AUDIO_STORAGE_PATH, recording_id)
    os.makedirs(recording_dir, exist_ok=True)

    chunk_filename = f"chunk_{chunk_index:04d}.webm"
    chunk_path = os.path.join(recording_dir, chunk_filename)

    try:
        with open(chunk_path, "wb") as buffer:
            shutil.copyfileobj(audio_chunk.file, buffer)

        # Get duration if possible
        try:
            duration = get_audio_duration(chunk_path)
        except:
            duration = None

        # Add chunk to database
        chunk = recording_repo.add_chunk(
            recording_id=recording_id,
            chunk_path=chunk_path,
            chunk_index=chunk_index,
            duration_seconds=duration
        )

        return chunk.to_dict()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save audio chunk: {str(e)}"
        )


@router.patch("/{recording_id}/pause")
async def pause_recording(
    recording_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a recording as paused

    Args:
        recording_id: ID of the recording
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated recording object
    """
    recording_repo = MySQLRecordingRepository(db)
    recording = recording_repo.get_recording(recording_id)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this recording"
        )

    recording = recording_repo.mark_paused(recording_id)
    return recording.to_dict()


@router.post("/{recording_id}/finish")
async def finish_recording(
    recording_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark recording as ended, assemble chunks, and trigger transcription

    Args:
        recording_id: ID of the recording
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated recording object with transcription
    """
    recording_repo = MySQLRecordingRepository(db)
    recording = recording_repo.get_recording(recording_id)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to finish this recording"
        )

    try:
        # Get all chunks
        chunks = recording_repo.get_chunks(recording_id)

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No audio chunks found for this recording"
            )

        # Sort chunks by index
        chunks = sorted(chunks, key=lambda x: x.chunk_index)
        chunk_paths = [chunk.audio_blob_path for chunk in chunks]

        # Assemble chunks into single audio file
        recording_dir = os.path.join(settings.AUDIO_STORAGE_PATH, recording_id)
        assembled_path = os.path.join(recording_dir, "full_audio.wav")

        assemble_audio_chunks(chunk_paths, assembled_path)

        # Encrypt the assembled audio file (HIPAA compliance)
        encrypted_path = os.path.join(recording_dir, "full_audio_encrypted.bin")
        encryption_service.encrypt_file(assembled_path, encrypted_path)

        # Transcribe using LLM provider
        llm_provider = RequestYaiProvider()
        transcription_text = llm_provider.transcribe_audio(assembled_path)

        # Encrypt transcription (HIPAA compliance)
        encrypted_transcription = encryption_service.encrypt_text(transcription_text)

        # Update recording with results
        recording = recording_repo.mark_ended(
            recording_id=recording_id,
            full_audio_path=encrypted_path,
            transcription=encrypted_transcription
        )

        # Clean up unencrypted file
        if os.path.exists(assembled_path):
            os.remove(assembled_path)

        # Return with decrypted transcription for display
        result = recording.to_dict()
        result['transcription_text'] = transcription_text

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to finish recording: {str(e)}"
        )


@router.get("/")
async def list_recordings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all recordings for the current user

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List of recording objects
    """
    recording_repo = MySQLRecordingRepository(db)
    recordings = recording_repo.list_recordings(user_id=current_user.id)

    # Decrypt transcriptions for display
    result = []
    for recording in recordings:
        rec_dict = recording.to_dict()
        if rec_dict.get('transcription_text'):
            try:
                rec_dict['transcription_text'] = encryption_service.decrypt_text(
                    rec_dict['transcription_text']
                )
            except:
                pass  # Keep encrypted if decryption fails
        result.append(rec_dict)

    return result


@router.get("/{recording_id}")
async def get_recording(
    recording_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific recording by ID

    Args:
        recording_id: ID of the recording
        current_user: Authenticated user
        db: Database session

    Returns:
        Recording object
    """
    recording_repo = MySQLRecordingRepository(db)
    recording = recording_repo.get_recording(recording_id)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this recording"
        )

    # Decrypt transcription for display
    rec_dict = recording.to_dict()
    if rec_dict.get('transcription_text'):
        try:
            rec_dict['transcription_text'] = encryption_service.decrypt_text(
                rec_dict['transcription_text']
            )
        except:
            pass  # Keep encrypted if decryption fails

    return rec_dict


@router.patch("/{recording_id}/notes")
async def update_recording_notes(
    recording_id: str,
    notes: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update notes for a recording (Enhancement from PRD)

    Args:
        recording_id: ID of the recording
        notes: Notes to add to the recording
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated recording object
    """
    recording_repo = MySQLRecordingRepository(db)
    recording = recording_repo.get_recording(recording_id)

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )

    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this recording"
        )

    recording = recording_repo.update_recording(recording_id, notes=notes)
    return recording.to_dict()
