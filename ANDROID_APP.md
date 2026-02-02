# Android App - Receive Calls and Connect to AI Service

The Android application receives incoming phone calls on your Android device and forwards them to the AI Call Service for intelligent processing and routing decisions.

## Quick Start

1. **On your computer:**
   ```bash
   cd ai-service
   python api.py
   ```

2. **Build the Android app:**
   ```bash
   cd android-app
   ./gradlew assembleDebug
   ```

3. **Install on your Android device:**
   ```bash
   adb install app/build/outputs/apk/debug/app-debug.apk
   ```

4. **Setup the app:**
   - Open the app on your Android device
   - Enter your computer's IP: `http://192.168.1.100:8000`
   - Test the connection
   - Enable call monitoring
   - Grant required permissions

5. **Receive calls:**
   - Incoming phone calls will be automatically detected
   - Call information is forwarded to the AI service
   - You'll see a notification with the AI's decision
   - View call history to review AI decisions

## Documentation

Full documentation is available in the `android-app/` directory:

- **[android-app/README.md](android-app/README.md)** - Overview and features
- **[android-app/QUICKSTART.md](android-app/QUICKSTART.md)** - Step-by-step setup guide
- **[android-app/BUILD_GUIDE.md](android-app/BUILD_GUIDE.md)** - Detailed build instructions
- **[android-app/ARCHITECTURE.md](android-app/ARCHITECTURE.md)** - Technical architecture
- **[android-app/TROUBLESHOOTING.md](android-app/TROUBLESHOOTING.md)** - Common issues and solutions
- **[android-app/SUMMARY.md](android-app/SUMMARY.md)** - Implementation summary

## Features

- ✅ Detect incoming phone calls on Android device
- ✅ Forward call information to AI service
- ✅ Receive AI-driven routing decisions
- ✅ Display decisions via notifications
- ✅ Maintain call history with AI decisions
- ✅ Test connection to AI service
- ✅ Manual call simulation for testing
- ✅ Material Design UI

## Requirements

- Android 7.0 (API 24) or higher
- Computer and Android device on same WiFi network
- AI Service running on computer
- Java 11+ for building
- Phone call permissions granted on device

## Support

See the [troubleshooting guide](android-app/TROUBLESHOOTING.md) for help with common issues.
