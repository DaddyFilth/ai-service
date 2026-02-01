# Architecture Documentation

## System Flow

This document describes the complete call flow through the AI service.

## Components

### 1. Caller (SIP/WebRTC)
- Entry point for incoming calls
- Supports SIP and WebRTC protocols
- Connects to the SIP Server

### 2. SIP Server (Asterisk)
**Implementation**: `sip_integration.py`

Responsibilities:
- Handle SIP signaling (INVITE, ACK, BYE, etc.)
- Manage call state
- Bridge media streams
- Execute call control actions (answer, hangup, transfer)

Key Methods:
- `handle_incoming_call()`: Process new call
- `answer_call()`: Answer incoming call
- `hangup_call()`: Terminate call
- `transfer_call()`: Forward to another destination

### 3. Media (RTP)
**Implementation**: `media_handler.py`

Responsibilities:
- Capture RTP audio streams
- Record audio to files
- Play audio back to callers
- Generate and stream TTS

Key Methods:
- `capture_audio_stream()`: Record caller audio
- `play_audio()`: Play pre-recorded audio
- `stream_tts()`: Convert text to speech and play

### 4. STT (Whisper)
**Implementation**: `stt_service.py`

Responsibilities:
- Transcribe audio to text using OpenAI Whisper
- Support multiple languages
- Handle various audio formats

Models available:
- tiny: Fastest, least accurate
- base: Good balance (default)
- small: Better accuracy
- medium: High accuracy
- large: Highest accuracy, slowest

Key Methods:
- `transcribe()`: Convert audio file to text
- `transcribe_chunk()`: Detailed transcription with timestamps

### 5. Ollama (Decision Engine)
**Implementation**: `decision_engine.py`

Responsibilities:
- Analyze transcribed call content
- Make intelligent routing decisions
- Provide reasoning for decisions

Decision Types:
- **forward**: Route call to another number
- **voicemail**: Record a message
- **ask_question**: Gather more information

Key Methods:
- `analyze_call()`: Process transcription and return decision
- `_build_prompt()`: Create AI prompt from call data
- `_parse_decision()`: Extract structured decision from AI response

### 6. Action Router
**Implementation**: `action_router.py`

Responsibilities:
- Execute actions based on AI decisions
- Coordinate with SIP and Media components
- Track action results

Actions:

#### Forward (SIP)
- Transfer call to another extension/number
- Supports blind and attended transfers
- Logs forwarding actions

#### Voicemail (Record)
- Play greeting message
- Record caller message
- Save to configurable directory
- Timestamp recordings

#### Ask Question (TTS)
- Generate speech from text
- Play to caller
- Wait for response
- Can trigger new STT cycle

## Call Flow Example

```
1. Caller dials in
   └─> SIP Server receives INVITE

2. SIP Server answers call
   └─> Media starts RTP stream

3. Play greeting via TTS
   └─> "Hello, please state your reason for calling"

4. Capture caller response
   └─> Record 5 seconds of audio
   └─> Save to recordings/audio_call_001_20260201_141920.wav

5. Transcribe audio
   └─> STT: "I need to speak with the sales department"

6. AI analyzes intent
   └─> Decision Engine: "forward to sales extension"
   └─> Action: "forward", Destination: "100"

7. Execute action
   └─> Action Router forwards call
   └─> SIP transfers to extension 100

8. Call connected
   └─> Caller speaking with sales
```

## Error Handling

Each component includes error handling:

- **SIP errors**: Gracefully hangup call
- **Media errors**: Log and continue with defaults
- **STT errors**: Ask caller to repeat
- **AI errors**: Default to asking a question
- **Router errors**: Fallback to voicemail

## Extensibility

The modular design allows easy extension:

1. **New Actions**: Add to `ActionRouter.route_action()`
2. **New AI Models**: Swap `ollama` for other LLM providers
3. **New STT Engines**: Replace Whisper with alternatives
4. **Custom TTS**: Implement different TTS engines

## Configuration

All components use centralized configuration via `config.py`:

- Environment variables via `.env`
- Pydantic validation
- Type safety
- Default values

## API Integration

The `api.py` provides REST API endpoints:

- `POST /call/incoming`: Handle new calls
- `GET /call/{id}/status`: Check call status
- `GET /health`: Service health check

This allows Asterisk or other systems to trigger call handling via HTTP webhooks.
