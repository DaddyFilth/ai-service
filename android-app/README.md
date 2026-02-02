# AI Service Android Client

This Android application connects to the AI Call Service and handles incoming phone calls by forwarding them to the AI server for intelligent processing.

## Quick Links

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running fast
- **[Build Guide](BUILD_GUIDE.md)** - Detailed build instructions
- **[Architecture](ARCHITECTURE.md)** - Technical architecture and design
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

## Features

- **Call Monitoring**: Automatically detects incoming phone calls on your Android device
- **AI Processing**: Forwards call information to the AI Service for intelligent decision making
- **Real-time Notifications**: Displays AI decisions (forward, voicemail, ask question) via notifications
- **Call History**: Keeps track of all processed calls with AI decisions
- **Manual Testing**: Simulate calls to test the AI service
- **Connection Management**: Test and monitor connection to the AI server

## How It Works

1. **Incoming Call**: When a phone call comes to your Android device, the app detects it
2. **Forward to AI**: Call information (caller number, timestamp) is sent to the AI service
3. **AI Decision**: The server analyzes the call using AI and makes a routing decision
4. **Notification**: You receive a notification showing what the AI decided
5. **History**: All calls are logged so you can review AI decisions later

## Requirements

- Android device running Android 7.0 (API 24) or higher
- AI Service running on a computer on the same network
- Phone call permissions granted to the app

## Building the APK

### Prerequisites

- JDK 11 or higher
- Android SDK (automatically downloaded by Gradle)

### Build Instructions

#### Quick Verification (Recommended)

Before building, verify your environment:
```bash
cd android-app
./verify-build-env.sh
```

This script checks:
- Java installation (version 11+)
- Gradle wrapper files
- Project structure
- Internet connection
- Disk space

#### Build the APK

1. Navigate to the android-app directory:
   ```bash
   cd android-app
   ```

2. Build the APK:
   ```bash
   ./gradlew assembleDebug
   ```

3. The APK will be generated at:
   ```
   app/build/outputs/apk/debug/app-debug.apk
   ```

### Build Release APK (Signed)

For a release build, you'll need to create a keystore:

```bash
./gradlew assembleRelease
```

## Installation

### Install via ADB

1. Connect your Android device via USB
2. Enable USB debugging on your device
3. Run:
   ```bash
   adb install app/build/outputs/apk/debug/app-debug.apk
   ```

### Install Manually

1. Transfer the APK to your Android device
2. Open the APK file on your device
3. Allow installation from unknown sources if prompted
4. Install the app

## Usage

### Setup

1. **Start the AI Service** on your computer:
   ```bash
   python api.py
   ```

2. **Find your computer's IP address** on the local network:
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig` or `ip addr`

3. **Open the AI Service Client app** on your Android device

4. **Enter the server URL** (e.g., `http://192.168.1.100:8000`)

5. **Test Connection**: Click "Test Connection" to verify connectivity

### Enable Call Monitoring

1. **Test the connection first** to ensure the server is reachable
2. **Click "Enable Call Monitoring"**
3. **Grant permissions** when prompted:
   - Read Phone State (required to detect calls)
   - Read Call Log (required to get call details)
   - Answer Phone Calls (required to process calls)
4. **Monitoring is now active** - incoming calls will be forwarded to the AI service

### View Call History

- Click "View Call History" to see all processed calls
- Each entry shows:
  - Time of call
  - Caller phone number
  - AI decision (forward/voicemail/ask_question)
  - AI message

### Manual Testing

You can still manually simulate calls for testing:
1. Fill in the call details:
   - Call ID (e.g., `test_001`)
   - Caller Number (e.g., `+1234567890`)
   - Called Number (e.g., `+0987654321`)
2. Click "Simulate Call" to send a test request to the service

## Network Configuration

### Firewall Settings

Make sure your computer's firewall allows incoming connections on port 8000:

- **Windows Firewall**: Add an inbound rule for port 8000
- **macOS Firewall**: Allow python/api.py to accept incoming connections
- **Linux (ufw)**: `sudo ufw allow 8000`

### AI Service Configuration

Ensure the AI service is configured to listen on all interfaces:

In `.env` file:
```
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8000
```

## Troubleshooting

### Cannot Connect to Service

1. Verify the AI service is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check if the service is accessible from the network:
   ```bash
   curl http://<computer-ip>:8000/health
   ```

3. Ensure both devices are on the same network

4. Check firewall settings on the computer

### Call Monitoring Not Working

1. **Check Permissions**: Ensure all required permissions are granted
   - Go to Android Settings > Apps > AI Service Client > Permissions
   - Enable Phone and Call Log permissions

2. **Check Monitoring Status**: Ensure monitoring is enabled in the app
   - Look for "Status: ACTIVE" in the Call Monitoring section

3. **Check Server Connection**: Test the connection before enabling monitoring

4. **Check Logs**: Use `adb logcat` to see detailed logs:
   ```bash
   adb logcat | grep -i "CallReceiver\|CallMonitorService"
   ```

### Calls Not Being Forwarded

1. **Verify monitoring is enabled** in the app
2. **Check server URL** is correct and saved
3. **Check network connection** between device and server
4. **Review call history** to see if calls were detected but failed to process

### Connection Timeout

- Increase timeout values if on a slow network
- Ensure the Ollama service is running if the AI service requires it

## API Endpoints Used

- `GET /` - Root endpoint (service info)
- `GET /health` - Health check (verify connection)
- `POST /call/incoming` - Process incoming call and get AI decision
  - Sent automatically when monitoring is enabled
  - Can also be triggered manually for testing

## Permissions Required

The app requires the following permissions:

### Network Permissions (Auto-granted)
- `INTERNET` - Connect to the AI service
- `ACCESS_NETWORK_STATE` - Check network connectivity
- `FOREGROUND_SERVICE` - Run call monitoring in background
- `FOREGROUND_SERVICE_PHONE_CALL` - Handle phone calls

### Runtime Permissions (User must grant)
- `READ_PHONE_STATE` - Detect incoming calls
- `READ_CALL_LOG` - Access call information
- `ANSWER_PHONE_CALLS` - Process incoming calls (Android 8.0+)

**Note**: These permissions are only used when call monitoring is enabled. The app will request them when you click "Enable Call Monitoring".

## Development

The Android app is built with:
- Kotlin
- Retrofit for API calls
- Material Design components
- Coroutines for async operations

### Project Structure

```
android-app/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── java/com/aiservice/client/
│   │       │   ├── MainActivity.kt
│   │       │   ├── ApiClient.kt
│   │       │   ├── AIServiceApi.kt
│   │       │   └── Models.kt
│   │       ├── res/
│   │       │   ├── layout/
│   │       │   ├── values/
│   │       │   └── mipmap-*/
│   │       └── AndroidManifest.xml
│   └── build.gradle
├── build.gradle
├── settings.gradle
└── gradlew
```

## License

Same as the main AI Service project - MIT License
