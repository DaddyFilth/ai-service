"""Configuration management for the AI service."""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        # Asterisk/SIP Configuration
        self.asterisk_host: str = os.getenv("ASTERISK_HOST", "localhost")
        try:
            self.asterisk_port: int = int(os.getenv("ASTERISK_PORT", "5060"))
        except ValueError:
            raise ValueError(
                f"Invalid ASTERISK_PORT environment variable: {os.getenv('ASTERISK_PORT')}. "
                "Must be a valid integer."
            )
        self.asterisk_username: str = os.getenv("ASTERISK_USERNAME", "ai_service")
        self.asterisk_password: str = os.getenv("ASTERISK_PASSWORD", "")
        
        # Ollama Configuration
        self.ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_model: str = os.getenv("OLLAMA_MODEL", "llama2")
        
        # Service Configuration
        self.service_host: str = os.getenv("SERVICE_HOST", "0.0.0.0")
        try:
            self.service_port: int = int(os.getenv("SERVICE_PORT", "8000"))
        except ValueError:
            raise ValueError(
                f"Invalid SERVICE_PORT environment variable: {os.getenv('SERVICE_PORT')}. "
                "Must be a valid integer."
            )
        self.recordings_dir: str = os.getenv("RECORDINGS_DIR", "./recordings")
        try:
            self.min_free_space_mb: int = int(os.getenv("MIN_FREE_SPACE_MB", "100"))
        except ValueError:
            raise ValueError(
                f"Invalid MIN_FREE_SPACE_MB environment variable: {os.getenv('MIN_FREE_SPACE_MB')}. "
                "Must be a valid integer."
            )


# Global settings instance
settings = Settings()
