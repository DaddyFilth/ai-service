"""Tests for the AI Call Service components."""
import logging
import sys
import shutil
from pathlib import Path

import pytest

from media_handler import MediaHandler, ensure_free_space
from sip_integration import SIPIntegration, MISSING_PASSWORD_WARNING
from action_router import ActionRouter
from decision_engine import DecisionEngine
from config import settings, validate_password_strength

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestPasswordValidation:
    """Test password validation functions."""

    def test_empty_password(self):
        """Test that empty password is rejected."""
        is_valid, error_msg = validate_password_strength("")
        assert not is_valid
        assert "empty" in error_msg.lower()

    def test_short_password(self):
        """Test that short password is rejected."""
        is_valid, error_msg = validate_password_strength("short")
        assert not is_valid
        assert "12 characters" in error_msg

    def test_weak_pattern_password(self):
        """Test that password with weak pattern is rejected."""
        is_valid, error_msg = validate_password_strength("password123456")
        assert not is_valid
        assert "weak pattern" in error_msg.lower()
        assert "password" in error_msg.lower()

    def test_weak_pattern_change_this(self):
        """Test that CHANGE_THIS pattern is rejected."""
        is_valid, error_msg = validate_password_strength("CHANGE_THIS_SECURE")
        assert not is_valid
        assert "weak pattern" in error_msg.lower()
        assert "change_this" in error_msg.lower()

    def test_strong_password(self):
        """Test that strong password is accepted."""
        is_valid, error_msg = validate_password_strength(
            "aB3$xZ9@mK2#pL7&qW5!")
        assert is_valid
        assert error_msg == ""

    def test_long_random_password(self):
        """Test that long random password is accepted."""
        is_valid, error_msg = validate_password_strength(
            "a1b2c3d4e5f6g7h8i9j0k1l2")
        assert is_valid
        assert error_msg == ""


class TestConfigWithPassword:
    """Test configuration with password validation."""

    def test_config_rejects_weak_password(self, monkeypatch):
        """Test that config rejects weak passwords."""
        # Clear any cached settings
        import sys
        if 'config' in sys.modules:
            del sys.modules['config']

        monkeypatch.setenv("ASTERISK_PASSWORD", "weak")
        with pytest.raises(ValueError, match="does not meet security requirements"):
            from config import Settings
            Settings()

    def test_config_accepts_strong_password(self, monkeypatch):
        """Test that config accepts strong passwords."""
        # Clear any cached settings
        import sys
        if 'config' in sys.modules:
            del sys.modules['config']

        monkeypatch.setenv("ASTERISK_PASSWORD", "aB3$xZ9@mK2#pL7&qW5!")
        from config import Settings
        settings = Settings()
        assert settings.asterisk_password == "aB3$xZ9@mK2#pL7&qW5!"

    def test_config_allows_empty_password(self, monkeypatch):
        """Test that config allows empty password (for development only)."""
        # Clear any cached settings
        import sys
        if 'config' in sys.modules:
            del sys.modules['config']

        monkeypatch.setenv("ASTERISK_PASSWORD", "")
        from config import Settings
        settings = Settings()
        assert settings.asterisk_password == ""


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
        assert MISSING_PASSWORD_WARNING in caplog.text

    def test_initialization_with_password(self, monkeypatch, caplog):
        """Test SIP integration with configured password."""
        monkeypatch.setattr(settings, "asterisk_password", "Str0ng!Passw0rd")
        with caplog.at_level(logging.WARNING):
            sip = SIPIntegration()
        assert sip.password == "Str0ng!Passw0rd"
        assert sip.username == "ai_service"
        assert MISSING_PASSWORD_WARNING not in caplog.text

    @pytest.mark.asyncio
    async def test_connect_uses_credentials(self, monkeypatch, caplog):
        """Ensure connect works with configured credentials."""
        monkeypatch.setattr(settings, "asterisk_password", "Str0ng!Passw0rd")
        with caplog.at_level(logging.INFO):
            sip = SIPIntegration()
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


class TestSecurityFeatures:
    """Test security features added to the service."""

    def test_sanitize_filename_valid(self):
        """Test that valid filenames are accepted."""
        from media_handler import sanitize_filename
        
        assert sanitize_filename("test123") == "test123"
        assert sanitize_filename("call_id_456") == "call_id_456"
        assert sanitize_filename("file.wav") == "file.wav"

    def test_sanitize_filename_path_traversal(self):
        """Test that path traversal attempts are blocked."""
        from media_handler import sanitize_filename
        
        # Path traversal attempts should be sanitized
        result = sanitize_filename("../etc/passwd")
        assert ".." not in result
        assert "/" not in result
        # Leading dots are removed, so we get "_etc_passwd"
        assert "etc_passwd" in result
        assert not result.startswith(".")

    def test_sanitize_filename_empty(self):
        """Test that empty filenames are rejected."""
        from media_handler import sanitize_filename
        
        with pytest.raises(ValueError, match="empty"):
            sanitize_filename("")

    def test_sanitize_filename_hidden_file(self):
        """Test that hidden files (starting with .) have dots removed."""
        from media_handler import sanitize_filename
        
        # Leading dots should be removed
        result = sanitize_filename(".hidden")
        assert not result.startswith(".")
        assert result == "hidden"

    def test_sanitize_path_valid(self):
        """Test that valid paths within base directory are accepted."""
        from media_handler import sanitize_path
        from pathlib import Path
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            file_path = base_dir / "test.wav"
            
            # Create the file
            file_path.touch()
            
            # Should succeed
            result = sanitize_path(file_path, base_dir)
            assert result.is_absolute()

    def test_sanitize_path_traversal(self):
        """Test that path traversal attempts are blocked."""
        from media_handler import sanitize_path
        from pathlib import Path
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir) / "recordings"
            base_dir.mkdir()
            
            # Try to escape the base directory
            escape_path = base_dir / ".." / ".." / "etc" / "passwd"
            
            with pytest.raises(ValueError, match="Path traversal detected"):
                sanitize_path(escape_path, base_dir)

    @pytest.mark.asyncio
    async def test_media_handler_call_id_sanitization(self):
        """Test that MediaHandler sanitizes call IDs."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = MediaHandler(recordings_dir=tmpdir)
            
            # Try to use path traversal in call_id
            malicious_call_id = "../../../etc/passwd"
            
            # Should not raise an error, but should sanitize the path
            audio_file = await handler.capture_audio_stream(
                call_id=malicious_call_id,
                duration=1
            )
            
            # Verify the file is in the recordings directory
            audio_path = Path(audio_file)
            assert audio_path.parent == handler.recordings_dir.resolve()
            assert ".." not in audio_file
            assert "/etc/" not in audio_file

    @pytest.mark.asyncio
    async def test_media_handler_tts_call_id_sanitization(self):
        """Test that stream_tts sanitizes call IDs."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = MediaHandler(recordings_dir=tmpdir)
            
            # Try to use path traversal in call_id
            malicious_call_id = "../../../tmp/malicious"
            
            # Should sanitize the call_id
            await handler.stream_tts(call_id=malicious_call_id, text="Test message")
            
            # Verify files are created in the correct location
            tmpdir_path = Path(tmpdir).resolve()
            
            # Check that files exist in tmpdir
            wav_files = list(tmpdir_path.glob("*.wav"))
            assert len(wav_files) > 0, "No wav files created"
            
            # Verify all files are in tmpdir and have sanitized names
            for file in wav_files:
                # Should be directly in tmpdir, not in subdirectories
                assert file.parent == tmpdir_path, f"File {file} not in recordings directory"
                # Should not contain path traversal patterns
                assert ".." not in file.name, f"Filename contains '..': {file.name}"
                assert "/" not in file.name, f"Filename contains '/': {file.name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
