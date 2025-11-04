import os
from typing import List
from pydub import AudioSegment


def assemble_audio_chunks(chunk_paths: List[str], output_path: str) -> str:
    """
    Assemble multiple audio chunks into a single audio file

    Args:
        chunk_paths: List of paths to audio chunk files (in order)
        output_path: Path where the assembled audio should be saved

    Returns:
        Path to the assembled audio file

    Raises:
        Exception: If assembly fails
    """
    try:
        if not chunk_paths:
            raise ValueError("No chunks provided to assemble")

        # Load the first chunk to initialize
        combined = AudioSegment.from_file(chunk_paths[0])

        # Append remaining chunks
        for chunk_path in chunk_paths[1:]:
            if os.path.exists(chunk_path):
                audio_chunk = AudioSegment.from_file(chunk_path)
                combined += audio_chunk
            else:
                raise FileNotFoundError(f"Chunk file not found: {chunk_path}")

        # Export the combined audio
        combined.export(output_path, format="wav")

        return output_path

    except Exception as e:
        raise Exception(f"Failed to assemble audio chunks: {str(e)}")


def get_audio_duration(audio_path: str) -> float:
    """
    Get duration of an audio file in seconds

    Args:
        audio_path: Path to audio file

    Returns:
        Duration in seconds
    """
    try:
        audio = AudioSegment.from_file(audio_path)
        return len(audio) / 1000.0  # Convert milliseconds to seconds
    except Exception as e:
        raise Exception(f"Failed to get audio duration: {str(e)}")
