import requests
from typing import Optional
from config import settings


class RequestYaiProvider:
    """RequestYai implementation of LLM transcription provider"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.LLM_API_KEY
        self.api_url = "https://api.requestyai.com/v1/transcribe"  # Placeholder URL

    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio file using RequestYai API

        Args:
            audio_path: Path to the audio file to transcribe

        Returns:
            Transcribed text from the audio file

        Raises:
            Exception: If transcription fails
        """
        try:
            # Open audio file
            with open(audio_path, 'rb') as audio_file:
                files = {'file': audio_file}
                headers = {
                    'Authorization': f'Bearer {self.api_key}'
                }

                # Make API request
                response = requests.post(
                    self.api_url,
                    files=files,
                    headers=headers,
                    timeout=300  # 5 minutes timeout for long audio files
                )

                response.raise_for_status()

                # Parse response
                result = response.json()
                transcription = result.get('transcription', result.get('text', ''))

                if not transcription:
                    raise ValueError("No transcription returned from API")

                return transcription

        except requests.exceptions.RequestException as e:
            raise Exception(f"RequestYai API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")


class MockLLMProvider:
    """Mock LLM provider for testing purposes"""

    def transcribe_audio(self, audio_path: str) -> str:
        """
        Mock transcription that returns a placeholder text

        Args:
            audio_path: Path to the audio file (unused in mock)

        Returns:
            Mock transcription text
        """
        return f"[Mock transcription for {audio_path}] This is a sample transcription of the audio file. In a real implementation, this would contain the actual transcribed text from the RequestYai API."
