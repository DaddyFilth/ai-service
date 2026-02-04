#!/bin/bash

# Setup script for AI Call Service

GENERATE_ASTERISK_CONFIGS=true
SKIP_OLLAMA=false
DEFAULT_OLLAMA_MODEL="llama2"
OLLAMA_STARTUP_RETRIES=10

for arg in "$@"; do
    case "$arg" in
        --skip-asterisk)
            GENERATE_ASTERISK_CONFIGS=false
            ;;
        --skip-ollama)
            SKIP_OLLAMA=true
            ;;
        *)
            ;;
    esac
done

# Generate a secure hex password.
generate_password() {
    python3 - <<'PY'
import secrets
print(secrets.token_hex(24))
PY
}

# Ensure a key exists in the .env file.
ensure_env_value() {
    local key="$1"
    local value="$2"
    local file="$3"

    python3 - "$key" "$value" "$file" <<'PY'
import sys
from pathlib import Path

key, value, path = sys.argv[1:4]
env_file = Path(path)
lines = env_file.read_text().splitlines() if env_file.exists() else []
updated = False
new_lines = []

for line in lines:
    if line.startswith(f"{key}="):
        new_lines.append(f"{key}={value}")
        updated = True
    else:
        new_lines.append(line)

if not updated:
    new_lines.append(f"{key}={value}")

env_file.write_text("\n".join(new_lines) + "\n")
PY
}

# Get a key value from a .env file.
get_env_value() {
    local key="$1"
    local file="$2"

    python3 - "$key" "$file" <<'PY'
import sys
from pathlib import Path

key, path = sys.argv[1:3]
value = ""
env_file = Path(path)
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if line.startswith(f"{key}="):
            value = line.split("=", 1)[1].rstrip("\r\n")
            break
print(value)
PY
}

echo "=== AI Call Service Setup ==="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "Error: Python 3 is required"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Warning: Some dependencies may have failed to install"
    echo "You may need to install system dependencies first"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
fi

if [ -f .env ]; then
    if ! chmod 600 .env 2>/dev/null; then
        echo "Error: Unable to set permissions on .env; ensure it is readable only by your user."
        exit 1
    fi
    set -a
    . ./.env
    set +a
fi

existing_password=$(get_env_value "ASTERISK_PASSWORD" ".env")
if [ -z "$existing_password" ]; then
    generated_password=$(generate_password)
    ensure_env_value "ASTERISK_PASSWORD" "$generated_password" ".env"
    echo "Generated secure ASTERISK_PASSWORD and saved to .env"
fi

# Create recordings directory
echo ""
echo "Creating recordings directory..."
mkdir -p recordings

# Check for Ollama
echo ""
echo "Checking for Ollama..."
if [ "$SKIP_OLLAMA" = true ]; then
    echo "Skipping Ollama setup (--skip-ollama)"
elif command -v ollama &> /dev/null; then
    echo "Ollama is installed"
    OLLAMA_HEALTH_URL="${OLLAMA_HOST:-http://localhost:11434}/api/tags"
    if ! curl -fsS "$OLLAMA_HEALTH_URL" &> /dev/null; then
        echo "Starting Ollama service..."
        OLLAMA_LOG_DIR="./logs"
        OLLAMA_LOG_FILE="${OLLAMA_LOG_DIR}/ollama.log"
        mkdir -p "$OLLAMA_LOG_DIR"
        if ! chmod 700 "$OLLAMA_LOG_DIR" 2>/dev/null; then
            echo "Warning: Unable to set permissions on ${OLLAMA_LOG_DIR}; writing Ollama logs to /dev/null."
            OLLAMA_LOG_FILE="/dev/null"
        fi
        nohup ollama serve > "$OLLAMA_LOG_FILE" 2>&1 &
        service_ready=false
        for ((i=1; i<=OLLAMA_STARTUP_RETRIES; i++)); do
            if curl -fsS "$OLLAMA_HEALTH_URL" &> /dev/null; then
                service_ready=true
                break
            fi
            sleep 1
        done
        if [ "$service_ready" = false ]; then
            echo "Warning: Ollama did not become available after ${OLLAMA_STARTUP_RETRIES} attempts; verify the service is running."
            echo "Check logs at: ${OLLAMA_LOG_FILE}"
        fi
    fi
    OLLAMA_MODEL_TO_PULL="${OLLAMA_MODEL:-$DEFAULT_OLLAMA_MODEL}"
    echo "Pulling model (${OLLAMA_MODEL_TO_PULL})..."
    if ! ollama pull "$OLLAMA_MODEL_TO_PULL"; then
        echo "Warning: Failed to pull model ${OLLAMA_MODEL_TO_PULL}; ensure Ollama is running and the model name is valid."
    fi
else
    echo "Warning: Ollama is not installed"
    echo "Install Ollama from: https://ollama.ai"
fi

echo ""
echo "=== Setup Complete ==="
echo ""

if [ "$GENERATE_ASTERISK_CONFIGS" = true ]; then
    echo ""
    if [ -f "asterisk_config_generator.py" ]; then
        echo "Generating Asterisk configuration files..."
        python asterisk_config_generator.py -o ./asterisk-configs
        echo ""
        echo "Asterisk configurations generated in ./asterisk-configs/"
        echo "See ./asterisk-configs/README.md for installation instructions"
    else
        echo "Error: asterisk_config_generator.py not found"
        echo "Please ensure all repository files are present"
    fi
else
    echo "Skipping Asterisk configuration generation (--skip-asterisk)"
fi

echo ""
echo "Next steps:"
echo "1. Your configuration is ready in .env (includes generated ASTERISK_PASSWORD)"
echo "2. Ensure Ollama is running: ollama serve"
if [ "$GENERATE_ASTERISK_CONFIGS" = true ]; then
    echo "3. Install Asterisk configs: cd asterisk-configs && sudo bash install_configs.sh"
    echo "4. Run the service: python main.py"
    echo "   or as API: python api.py"
else
    echo "3. (Optional) Generate Asterisk configs: python asterisk_config_generator.py"
    echo "4. Run the service: python main.py"
    echo "   or as API: python api.py"
fi
echo ""
echo "To activate the virtual environment later, run:"
echo "  source venv/bin/activate"
