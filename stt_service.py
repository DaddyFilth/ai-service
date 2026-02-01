"""Speech-to-Text service using OpenAI Whisper."""
from typing import Optional
import logging

try:
    import whisper
except ImportError:  # pragma: no cover - optional dependency
    whisper = None

logger = logging.getLogger(__name__)


class STTService:
    """Speech-to-Text service using Whisper model."""
    
    def __init__(self, model_name: str = "base"):
        """
        Initialize the STT service.
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model: Optional["whisper.Whisper"] = None
        logger.info(f"Initializing STT service with model: {model_name}")
    
    def load_model(self):
        """Load the Whisper model."""
        if whisper is None:
            raise RuntimeError(
                "openai-whisper is not installed. Install optional dependencies with "
                "`pip install -r requirements-optional.txt`."
            )
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
    
    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Transcribed text
        """
        if self.model is None:
            self.load_model()
        
        logger.info(f"Transcribing audio: {audio_path}")
        result = self.model.transcribe(audio_path)
        text = result["text"]
        logger.info(f"Transcription result: {text}")
        return text
    
    def transcribe_chunk(self, audio_path: str, language: Optional[str] = None) -> dict:
        """
        Transcribe audio with detailed information.
        
        Args:
            audio_path: Path to the audio file
            language: Optional language code
            
        Returns:
            Dictionary with transcription details
        """
        if self.model is None:
            self.load_model()
        
        logger.info(f"Transcribing audio chunk: {audio_path}")
        result = self.model.transcribe(audio_path, language=language)
        return result
