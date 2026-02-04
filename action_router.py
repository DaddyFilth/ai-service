"""Action router for handling call actions based on AI decisions."""
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from config import settings
from media_handler import ensure_free_space

logger = logging.getLogger(__name__)


class ActionRouter:
    """Routes calls to different actions based on AI decisions."""

    def __init__(
        self,
        recordings_dir: str = "./recordings",
        min_free_space_mb: Optional[int] = None,
        sip_integration: Optional[Any] = None,
        media_handler: Optional[Any] = None,
    ):
        """
        Initialize the action router.

        Args:
            recordings_dir: Directory for storing recordings
            min_free_space_mb: Minimum free disk space required in megabytes
        """
        self.recordings_dir = Path(recordings_dir)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        self.min_free_space_mb = (
            min_free_space_mb if min_free_space_mb is not None else settings.min_free_space_mb)
        self.sip_integration = sip_integration
        self.media_handler = media_handler
        if self.min_free_space_mb < 0:
            raise ValueError("min_free_space_mb must be >= 0")
        logger.info(
            f"Action router initialized with recordings dir: {
                self.recordings_dir}")

    async def route_action(
            self, decision: Dict[str, Any], call_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route to the appropriate action based on decision.

        Args:
            decision: Decision from the decision engine
            call_context: Context about the current call

        Returns:
            Result of the action
        """
        action = decision.get("action", "ask_question")
        parameters = decision.get("parameters", {})

        logger.info(f"Routing to action: {action}")

        if action == "forward":
            return await self.forward_call(call_context, parameters)
        elif action == "voicemail":
            return await self.record_voicemail(call_context, parameters)
        elif action == "ask_question":
            return await self.ask_question(call_context, parameters)
        else:
            logger.warning(
                f"Unknown action: {action}, defaulting to ask_question")
            return await self.ask_question(call_context, {})

    async def forward_call(
            self,
            call_context: Dict[str, Any],
            parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Forward the call to another number or extension.

        Args:
            call_context: Current call context
            parameters: Forward parameters (e.g., destination number)

        Returns:
            Result of forwarding action
        """
        destination = parameters.get(
            "destination", call_context.get(
                "default_forward_number", "100"))

        logger.info(
            f"Forwarding call {
                call_context.get('call_id')} to {destination}")

        if self.sip_integration:
            await self.sip_integration.transfer_call(call_context.get("call_id"), destination)
        result = {
            "action": "forward",
            "status": "success",
            "destination": destination,
            "call_id": call_context.get("call_id"),
            "message": f"Call forwarded to {destination}"
        }

        return result

    async def record_voicemail(
            self, call_context: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record a voicemail message.

        Args:
            call_context: Current call context
            parameters: Recording parameters

        Returns:
            Result of recording action
        """
        ensure_free_space(self.recordings_dir, self.min_free_space_mb)
        call_id = call_context.get("call_id", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voicemail_{call_id}_{timestamp}.wav"
        filepath = self.recordings_dir / filename

        logger.info(f"Recording voicemail for call {call_id} to {filepath}")

        greeting = parameters.get("greeting",
                                  "Please leave a message after the beep.")
        if self.media_handler:
            await self.media_handler.stream_tts(call_id, greeting)
            await self.media_handler.capture_audio_stream(call_id, duration=30)
            await self.media_handler.stop_capture(call_id)
        result = {
            "action": "voicemail",
            "status": "recorded" if self.media_handler else "recording",
            "filepath": str(filepath),
            "call_id": call_id,
            "message": (
                "Voicemail recorded" if self.media_handler
                else "Recording voicemail message"),
            "greeting": greeting}

        return result

    async def ask_question(
            self,
            call_context: Dict[str, Any],
            parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ask the caller a question using TTS.

        Args:
            call_context: Current call context
            parameters: Question parameters

        Returns:
            Result of TTS action
        """
        question = parameters.get("question", "How can I help you today?")
        call_id = call_context.get("call_id", "unknown")

        logger.info(f"Asking question to call {call_id}: {question}")

        status = "playing"
        message = f"Playing TTS: {question}"
        if self.media_handler:
            await self.media_handler.stream_tts(call_id, question)
        result = {
            "action": "ask_question",
            "status": status,
            "question": question,
            "call_id": call_id,
            "message": message,
            "next_action": "wait_for_response"
        }

        return result
