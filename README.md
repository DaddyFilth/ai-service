# AI Call Service

A self-hosted PBX with AI call screening using VoIP/WebRTC with zero carrier costs.

## Overview

This service provides intelligent call routing and screening using AI. It integrates with Asterisk for SIP/VoIP handling and uses AI models for call analysis and decision making.

## Architecture

```
Caller (SIP/WebRTC)
        ↓
   SIP Server (Asterisk)
        ↓
   Media (RTP)
        ↓
   STT (Whisper)
        ↓
   Ollama (Decision Engine)
        ↓
   Action Router
   ├── Forward (SIP)
   ├── Voicemail (Record)
   └── Ask Question (TTS)
```

## Features

- **SIP/WebRTC Integration**: Handle incoming calls via Asterisk
- **Speech-to-Text**: Transcribe caller speech using OpenAI Whisper
- **AI Decision Engine**: Analyze calls using Ollama for intelligent routing
- **Action Router**: Three routing options:
  - **Forward**: Route calls to specific extensions/numbers
  - **Voicemail**: Record messages
  - **Ask Question**: Interactive TTS-based conversation

## Requirements

- Python 3.8+
- Asterisk PBX (for production SIP handling)
- Ollama (for AI decision engine)
- FFmpeg (for audio processing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/DaddyFilth/ai-service.git
cd ai-service
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Optional (for Whisper STT and audio capture):
```bash
pip install -r requirements-optional.txt
```

3. Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Install and start Ollama:
```bash
# Follow instructions at https://ollama.ai
ollama pull llama2
```

## Configuration

Edit `.env` file with your settings:

- `ASTERISK_HOST`: Your Asterisk server address
- `ASTERISK_PORT`: SIP port (default: 5060)
- `OLLAMA_HOST`: Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL`: AI model to use (default: llama2)
- `SERVICE_PORT`: API server port (default: 8000)

## Usage

### Running the Service

#### As a standalone script:
```bash
python main.py
```

#### As a web API:
```bash
python api.py
# or
uvicorn api:app --host 0.0.0.0 --port 8000
```

### Testing the API

Once running, you can test the service:

```bash
# Health check
curl http://localhost:8000/health

# Simulate an incoming call
curl -X POST http://localhost:8000/call/incoming \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "test_001",
    "caller_number": "+1234567890",
    "called_number": "+0987654321"
  }'
```

## Components

### SIP Integration (`sip_integration.py`)
Handles communication with Asterisk SIP server for call control.

### Media Handler (`media_handler.py`)
Manages RTP audio streams, recording, and playback.

### STT Service (`stt_service.py`)
Speech-to-text transcription using OpenAI Whisper.

### Decision Engine (`decision_engine.py`)
AI-powered call analysis using Ollama to determine routing actions.

### Action Router (`action_router.py`)
Routes calls based on AI decisions to:
- Forward calls
- Record voicemails
- Ask interactive questions

## Integration with Asterisk

For production deployment, configure Asterisk to send call events to this service:

1. Install Asterisk with ARI (Asterisk REST Interface)
2. Configure ARI in `/etc/asterisk/ari.conf`
3. Set up dialplan to route calls through this service
4. Configure webhooks or use ARI WebSocket for real-time events

## Development

The service is modular and each component can be tested independently:

```bash
# Test STT service
python -c "from stt_service import STTService; stt = STTService(); print(stt)"

# Test decision engine
python -c "from decision_engine import DecisionEngine; engine = DecisionEngine(); print(engine)"
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Roadmap

- [ ] Full Asterisk ARI integration
- [ ] WebRTC browser-based calling
- [ ] Advanced TTS with multiple voices
- [ ] Call analytics dashboard
- [ ] Multi-language support
- [ ] Custom AI model training
