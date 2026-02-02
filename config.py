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
        self.asterisk_port: int = int(os.getenv("ASTERISK_PORT", "5060"))
        self.asterisk_username: str = os.getenv("ASTERISK_USERNAME", "ai_service")
        self.asterisk_password: str = os.getenv("ASTERISK_PASSWORD", "")
        
        # Ollama Configuration
        self.ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_model: str = os.getenv("OLLAMA_MODEL", "llama2")
        
        # Service Configuration
        self.service_host: str = os.getenv("SERVICE_HOST", "0.0.0.0")
        self.service_port: int = int(os.getenv("SERVICE_PORT", "8000"))
        self.recordings_dir: str = os.getenv("RECORDINGS_DIR", "./recordings")
        self.min_free_space_mb: int = int(os.getenv("MIN_FREE_SPACE_MB", "100"))


# Global settings instance
settings = Settings()
