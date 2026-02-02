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
- **Android Client App**: Connect to the AI service from your Android device

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
- `MIN_FREE_SPACE_MB`: Minimum free disk space for recordings (default: 100 MB)

## Usage

### Running the Service

#### As a standalone script:
```bash
python main.py
```

#### As a web API:
```bash
python api.py
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

### Automatic Configuration (Recommended)

Generate Asterisk configuration files automatically:

```bash
# Generate configuration files
python asterisk_config_generator.py

# Or specify custom output directory
python asterisk_config_generator.py -o /path/to/output

# Install the generated configurations
cd asterisk-configs
sudo bash install_configs.sh
```

The auto-config generator creates:
- `ari.conf` - REST API configuration
- `http.conf` - HTTP server settings
- `extensions.conf` - Call routing dialplan
- `pjsip.conf` - SIP endpoint configuration
- Installation script with automatic backup

### Manual Configuration

For production deployment, manually configure Asterisk:

1. Install Asterisk with ARI (Asterisk REST Interface)
2. Configure ARI in `/etc/asterisk/ari.conf`
3. Set up dialplan to route calls through this service
4. Configure webhooks or use ARI WebSocket for real-time events

See [INSTALLATION.md](INSTALLATION.md) for detailed manual configuration instructions.

## Development

The service is modular and each component can be tested independently:

```bash
# Test STT service
python -c "from stt_service import STTService; stt = STTService(); print(stt)"

# Test decision engine
python -c "from decision_engine import DecisionEngine; engine = DecisionEngine(); print(engine)"
```

## Android Client App

An Android application is included to connect to the AI service from mobile devices. This allows you to:
- Test the service remotely
- Simulate calls from your Android device
- Monitor service health

### Building the Android App

See [android-app/README.md](android-app/README.md) for detailed instructions on:
- Building the APK
- Installing on your device
- Configuring network settings
- Using the app to connect to your AI service

Quick start:
```bash
cd android-app
./gradlew assembleDebug
# APK will be at: app/build/outputs/apk/debug/app-debug.apk
```

For more details, see [android-app/BUILD_GUIDE.md](android-app/BUILD_GUIDE.md)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Roadmap

- [x] Android client app for remote connection
- [ ] Full Asterisk ARI integration
- [ ] WebRTC browser-based calling
- [ ] Advanced TTS with multiple voices
- [ ] Call analytics dashboard
- [ ] Multi-language support
- [ ] Custom AI model training
