"""Main AI service orchestrator that ties all components together."""
import logging
from typing import Dict, Any, Optional
import asyncio
from pathlib import Path

from sip_integration import SIPIntegration
from media_handler import MediaHandler
from stt_service import STTService
from decision_engine import DecisionEngine
from action_router import ActionRouter
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AICallService:
    """Main AI call screening service."""
    
    def __init__(self):
        """Initialize the AI call service with all components."""
        logger.info("Initializing AI Call Service")
        
        # Initialize all components
        self.sip = SIPIntegration()
        self.media = MediaHandler(settings.recordings_dir)
        self.stt = STTService()
        self.decision_engine = DecisionEngine()
        self.action_router = ActionRouter(
            settings.recordings_dir,
            min_free_space_mb=settings.min_free_space_mb,
            sip_integration=self.sip,
            media_handler=self.media,
        )
        
        logger.info("All components initialized")
    
    async def start(self):
        """Start the AI call service."""
        logger.info("Starting AI Call Service")
        await self.sip.connect()
        logger.info("AI Call Service is running")
    
    async def handle_call(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a complete call flow through the AI service.
        
        This implements the full flow:
        Caller → SIP Server → Media (RTP) → STT → Ollama → Action Router
        
        Args:
            call_data: Incoming call data
            
        Returns:
            Final result of the call handling
        """
        call_id = call_data.get("call_id", "unknown")
        logger.info(f"=== Starting call handling for {call_id} ===")
        
        try:
            # Step 1: SIP Server - Handle incoming call
            logger.info("Step 1: SIP Server - Handling incoming call")
            call_context = await self.sip.handle_incoming_call(call_data)
            await self.sip.answer_call(call_context["call_id"])
            
            # Step 2: Media (RTP) - Capture audio stream
            logger.info("Step 2: Media (RTP) - Capturing audio stream")
            # Play greeting first
            await self.media.stream_tts(call_context["call_id"], "Hello, please state your reason for calling.")
            
            # Capture caller's response
            audio_file = await self.media.capture_audio_stream(
                call_context["call_id"],
                duration=5
            )
            
            # Step 3: STT (Whisper) - Convert speech to text
            logger.info("Step 3: STT (Whisper) - Transcribing audio")
            transcribed_text = self.stt.transcribe(audio_file)
            logger.info(f"Transcribed: {transcribed_text}")
            
            # Step 4: Ollama (Decision Engine) - Analyze and decide action
            logger.info("Step 4: Ollama - Analyzing call and making decision")
            decision = self.decision_engine.analyze_call(transcribed_text, call_context)
            logger.info(f"Decision: {decision}")
            
            # Step 5: Action Router - Execute the decision
            logger.info("Step 5: Action Router - Executing action")
            result = await self.action_router.route_action(decision, call_context)
            logger.info(f"Action result: {result}")
            
            # Handle the specific action
            if result["action"] == "forward":
                await self.sip.transfer_call(call_context["call_id"], result["destination"])
            elif result["action"] == "voicemail":
                await self.media.stream_tts(call_context["call_id"], result["greeting"])
                # Continue recording voicemail
                await self.media.capture_audio_stream(
                    call_context["call_id"],
                    duration=30
                )
                await self.sip.hangup_call(call_context["call_id"])
            elif result["action"] == "ask_question":
                await self.media.stream_tts(call_context["call_id"], result["question"])
                # This could loop back to capture more audio and re-analyze
            
            logger.info(f"=== Call handling completed for {call_id} ===")
            return result
            
        except Exception as e:
            logger.error(f"Error handling call {call_id}: {e}", exc_info=True)
            # Try to gracefully end the call
            try:
                await self.sip.hangup_call(call_context.get("call_id", call_id))
            except:
                pass
            return {
                "status": "error",
                "error": str(e),
                "call_id": call_id
            }
    
    async def stop(self):
        """Stop the AI call service."""
        logger.info("Stopping AI Call Service")
        # Clean up resources
        logger.info("AI Call Service stopped")


async def main():
    """Main entry point for the AI call service."""
    service = AICallService()
    await service.start()
    
    # Example call data (in production this would come from Asterisk events)
    example_call = {
        "call_id": "call_001",
        "caller_number": "+1234567890",
        "called_number": "+0987654321",
        "timestamp": "2026-02-01T14:19:20Z",
        "channel": "SIP/trunk-00000001"
    }
    
    # Handle the example call
    result = await service.handle_call(example_call)
    logger.info(f"Final result: {result}")
    
    await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
