# Installation Guide

## Prerequisites

Before installing the AI Call Service, ensure you have the following:

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+, Debian 11+, or similar)
- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB (8GB+ recommended for Whisper models)
- **Storage**: 5GB+ free space for models and recordings

### Required Software
1. **Python 3.8+** with pip
2. **FFmpeg** for audio processing
3. **Ollama** for AI decision engine
4. **Asterisk PBX** (optional for production, required for actual call handling)

## Step 1: Install System Dependencies

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

### CentOS/RHEL
```bash
sudo yum install -y python3 python3-pip
```

### macOS
```bash
brew install python
```

## Step 2: Install Ollama

Ollama provides the AI decision engine for call routing.

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve &

# Pull the default model (llama2)
ollama pull llama2

# Optional: Pull other models for better performance
ollama pull mistral  # Faster, good quality
ollama pull llama2:13b  # Higher quality, slower
```

## Step 3: Clone and Setup the AI Service

```bash
# Clone the repository
git clone https://github.com/DaddyFilth/ai-service.git
cd ai-service

# Run the setup script
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Create a Python virtual environment
- Install all Python dependencies
- Create configuration files
- Set up the recordings directory

## Step 4: Configure the Service

Edit the `.env` file with your settings:

```bash
# Copy the example configuration
cp .env.example .env

# Edit with your preferred editor
nano .env
# or
vim .env
```

### Configuration Options

```bash
# Asterisk/SIP Configuration
ASTERISK_HOST=localhost        # Your Asterisk server IP
ASTERISK_PORT=5060            # SIP port
ASTERISK_USERNAME=ai_service  # Asterisk username
ASTERISK_PASSWORD=            # Asterisk password

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434  # Ollama server URL
OLLAMA_MODEL=llama2                 # AI model to use

# Service Configuration
SERVICE_HOST=0.0.0.0          # API server host (0.0.0.0 for all interfaces)
SERVICE_PORT=8000             # API server port
RECORDINGS_DIR=./recordings   # Directory for recordings
MIN_FREE_SPACE_MB=100         # Minimum free disk space for recordings
```

## Step 5: (Optional) Install Asterisk

For production use, you'll need Asterisk PBX:

### Ubuntu/Debian
```bash
sudo apt install -y asterisk asterisk-core-sounds-en asterisk-moh-opsound-wav
```

### From Source (latest version)
```bash
cd /tmp
wget http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-20-current.tar.gz
tar -xzvf asterisk-20-current.tar.gz
cd asterisk-20*/
./configure
make
sudo make install
sudo make samples
sudo make config
```

### Configure Asterisk for the AI Service
```bash
# Edit /etc/asterisk/ari.conf
[general]
enabled = yes

[ai_service]
type = user
read_only = no
password = CHANGE_ME_TO_STRONG_PASSWORD

# Edit /etc/asterisk/http.conf
[general]
enabled = yes
bindaddr = 0.0.0.0
bindport = 8088

# Restart Asterisk
sudo systemctl restart asterisk
```

## Step 6: Verify Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Verify all components
python3 verify_structure.py
```

You should see:
```
✓ ALL COMPONENTS HAVE VALID STRUCTURE
```

## Step 7: Run the Service

### Option A: Standalone Mode (for testing)
```bash
source venv/bin/activate
python main.py
```

### Option B: API Server Mode (recommended)
```bash
source venv/bin/activate
python api.py
```

Or using uvicorn directly:
```bash
source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Option C: Production Mode with systemd
Create `/etc/systemd/system/ai-call-service.service`:

```ini
[Unit]
Description=AI Call Service
After=network.target asterisk.service ollama.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/ai-service
Environment="PATH=/path/to/ai-service/venv/bin"
ExecStart=/path/to/ai-service/venv/bin/python api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-call-service
sudo systemctl start ai-call-service
sudo systemctl status ai-call-service
```

## Testing the Installation

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

Expected output:
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

### Test 2: Simulate a Call
```bash
curl -X POST http://localhost:8000/call/incoming \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "test_001",
    "caller_number": "+1234567890",
    "called_number": "+0987654321"
  }'
```

### Test 3: Run Demo
```bash
source venv/bin/activate
python demo.py
```

## Troubleshooting

### Issue: "No module named 'whisper'"
```bash
source venv/bin/activate
pip install openai-whisper torch torchaudio
```

### Issue: "Cannot connect to Ollama"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve
```

### Issue: "Permission denied on recordings directory"
```bash
mkdir -p recordings
chmod 755 recordings
```

### Issue: "Port 8000 already in use"
Edit `.env` and change `SERVICE_PORT` to another port (e.g., 8001)

## Next Steps

After installation:
1. Configure Asterisk dialplan to route calls to the AI service
2. Set up SIP trunks for incoming calls
3. Customize the AI prompts in `decision_engine.py`
4. Set up monitoring and logging
5. Configure backup and retention policies for recordings

## Upgrading

To upgrade to the latest version:

```bash
cd ai-service
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

## Uninstallation

```bash
# Stop the service
sudo systemctl stop ai-call-service
sudo systemctl disable ai-call-service

# Remove service file
sudo rm /etc/systemd/system/ai-call-service.service

# Remove application
cd ~
rm -rf ai-service
```
