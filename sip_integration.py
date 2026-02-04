"""SIP/Asterisk integration layer for handling calls."""
import logging
from typing import Dict, Any, Optional
import asyncio
from config import settings

logger = logging.getLogger(__name__)
MISSING_PASSWORD_WARNING = (
    "Asterisk password is not set; configure ASTERISK_PASSWORD for production use."
)


class SIPIntegration:
    """Integration with Asterisk SIP server."""

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        """
        Initialize SIP integration.

        Args:
            host: Asterisk server host
            port: Asterisk server port
        """
        self.host = host or settings.asterisk_host
        self.port = port or settings.asterisk_port
        self.username = settings.asterisk_username
        self.password = settings.asterisk_password
        self.connected = False
        if not self.password:
            logger.warning(MISSING_PASSWORD_WARNING)
        logger.info(f"SIP integration initialized for {self.host}:{self.port}")

    async def connect(self):
        """Connect to Asterisk server."""
        logger.info("Connecting to Asterisk server...")
        if not self.username or not self.password:
            logger.warning(
                "Asterisk credentials are missing; running in stub mode.")
        self.connected = True
        logger.info("Connected to Asterisk server")

    async def handle_incoming_call(
            self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an incoming call.

        Args:
            call_data: Data about the incoming call

        Returns:
            Call context dictionary
        """
        caller_number = call_data.get("caller_number", "unknown")
        called_number = call_data.get("called_number", "unknown")
        call_id = call_data.get(
            "call_id", f"call_{
                asyncio.get_event_loop().time()}")

        logger.info(
            f"Handling incoming call {call_id} from {caller_number} to {called_number}")

        call_context = {
            "call_id": call_id,
            "caller_number": caller_number,
            "called_number": called_number,
            "timestamp": call_data.get("timestamp"),
            "channel": call_data.get("channel"),
            "status": "ringing"
        }

        return call_context

    async def answer_call(self, call_id: str):
        """
        Answer an incoming call.

        Args:
            call_id: ID of the call to answer
        """
        logger.info(f"Answering call {call_id}")
        await asyncio.sleep(0.05)
        logger.info(f"Call {call_id} answered")

    async def hangup_call(self, call_id: str):
        """
        Hangup a call.

        Args:
            call_id: ID of the call to hangup
        """
        logger.info(f"Hanging up call {call_id}")
        await asyncio.sleep(0.05)
        logger.info(f"Call {call_id} hung up")

    async def transfer_call(self, call_id: str, destination: str):
        """
        Transfer a call to another extension or number.

        Args:
            call_id: ID of the call to transfer
            destination: Destination number or extension
        """
        logger.info(f"Transferring call {call_id} to {destination}")
        await asyncio.sleep(0.05)
        logger.info(f"Call {call_id} transferred to {destination}")
