# Copilot Instructions for AI Call Service

## Project Overview

This is an AI-powered call screening service that provides intelligent call routing using VoIP/SIP integration with Asterisk, speech-to-text (Whisper), and AI decision-making (Ollama). The service can forward calls, record voicemails, or ask interactive questions based on AI analysis of caller intent.

**Architecture Flow:**
```
Caller (SIP/WebRTC) → Asterisk (SIP Server) → Media (RTP) → 
Whisper (STT) → Ollama (Decision Engine) → Action Router 
├── Forward (SIP)
├── Voicemail (Record)
└── Ask Question (TTS)
```

## Project Structure

```
ai-service/
├── config.py                      # Configuration management (Pydantic)
├── sip_integration.py            # Asterisk/SIP integration
├── media_handler.py              # RTP audio handling, recording, TTS
├── stt_service.py                # Speech-to-text (Whisper)
├── decision_engine.py            # AI decision-making (Ollama)
├── action_router.py              # Action routing (Forward/Voicemail/TTS)
├── main.py                       # Main orchestrator
├── api.py                        # REST API server (aiohttp)
├── asterisk_config_generator.py  # Generate Asterisk configs
├── demo.py                       # Demo/example script
├── test_service.py               # Unit tests
├── verify.py                     # Component verification with imports
├── verify_structure.py           # Structure verification (no imports)
├── requirements.txt              # Python dependencies
├── setup.sh                      # Setup script
├── .env.example                  # Environment template
└── android-app/                  # Android client app
    └── [Android project files]
```

## Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run setup script (creates .env, installs dependencies)
./setup.sh

# Generate Asterisk configuration files
python asterisk_config_generator.py
```

### Running the Service
```bash
# Run as standalone script
python main.py

# Run as REST API server
python api.py

# Run demo/test flow
python demo.py
```

### Testing
```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest test_service.py

# Run async tests
pytest -v --asyncio-mode=auto

# Verify component structure (no imports)
python verify_structure.py

# Verify components (with imports)
python verify.py
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Simulate incoming call
curl -X POST http://localhost:8000/call/incoming \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "test_001",
    "caller_number": "+1234567890",
    "called_number": "+0987654321"
  }'

# Check call status
curl http://localhost:8000/call/{call_id}/status
```

### Android App
```bash
# Build Android app
cd android-app
./gradlew assembleDebug

# Install on device
adb install app/build/outputs/apk/debug/app-debug.apk
```

## Code Conventions

### Python Style
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Use async/await for asynchronous operations
- Use Pydantic for configuration and data validation
- Use descriptive variable and function names
- Keep functions focused and modular

### Async Patterns
- All I/O operations should be async
- Use `asyncio` for concurrent operations
- Use `aiofiles` for file I/O
- Use `aiohttp` for HTTP operations

### Error Handling
- Use try/except blocks for external service calls
- Provide fallback mechanisms for failures
- Log errors with appropriate context
- Return meaningful error messages

### Logging
- Use Python's logging module
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Include contextual information (call_id, caller_number, etc.)

### Example Code Style
```python
from typing import Dict, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

async def process_call(call_id: str, caller_number: str) -> Dict[str, str]:
    """
    Process an incoming call.
    
    Args:
        call_id: Unique call identifier
        caller_number: Caller's phone number
        
    Returns:
        Dictionary with action and details
    """
    try:
        # Implementation
        result = await some_async_operation()
        logger.info(f"Call {call_id} processed successfully")
        return result
    except Exception as e:
        logger.error(f"Error processing call {call_id}: {e}")
        raise
```

## Testing Expectations

### Test Coverage
- Write tests for all new components
- Use pytest for test framework
- Use pytest-asyncio for async tests
- Mock external services (Asterisk, Ollama, Whisper)
- Test error conditions and edge cases

### Test Structure
```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_component_function():
    """Test description."""
    # Arrange
    component = ComponentClass()
    
    # Act
    result = await component.method()
    
    # Assert
    assert result == expected_value
```

### Test Files
- Name test files as `test_*.py`
- Place tests in the same directory or in a `tests/` folder
- Each component should have corresponding tests

## Configuration

### Environment Variables
Configuration is managed through `.env` file (use `.env.example` as template):

**Required:**
- `ASTERISK_HOST`: Asterisk server address
- `ASTERISK_PORT`: SIP port (default: 5060)
- `OLLAMA_HOST`: Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL`: AI model name (default: llama2)

**Optional:**
- `SERVICE_PORT`: API server port (default: 8000)
- `MIN_FREE_SPACE_MB`: Min disk space for recordings (default: 100)
- `WHISPER_MODEL`: Whisper model size (default: base)
- `RECORDINGS_DIR`: Directory for recordings (default: recordings/)

### Configuration Loading
All configuration uses `config.py` with Pydantic models:
```python
from config import get_config

config = get_config()
# Access: config.asterisk_host, config.ollama_model, etc.
```

## Dependencies

### Core Dependencies
- `aiohttp`: Async HTTP client/server
- `pydantic`: Data validation and settings
- `python-dotenv`: Environment variable management
- `asyncio`: Async I/O support

### Service Integration
- `requests`: HTTP client for Ollama
- `websockets`: WebSocket support for Asterisk
- `ollama`: Ollama Python client

### Audio Processing
- `pydub`: Audio manipulation
- FFmpeg (system dependency)

### Testing
- `pytest`: Test framework
- `pytest-asyncio`: Async test support

## External Services

### Asterisk (SIP Server)
- Handles SIP/VoIP calls
- Requires ARI (Asterisk REST Interface) configuration
- WebSocket events for real-time call updates
- Configuration files can be generated with `asterisk_config_generator.py`

### Ollama (AI Engine)
- Local LLM server for decision-making
- Install: https://ollama.com/download
- Pull model: `ollama pull llama2`
- Default endpoint: http://localhost:11434

### Whisper (Speech-to-Text)
- OpenAI Whisper for transcription
- Models: tiny, base, small, medium, large
- Runs locally (no API key needed)

## Boundaries and Constraints

### DO NOT Modify
- `.env` file (contains secrets) - use `.env.example` instead
- Asterisk production configurations without backup
- Recording files in `recordings/` directory
- Android app permissions without security review

### DO NOT Commit
- `.env` file (use `.env.example` as template)
- Audio recordings (*.wav files in recordings/)
- Asterisk passwords or credentials
- API keys or secrets
- Build artifacts (`__pycache__`, `*.pyc`)
- Virtual environment directories (`venv/`, `env/`)

### Security Considerations
- Never log passwords or sensitive credentials
- Validate all external inputs (phone numbers, call IDs)
- Sanitize file paths to prevent directory traversal
- Rate limit API endpoints
- Use secure WebSocket connections (wss://) in production

## Git Workflow

### Branch Naming
- Feature branches: `feature/description`
- AI-assisted changes: `copilot/description` (branches created when using GitHub Copilot coding agent)
- Bug fixes: `fix/description`
- Documentation: `docs/description`

### Commit Messages
- Use clear, descriptive commit messages
- Start with verb in present tense (Add, Fix, Update, Remove)
- Include context (component or file affected)
- Examples:
  - "Add voicemail recording functionality"
  - "Fix async timeout in decision engine"
  - "Update README with installation steps"

### Pull Requests
- Include clear description of changes
- Reference related issues
- Ensure all tests pass
- Update documentation if needed
- No merge conflicts

## Common Development Tasks

### Adding a New Action
1. Add action type to `decision_engine.py` decision types
2. Implement handler in `action_router.py`
3. Update tests in `test_service.py`
4. Document in README.md

### Adding a New AI Model
1. Update `OLLAMA_MODEL` in `.env`
2. Pull model: `ollama pull model-name`
3. Test decision accuracy
4. Update documentation

### Debugging Call Flow
1. Enable DEBUG logging in config
2. Run `python demo.py` to simulate calls
3. Check logs for each component step
4. Use `verify.py` to test individual components

## Architecture Notes

### Modular Design
Each component is independent and can be:
- Tested separately
- Replaced with alternatives
- Extended with new features
- Configured independently

### Key Integration Points
- **SIP → Media**: Audio streaming
- **Media → STT**: Audio transcription
- **STT → Decision Engine**: Intent analysis
- **Decision Engine → Action Router**: Execute actions
- **Action Router → SIP/Media**: Call control

### Async Flow
All operations use asyncio for non-blocking I/O:
1. Answer call (async)
2. Capture audio stream (async)
3. Transcribe audio (async)
4. Get AI decision (async)
5. Execute action (async)

## Documentation

### Where to Find Information
- **README.md**: Project overview, features, quick start
- **ARCHITECTURE.md**: Detailed architecture and call flow
- **INSTALLATION.md**: Complete installation guide
- **USAGE.md**: Comprehensive usage guide
- **PROJECT_SUMMARY.md**: What was built, file descriptions
- **android-app/**: Android client documentation

### When to Update Docs
- New features: Update README.md and USAGE.md
- Architecture changes: Update ARCHITECTURE.md
- Installation changes: Update INSTALLATION.md
- API changes: Update usage examples

## Performance Considerations

### Audio Processing
- Use appropriate Whisper model (base for speed, large for accuracy)
- Consider disk space for recordings (check `MIN_FREE_SPACE_MB`)
- Clean up old recordings periodically

### AI Decision Making
- Ollama response times vary by model size
- Consider timeout settings for production
- Cache common decisions if applicable

### Concurrent Calls
- Service supports multiple concurrent calls
- Monitor system resources (CPU, memory, disk)
- Consider load balancing for high volume

## Helpful Tips

- Run `verify_structure.py` to check code structure without importing
- Use `demo.py` to test the complete call flow
- Check `test_service.py` for examples of mocking external services
- Review `.env.example` for all configuration options
- The Android app in `android-app/` provides a complete client example
