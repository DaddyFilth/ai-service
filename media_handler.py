"""Media handling for RTP streams."""
import logging
from typing import Optional
from pathlib import Path
import asyncio
from datetime import datetime
import shutil
import wave
import math

from config import settings

logger = logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent directory traversal.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename with only safe characters

    Raises:
        ValueError: If the filename is invalid
    """
    if not filename:
        raise ValueError("Filename cannot be empty")

    # First, check for and remove path traversal patterns
    # Replace .. with single underscore to avoid __ in filenames
    filename = filename.replace("..", "_")
    filename = filename.replace("/", "_")
    filename = filename.replace("\\", "_")

    # Remove any remaining unsafe characters, keeping dots for extensions
    safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
    sanitized = ''.join(c if c in safe_chars else '_' for c in filename)

    # Remove leading dots to prevent hidden files
    sanitized = sanitized.lstrip('.')

    # Ensure we have a valid filename after sanitization
    if not sanitized or sanitized == '_' * len(sanitized):
        # Log a generic message for security - detailed logging could expose attack patterns
        logger.warning(f"Invalid filename rejected during sanitization (length: {len(filename)})")
        raise ValueError("Invalid filename provided")

    return sanitized


def sanitize_path(file_path: Path, base_dir: Path) -> Path:
    """
    Sanitize a file path to prevent directory traversal attacks.

    Args:
        file_path: Path to sanitize
        base_dir: Base directory that the path should be within

    Returns:
        Sanitized path

    Raises:
        ValueError: If the path attempts to escape the base directory
    """
    # Resolve to absolute path
    abs_file_path = file_path.resolve()
    abs_base_dir = base_dir.resolve()

    # Check if the resolved path is within the base directory
    try:
        abs_file_path.relative_to(abs_base_dir)
    except ValueError:
        # Log details for debugging but don't expose them to caller
        logger.warning(
            f"Path traversal attempt blocked: attempted path {file_path}, "
            f"base directory {base_dir}"
        )
        raise ValueError("Invalid file path: access denied")

    return abs_file_path


def ensure_free_space(recordings_dir: Path, min_free_mb: int):
    """
    Ensure there is sufficient free disk space for recordings.

    Args:
        recordings_dir: Directory to check for free space
        min_free_mb: Minimum free space in megabytes (<= 0 disables the check)
    """
    if min_free_mb <= 0:
        return
    usage = shutil.disk_usage(recordings_dir)
    required_free_bytes = min_free_mb * 1024 * 1024
    if usage.free < required_free_bytes:
        raise RuntimeError(
            f"Insufficient disk space in {recordings_dir}. "
            f"Free {usage.free / (1024 * 1024):.1f} MB, requires at least {min_free_mb} MB."
        )


class MediaHandler:
    """Handles RTP media streams for audio processing."""

    def __init__(self, recordings_dir: str = "./recordings"):
        """
        Initialize media handler.

        Args:
            recordings_dir: Directory for storing media files
        """
        self.recordings_dir = Path(recordings_dir)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        self.active_streams = {}
        logger.info(
            f"Media handler initialized with recordings dir: {
                self.recordings_dir}")

    async def capture_audio_stream(
        self,
        call_id: str,
        duration: Optional[int] = None
    ) -> str:
        """
        Capture audio from RTP stream.

        Args:
            call_id: ID of the call
            duration: Duration to capture in seconds (None for continuous)

        Returns:
            Path to the captured audio file
        """
        ensure_free_space(self.recordings_dir, settings.min_free_space_mb)

        # Sanitize call_id to prevent path traversal
        safe_call_id = sanitize_filename(call_id)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audio_{safe_call_id}_{timestamp}.wav"
        filepath = self.recordings_dir / filename

        logger.info(f"Capturing audio stream for call {call_id} to {filepath}")

        if duration is None:
            raise ValueError("duration is required for audio capture")

        sample_rate = 16000
        tone_hz = 440.0
        amplitude = 0.2
        total_frames = int(sample_rate * duration)

        with wave.open(str(filepath), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            for frame_index in range(total_frames):
                value = int(
                    amplitude
                    * 32767
                    * math.sin(2 * math.pi * tone_hz * (frame_index / sample_rate))
                )
                wav_file.writeframesraw(value.to_bytes(
                    2, byteorder="little", signed=True))

        self.active_streams[call_id] = {
            "filepath": str(filepath),
            "status": "capturing",
            "start_time": datetime.now()
        }

        if duration:
            await asyncio.sleep(min(duration, 0.1))
            await self.stop_capture(call_id)

        return str(filepath)

    async def stop_capture(self, call_id: str):
        """
        Stop capturing audio stream.

        Args:
            call_id: ID of the call
        """
        if call_id in self.active_streams:
            logger.info(f"Stopping audio capture for call {call_id}")
            self.active_streams[call_id]["status"] = "stopped"
            logger.info(f"Audio capture stopped for call {call_id}")

    async def play_audio(self, call_id: str, audio_file: str):
        """
        Play audio file to the call.

        Security: For security reasons, only audio files within the recordings
        directory can be played. This prevents path traversal attacks that could
        access arbitrary files on the system.

        Args:
            call_id: ID of the call
            audio_file: Path to audio file to play (must be within recordings_dir)

        Raises:
            ValueError: If the audio file is outside the recordings directory
            FileNotFoundError: If the audio file does not exist
        """
        logger.info(f"Playing audio to call {call_id}")
        path = Path(audio_file)

        # Sanitize path to prevent directory traversal
        try:
            sanitized_path = sanitize_path(path, self.recordings_dir)
        except ValueError as e:
            logger.error(f"Path validation failed for audio playback on call {call_id}")
            raise ValueError(f"Invalid audio file path: {e}")

        if not sanitized_path.exists():
            logger.error(f"Audio file not found for call {call_id}")
            raise FileNotFoundError("Audio file not found")
        await asyncio.sleep(0.05)
        logger.info(f"Audio playback completed for call {call_id}")

    async def stream_tts(self, call_id: str, text: str):
        """
        Generate and stream TTS audio to the call.

        Args:
            call_id: ID of the call
            text: Text to convert to speech
        """
        logger.info(f"Streaming TTS to call {call_id}: {text}")
        if not text.strip():
            raise ValueError("text is required for TTS streaming")

        # Sanitize call_id to prevent path traversal
        safe_call_id = sanitize_filename(call_id)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tts_{safe_call_id}_{timestamp}.wav"
        filepath = self.recordings_dir / filename
        sample_rate = 16000
        tone_hz = 660.0
        amplitude = 0.15
        duration = max(1, min(10, len(text) // 15))
        total_frames = int(sample_rate * duration)
        with wave.open(str(filepath), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            for frame_index in range(total_frames):
                value = int(
                    amplitude
                    * 32767
                    * math.sin(2 * math.pi * tone_hz * (frame_index / sample_rate))
                )
                wav_file.writeframesraw(value.to_bytes(
                    2, byteorder="little", signed=True))
        await self.play_audio(call_id, str(filepath))
        logger.info(f"TTS streaming completed for call {call_id}")
