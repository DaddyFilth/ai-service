"""Tests for the AI Call Service components."""
import logging
import pytest
import asyncio
from pathlib import Path
import sys
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from decision_engine import DecisionEngine
from action_router import ActionRouter
from sip_integration import SIPIntegration
from media_handler import MediaHandler, ensure_free_space


class TestDecisionEngine:
    """Test the AI decision engine."""
    
    def test_initialization(self):
        """Test that decision engine initializes correctly."""
        engine = DecisionEngine()
        assert engine is not None
        assert engine.model is not None
    
    def test_parse_decision_forward(self):
        """Test parsing a forward decision."""
        engine = DecisionEngine()
        decision = engine._parse_decision("forward to sales", "original text")
        assert decision["action"] == "forward"
    
    def test_parse_decision_voicemail(self):
        """Test parsing a voicemail decision."""
        engine = DecisionEngine()
        decision = engine._parse_decision("leave a voicemail", "original text")
        assert decision["action"] == "voicemail"
    
    def test_parse_decision_ask_question(self):
        """Test parsing an ask question decision."""
        engine = DecisionEngine()
        decision = engine._parse_decision("ask them more", "original text")
        assert decision["action"] == "ask_question"


class TestActionRouter:
    """Test the action router."""
    
    def test_initialization(self):
        """Test that action router initializes correctly."""
        router = ActionRouter()
        assert router is not None
        assert router.recordings_dir.exists()
    
    @pytest.mark.asyncio
    async def test_forward_call(self):
        """Test forwarding a call."""
        router = ActionRouter()
        call_context = {"call_id": "test_001"}
        parameters = {"destination": "100"}
        
        result = await router.forward_call(call_context, parameters)
        assert result["action"] == "forward"
        assert result["status"] == "success"
        assert result["destination"] == "100"
    
    @pytest.mark.asyncio
    async def test_record_voicemail(self):
        """Test recording voicemail."""
        router = ActionRouter(min_free_space_mb=0)
        call_context = {"call_id": "test_002"}
        parameters = {}
        
        result = await router.record_voicemail(call_context, parameters)
        assert result["action"] == "voicemail"
        assert result["status"] == "recording"
        assert "filepath" in result
    
    @pytest.mark.asyncio
    async def test_ask_question(self):
        """Test asking a question."""
        router = ActionRouter()
        call_context = {"call_id": "test_003"}
        parameters = {"question": "How can I help you?"}
        
        result = await router.ask_question(call_context, parameters)
        assert result["action"] == "ask_question"
        assert result["status"] == "playing"
        assert result["question"] == "How can I help you?"


class TestSIPIntegration:
    """Test SIP integration."""
    
    def test_initialization(self, caplog):
        """Test SIP integration initialization."""
        with caplog.at_level(logging.WARNING):
            sip = SIPIntegration()
        assert sip is not None
        assert sip.host is not None
        assert sip.port is not None
        assert sip.username == "ai_service"
        assert sip.password == ""
        assert sip.connected is False
        assert "Asterisk password is not set" in caplog.text

    @pytest.mark.asyncio
    async def test_initialization_with_password(self, monkeypatch, caplog):
        """Test SIP integration with configured password."""
        monkeypatch.setattr(settings, "asterisk_password", "Str0ng!Passw0rd")
        with caplog.at_level(logging.WARNING):
            sip = SIPIntegration()
        assert sip.password == "Str0ng!Passw0rd"
        assert sip.username == "ai_service"
        assert "Asterisk password is not set" not in caplog.text
        await sip.connect()
        assert sip.connected is True

    def test_initialization_with_username(self, monkeypatch):
        """Test SIP integration with configured username."""
        monkeypatch.setattr(settings, "asterisk_username", "custom_user")
        sip = SIPIntegration()
        assert sip.username == "custom_user"
    
    @pytest.mark.asyncio
    async def test_handle_incoming_call(self):
        """Test handling an incoming call."""
        sip = SIPIntegration()
        call_data = {
            "call_id": "test_call",
            "caller_number": "+1234567890",
            "called_number": "+0987654321"
        }
        
        context = await sip.handle_incoming_call(call_data)
        assert context["call_id"] == "test_call"
        assert context["caller_number"] == "+1234567890"
        assert context["status"] == "ringing"


class TestMediaHandler:
    """Test media handler."""
    
    def test_initialization(self):
        """Test media handler initialization."""
        media = MediaHandler()
        assert media is not None
        assert media.recordings_dir.exists()
    
    @pytest.mark.asyncio
    async def test_stream_tts(self):
        """Test TTS streaming."""
        media = MediaHandler()
        # This should complete without errors
        await media.stream_tts("test_call", "Hello world")

    def test_disk_space_guard_allows(self):
        """Ensure disk space guard allows when requirement is zero."""
        media = MediaHandler()
        ensure_free_space(media.recordings_dir, 0)

    def test_disk_space_guard_blocks(self):
        """Ensure disk space guard blocks if requirement exceeds free space."""
        media = MediaHandler()
        free_bytes = shutil.disk_usage(media.recordings_dir).free
        required_mb = (free_bytes // (1024 * 1024)) + 1
        with pytest.raises(RuntimeError, match=r"Insufficient disk space"):
            ensure_free_space(media.recordings_dir, required_mb)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
