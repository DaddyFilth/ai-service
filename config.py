"""Configuration management for the AI service."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Asterisk/SIP Configuration
    asterisk_host: str = "localhost"
    asterisk_port: int = 5060
    asterisk_username: str = "ai_service"
    asterisk_password: str = ""
    
    # Ollama Configuration
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    
    # Service Configuration
    service_host: str = "0.0.0.0"
    service_port: int = 8000
    recordings_dir: str = "./recordings"
    min_free_space_mb: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
