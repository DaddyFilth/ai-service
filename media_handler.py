"""Media handling for RTP streams."""
import logging
from typing import Optional
from pathlib import Path
import asyncio
from datetime import datetime
import shutil

from config import settings

logger = logging.getLogger(__name__)

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
        logger.info(f"Media handler initialized with recordings dir: {self.recordings_dir}")

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
            min_free_space_mb: Minimum free disk space required in megabytes
            
        Returns:
            Path to the captured audio file
        """
        ensure_free_space(self.recordings_dir, settings.min_free_space_mb)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audio_{call_id}_{timestamp}.wav"
        filepath = self.recordings_dir / filename
        
        logger.info(f"Capturing audio stream for call {call_id} to {filepath}")
        
        # In a real implementation, this would:
        # 1. Capture RTP packets from Asterisk
        # 2. Decode the audio codec (e.g., G.711, Opus)
        # 3. Save to WAV file
        
        # For now, we'll simulate the capture
        self.active_streams[call_id] = {
            "filepath": str(filepath),
            "status": "capturing",
            "start_time": datetime.now()
        }
        
        if duration:
            await asyncio.sleep(duration)
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
        
        Args:
            call_id: ID of the call
            audio_file: Path to audio file to play
        """
        logger.info(f"Playing audio {audio_file} to call {call_id}")
        # In a real implementation, send audio to Asterisk for playback
        await asyncio.sleep(0.1)  # Simulate processing
        logger.info(f"Audio playback completed for call {call_id}")
    
    async def stream_tts(self, call_id: str, text: str):
        """
        Generate and stream TTS audio to the call.
        
        Args:
            call_id: ID of the call
            text: Text to convert to speech
        """
        logger.info(f"Streaming TTS to call {call_id}: {text}")
        
        # In a real implementation:
        # 1. Generate TTS audio (using piper, festival, or cloud TTS)
        # 2. Stream to Asterisk channel
        
        # For now, simulate TTS processing
        await asyncio.sleep(len(text) * 0.05)  # Simulate speech duration
        logger.info(f"TTS streaming completed for call {call_id}")
