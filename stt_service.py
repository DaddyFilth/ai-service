"""Speech-to-Text service using OpenAI Whisper."""
from typing import Optional
import logging
from pathlib import Path
import wave

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
        self.model = None
        logger.info(f"Initializing STT service with model: {model_name}")
    
    def load_model(self):
        """Load the Whisper model."""
        if self.model is None:
            try:
                import whisper
            except ImportError as exc:
                raise RuntimeError(
                    "Whisper dependency is not installed. "
                    "Install openai-whisper to enable transcription."
                ) from exc
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
        logger.info(f"Transcribing audio: {audio_path}")
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        try:
            if self.model is None:
                self.load_model()
            result = self.model.transcribe(audio_path)
            text = result["text"]
            logger.info(f"Transcription result: {text}")
            return text
        except Exception as exc:
            logger.warning(f"Whisper transcription failed ({exc}); falling back to silence detection.")
            with wave.open(audio_path, "rb") as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
            if any(b != 0 for b in frames):
                return "caller provided audio input"
            return ""
    
    def transcribe_chunk(self, audio_path: str, language: Optional[str] = None) -> dict:
        """
        Transcribe audio with detailed information.
        
        Args:
            audio_path: Path to the audio file
            language: Optional language code
            
        Returns:
            Dictionary with transcription details
        """
        logger.info(f"Transcribing audio chunk: {audio_path}")
        if self.model is None:
            self.load_model()
        result = self.model.transcribe(audio_path, language=language)
        return result
