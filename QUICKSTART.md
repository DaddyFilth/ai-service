# Quick Start Guide

Get the AI Call Service running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.8+)
python3 --version

# Check if pip is installed
pip3 --version

# Check if ffmpeg is installed
ffmpeg -version
```

## Installation (3 steps)

### 1. Install Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve &
ollama pull llama2
```

### 2. Setup the Service
```bash
git clone https://github.com/DaddyFilth/ai-service.git
cd ai-service
chmod +x setup.sh
./setup.sh
```

### 3. Configure
```bash
cp .env.example .env
# Edit .env if needed (defaults work for local testing)
```

## Running (1 command)

```bash
source venv/bin/activate
python demo.py
```

You should see the AI service handle sample calls!

## What Just Happened?

The demo simulated:
1. ✓ Incoming call received
2. ✓ Audio transcribed using Whisper
3. ✓ AI analyzed the request
4. ✓ Call routed to appropriate action

## Try the API

Terminal 1 - Start server:
```bash
source venv/bin/activate
python api.py
```

Terminal 2 - Test it:
```bash
# Health check
curl http://localhost:8000/health

# Simulate a call
curl -X POST http://localhost:8000/call/incoming \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "test_001",
    "caller_number": "+1234567890",
    "called_number": "+0987654321"
  }'
```

## Common Issues

**"No module named X"**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**"Cannot connect to Ollama"**
```bash
ollama serve
```

**Port 8000 in use**
```bash
# Edit .env and change SERVICE_PORT to 8001
```

## Next Steps

- Read [USAGE.md](USAGE.md) for detailed features
- Read [INSTALLATION.md](INSTALLATION.md) for production setup
- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- Customize AI prompts in `decision_engine.py`
- Integrate with real Asterisk PBX

## Support

- Check logs for errors
- Run `python verify_structure.py` to verify installation
- See troubleshooting in INSTALLATION.md

---

**That's it! You now have an AI call screening service running locally.**
