# Usage Guide

## Running the AI Call Service

### Basic Usage

1. **Start Ollama** (in a separate terminal):
```bash
ollama serve
```

2. **Run the AI Service**:
```bash
# Activate virtual environment
source venv/bin/activate

# Option 1: Standalone mode
python main.py

# Option 2: API server mode
python api.py
```

3. **Test with demo**:
```bash
python demo.py
```

## Call Flow

When a call comes in, the service follows this flow:

```
1. Incoming Call → SIP Integration receives call
2. Answer Call → Service answers and plays greeting
3. Capture Audio → Records caller's speech (5 seconds)
4. Transcribe → Whisper converts speech to text
5. Analyze → Ollama decides on action
6. Route → Execute one of three actions:
   - Forward to extension/number
   - Record voicemail
   - Ask question and gather more info
```

## API Endpoints

### GET /
Root endpoint - Service information
```bash
curl http://localhost:8000/
```

Response:
```json
{
  "service": "AI Call Service",
  "version": "1.0.0",
  "status": "running"
}
```

### GET /health
Health check - Component status
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "components": {
    "sip": true,
    "stt": true,
    "decision_engine": true,
    "action_router": true
  }
}
```

### POST /call/incoming
Handle incoming call
```bash
curl -X POST http://localhost:8000/call/incoming \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "call_12345",
    "caller_number": "+1234567890",
    "called_number": "+0987654321",
    "timestamp": "2026-02-01T14:19:20Z",
    "channel": "SIP/trunk-00000001"
  }'
```

Response:
```json
{
  "status": "success",
  "call_id": "call_12345",
  "action": "forward",
  "message": "Call forwarded to 100"
}
```

### GET /call/{call_id}/status
Get call status
```bash
curl http://localhost:8000/call/call_12345/status
```

## Customizing AI Behavior

### Modifying Decision Logic

Edit `decision_engine.py` to customize how the AI makes decisions:

```python
# In decision_engine.py, modify the system prompt:
{
    "role": "system",
    "content": "You are an AI call routing assistant. [Customize this prompt]"
}
```

### Example Custom Prompts

**For Business Hours Routing**:
```python
"content": "You are a business receptionist AI. During business hours (9-5), forward sales calls to extension 100, support to 200. After hours, take voicemails. Always be polite."
```

**For Medical Office**:
```python
"content": "You are a medical office assistant. Emergencies should be forwarded to on-call (911). Appointment requests go to voicemail. General questions can be answered via TTS."
```

**For Restaurant**:
```python
"content": "You are a restaurant host AI. Reservations should be recorded as voicemail with name, party size, date, and time. Delivery orders forward to kitchen (101). General inquiries get answered."
```

### Changing Whisper Model

For better accuracy, use a larger model:

```python
# In main.py or stt_service.py initialization:
self.stt = STTService(model_name="medium")  # or "large"
```

Models:
- `tiny` - Fastest, least accurate
- `base` - Default, good balance
- `small` - Better accuracy
- `medium` - High accuracy
- `large` - Best accuracy, slowest

### Changing Ollama Model

For better decisions, use a different model:

```bash
# In .env file:
OLLAMA_MODEL=mistral  # Faster than llama2
# or
OLLAMA_MODEL=llama2:13b  # More capable
```

Pull new models:
```bash
ollama pull mistral
ollama pull llama2:13b
ollama pull codellama  # For technical support
```

## Integrating with Asterisk

### Asterisk Dialplan Configuration

Add to `/etc/asterisk/extensions.conf`:

```ini
[default]
; Route incoming calls through AI service
exten => _X.,1,NoOp(AI Call Screening)
  same => n,Set(CALL_ID=${UNIQUEID})
  same => n,Set(CALLER_NUM=${CALLERID(num)})
  same => n,Set(CALLED_NUM=${EXTEN})
  same => n,Answer()
  same => n,AGI(agi://localhost:8000/agi,${CALL_ID},${CALLER_NUM},${CALLED_NUM})
  same => n,Hangup()
```

### Using Asterisk ARI

For real-time integration:

```python
# In sip_integration.py, add WebSocket connection:
async def connect_ari(self):
    uri = f"ws://{self.host}:8088/ari/events?app=ai_service"
    async with websockets.connect(uri) as ws:
        async for message in ws:
            event = json.loads(message)
            if event['type'] == 'StasisStart':
                await self.handle_incoming_call(event)
```

## Working with Recordings

### Location
Recordings are stored in the directory specified by `RECORDINGS_DIR` (default: `./recordings/`)

### Filename Format
- Audio captures: `audio_{call_id}_{timestamp}.wav`
- Voicemails: `voicemail_{call_id}_{timestamp}.wav`

### Managing Recordings

List recordings:
```bash
ls -lh recordings/
```

Play a recording:
```bash
# Using ffplay
ffplay recordings/audio_call_001_20260201_141920.wav

# Using aplay (Linux)
aplay recordings/audio_call_001_20260201_141920.wav
```

Convert format:
```bash
# WAV to MP3
ffmpeg -i recordings/audio_call_001.wav -b:a 192k recordings/audio_call_001.mp3
```

### Cleanup Old Recordings

```bash
# Delete recordings older than 30 days
find recordings/ -name "*.wav" -mtime +30 -delete
```

## Monitoring and Logging

### View Logs

```bash
# If running in terminal
python api.py  # Logs appear in console

# If running as systemd service
sudo journalctl -u ai-call-service -f
```

### Log Levels

Edit logging in your Python files:

```python
# For debug mode
logging.basicConfig(level=logging.DEBUG)

# For production (less verbose)
logging.basicConfig(level=logging.WARNING)
```

### Log File

To log to a file:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai-service.log'),
        logging.StreamHandler()
    ]
)
```

## Advanced Usage

### Multi-Language Support

Enable language detection:

```python
# In stt_service.py, modify transcribe_chunk:
result = self.model.transcribe(audio_path, language=None)  # Auto-detect
# or specify:
result = self.model.transcribe(audio_path, language='es')  # Spanish
```

### Custom TTS

Replace the simulated TTS with a real engine:

```python
# In media_handler.py
async def stream_tts(self, call_id: str, text: str):
    # Option 1: Use Piper TTS
    subprocess.run(['piper', '--output', 'tts.wav'], input=text)
    await self.play_audio(call_id, 'tts.wav')
    
    # Option 2: Use festival
    subprocess.run(['text2wave', '-o', 'tts.wav'], input=text)
    await self.play_audio(call_id, 'tts.wav')
    
    # Option 3: Use cloud TTS (Google, AWS, Azure)
    # Implement cloud API calls here
```

### Webhook Integration

Configure external systems to call the AI service:

```bash
# From Twilio
curl -X POST https://your-server.com:8000/call/incoming \
  -d "call_id=${CallSid}" \
  -d "caller_number=${From}" \
  -d "called_number=${To}"

# From other VoIP providers
# Configure webhook URL to: https://your-server.com:8000/call/incoming
```

## Performance Optimization

### For Low-Latency
1. Use `tiny` or `base` Whisper model
2. Use `mistral` instead of `llama2`
3. Pre-load models at startup
4. Use SSD storage for recordings

### For High Accuracy
1. Use `medium` or `large` Whisper model
2. Use `llama2:13b` or larger Ollama model
3. Increase audio capture duration
4. Fine-tune AI prompts

### For High Volume
1. Run multiple instances behind a load balancer
2. Use Redis for call state management
3. Separate STT and AI workers
4. Use GPU for Whisper if available

## Security Considerations

1. **Authentication**: Add API authentication
2. **Encryption**: Use HTTPS/TLS for API
3. **SIP Security**: Use SIP over TLS (SIPS)
4. **Rate Limiting**: Prevent abuse
5. **Data Privacy**: Encrypt recordings at rest
6. **Access Control**: Restrict who can access recordings

## Troubleshooting Common Issues

### Calls Not Being Routed
- Check Asterisk configuration
- Verify API endpoint is accessible
- Check logs for errors

### Poor Transcription Quality
- Use larger Whisper model
- Increase audio capture duration
- Check audio quality (sample rate, bitrate)

### AI Making Wrong Decisions
- Improve system prompt
- Use larger Ollama model
- Provide more context in prompts
- Train custom model on your data

### High Latency
- Use smaller models
- Optimize hardware (CPU/GPU)
- Reduce audio capture duration
- Cache common responses
