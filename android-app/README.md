# AI Service Android Client

This Android application connects to the AI Call Service running on your computer and allows you to simulate calls and test the service.

## Features

- Connect to AI Service API running on a computer
- Test connection health check
- Simulate incoming calls
- View AI service responses

## Requirements

- Android device or emulator running Android 7.0 (API 24) or higher
- AI Service running on a computer on the same network

## Building the APK

### Prerequisites

- JDK 11 or higher
- Android SDK (automatically downloaded by Gradle)

### Build Instructions

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

1. Start the AI Service on your computer:
   ```bash
   python api.py
   ```

2. Find your computer's IP address on the local network:
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig` or `ip addr`

3. Open the AI Service Client app on your Android device

4. Enter the server URL (e.g., `http://192.168.1.100:8000`)

5. Click "Test Connection" to verify connectivity

6. Fill in the call details:
   - Call ID (e.g., `test_001`)
   - Caller Number (e.g., `+1234567890`)
   - Called Number (e.g., `+0987654321`)

7. Click "Simulate Call" to send a call request to the service

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

### Connection Timeout

- Increase timeout values if on a slow network
- Ensure the Ollama service is running if the AI service requires it

## API Endpoints Used

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /call/incoming` - Simulate incoming call

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
